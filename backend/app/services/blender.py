from pathlib import Path
from datetime import datetime
from app.database import SessionLocal
from app.models import RenderMetadata, RenderResult, RenderProgress
from sqlalchemy.orm import Session
import subprocess
import re
import os
import zipfile
import shutil

# BASE_DIR menunjuk ke folder backend/
BASE_DIR = Path(__file__).resolve().parent.parent

def initialize_render_progress(db: Session, project_name: str, total_frames: int):
    progress = RenderProgress(
        project_name=project_name,
        total_frames=total_frames,
        rendered_frames=0,
        status="in_progress"
    )
    db.add(progress)
    db.commit()

def update_render_progress(db: Session, project_name: str, current_frame: int):
    progress = db.query(RenderProgress).filter_by(project_name=project_name).first()
    if progress:
        progress.rendered_frames += 1
        progress.current_frame = current_frame
        db.commit()

def complete_render_progress(db: Session, project_name: str):
    progress = db.query(RenderProgress).filter_by(project_name=project_name).first()
    if progress:
        progress.status = "done"
        db.commit()

def render_blend_file_with_settings(blend_file_path: str, project_name: str):
    blend_file_path = Path(blend_file_path)

    # Buat folder output berdasarkan nama project (agar konsisten)
    output_dir = BASE_DIR / "render_output" / project_name
    output_dir.mkdir(parents=True, exist_ok=True)

    # Path script Blender internal
    script_path = Path("scripts/render_from_settings.py").resolve()

    # Setup koneksi DB
    db = SessionLocal()

    # Jalankan Blender dengan subprocess
    process = subprocess.Popen(
        [
            "blender",
            "--background",
            "--factory-startup",
            str(blend_file_path),
            "--python", str(script_path),
            "--",
            str(output_dir.resolve())
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    frame_start, frame_end = None, None
    seen_frames = set()
    lines = []

    try:
        for line in process.stdout:
            print(line.strip())
            lines.append(line)

            # Deteksi frame awal
            if frame_start is None and "Start Frame" in line:
                match = re.search(r"(\d+)", line)
                if match:
                    frame_start = int(match.group(1))

            # Deteksi frame akhir
            if frame_end is None and "End Frame" in line:
                match = re.search(r"(\d+)", line)
                if match:
                    frame_end = int(match.group(1))

            # Deteksi rendering frame: Fra:5
            match = re.search(r"Fra:\s*(\d+)", line)
            if match:
                frame_num = int(match.group(1))
                if frame_num not in seen_frames:
                    seen_frames.add(frame_num)
                    update_render_progress(db, project_name, current_frame=frame_num)

        process.wait()
        
        # Setelah selesai membaca seluruh output
        if frame_start is None or frame_end is None:
            frame_numbers = [int(m.group(1)) for l in lines for m in re.finditer(r"Fra:\s*(\d+)", l)]
            if frame_numbers:
                frame_start = min(frame_numbers)
                frame_end = max(frame_numbers)

        # ✅ Sekarang set total_frames SEKALI dengan nilai fix
        if frame_start is not None and frame_end is not None:
            total_frames_actual = frame_end - frame_start + 1
            progress = db.query(RenderProgress).filter_by(project_name=project_name).first()
            if progress:
                progress.total_frames = total_frames_actual
                db.commit()
                print(f"[DEBUG] total_frames akhir: {total_frames_actual}")

        if process.returncode != 0:
            db.close()
            return False, f"Render process failed with exit code {process.returncode}"

        # Tandai render selesai
        complete_render_progress(db, project_name)

        # Cari semua file hasil render
        supported_formats = ["*.png", "*.jpg", "*.jpeg", "*.tiff", "*.bmp", "*.exr"]
        rendered_files = []
        for ext in supported_formats:
            rendered_files.extend(output_dir.glob(ext))

        if not rendered_files:
            db.close()
            return False, "Render selesai tapi file tidak ditemukan."

        output_format = rendered_files[0].suffix.replace(".", "").upper()

        # Simpan metadata render
        metadata = RenderMetadata(
            filename=blend_file_path.name,
            frame_start=frame_start or 0,
            frame_end=frame_end or 0,
            output_format=output_format,
            output_dir=str(output_dir),
            status="done",
            rendered_at=datetime.utcnow(),
        )
        db.add(metadata)
        db.commit()

        # Simpan hasil pertama ke RenderResult
        first_output = rendered_files[0]
        try:
            relative_path = str(first_output.relative_to(BASE_DIR))
        except ValueError:
            relative_path = f"render_output/{project_name}/{first_output.name}"

        result_row = RenderResult(
            filename=blend_file_path.name,
            output_path=relative_path
        )
        db.add(result_row)
        db.commit()
        db.close()

        zip_name = blend_file_path.stem + ".zip"
        zip_path = BASE_DIR / "render_output" / zip_name

        if not zip_path.exists():
            with zipfile.ZipFile(zip_path, "w") as zipf:
                for file in rendered_files:
                    zipf.write(file, arcname=file.name)
            print(f"[DEBUG] ZIP berhasil dibuat: {zip_path}")
        else:
            print(f"[DEBUG] ZIP sudah ada: {zip_path}")

        # Setelah ZIP berhasil dibuat, hapus folder render_output/<project_name>
        try:
            shutil.rmtree(output_dir)
            print(f"[DEBUG] Folder hasil render dihapus: {output_dir}")
        except Exception as e:
            print(f"[WARNING] Gagal menghapus folder hasil render: {e}")

        db.close()
        return True, {
            "output_path": str(zip_path),
            "project_name": project_name
        }

    except Exception as e:
        db.close()
        return False, f"Render error: {str(e)}"
