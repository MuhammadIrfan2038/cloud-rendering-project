from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from pathlib import Path
from dotenv import load_dotenv
from app.services.blender import render_blend_file_with_settings, initialize_render_progress
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import RenderMetadata, RenderProgress
from threading import Thread
from datetime import datetime
import os, shutil
import uuid

load_dotenv()
router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
TEMP_ZIP_DIR = BASE_DIR / "temp_zip"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")

@router.post("/render")
async def upload_and_render(file: UploadFile = File(...)):
    if not file.filename.endswith(".blend"):
        raise HTTPException(status_code=400, detail="File must be a .blend file")

    # Simpan file
    Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    file_path = Path(UPLOAD_DIR) / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Buat nama project unik
    project_name = f"{Path(file.filename).stem}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:5]}"

    # Inisialisasi progres di database
    db = SessionLocal()
    initialize_render_progress(db, project_name=project_name, total_frames=0)
    db.close()

    # Mulai proses render di thread background
    def start_render():
        render_blend_file_with_settings(str(file_path), project_name=project_name)

    Thread(target=start_render).start()

    return {
        "message": "File berhasil diunggah dan rendering telah dimulai.",
        "project_name": project_name
    }

@router.get("/render-history")
def get_render_history(db: Session = Depends(get_db)):
    renders = db.query(RenderMetadata).order_by(RenderMetadata.rendered_at.desc()).all()
    return [
        {
            "id": r.id,
            "filename": r.filename,
            "frame_start": r.frame_start,
            "frame_end": r.frame_end,
            "output_format": r.output_format,
            "output_dir": r.output_dir,
            "status": r.status,
            "rendered_at": r.rendered_at.isoformat()
        }
        for r in renders
    ]

@router.get("/render/progress/{project_name}")
def get_render_progress(project_name: str, db: Session = Depends(get_db)):
    progress = db.query(RenderProgress).filter_by(project_name=project_name).first()
    if not progress:
        raise HTTPException(status_code=404, detail="Progress tidak ditemukan.")
    
    return {
        "project_name": progress.project_name,
        "total_frames": progress.total_frames,
        "rendered_frames": progress.rendered_frames,
        "current_frame": progress.current_frame,
        "status": progress.status
    }

@router.get("/download/{project_name}")
def download_render_result(project_name: str):
    db = SessionLocal()
    metadata = db.query(RenderMetadata).filter(RenderMetadata.output_dir.contains(project_name)).first()
    if not metadata:
        db.close()
        raise HTTPException(status_code=404, detail="Metadata render tidak ditemukan.")

    output_dir = Path(metadata.output_dir)
    blend_filename = Path(metadata.filename).stem
    zip_path = BASE_DIR / "render_output" / f"{blend_filename}.zip"

    if not zip_path.exists():
        db.close()
        raise HTTPException(status_code=404, detail="File ZIP tidak ditemukan.")

    db.close()
    return FileResponse(
        path=zip_path,
        filename=zip_path.name,
        media_type="application/zip"
    )

@router.post("/cleanup_zip")
def cleanup_zip():
    render_output_dir = BASE_DIR / "render_output"
    print(f"[DEBUG] Mencari ZIP di: {render_output_dir.resolve()}")

    if not render_output_dir.exists():
        return {"message": "Folder render_output tidak ditemukan."}

    deleted = []
    for zip_file in render_output_dir.glob("*.zip"):
        try:
            zip_file.unlink()
            deleted.append(zip_file.name)
        except Exception as e:
            return {"error": f"Gagal menghapus {zip_file.name}: {str(e)}"}

    return {"message": f"ZIP terhapus: {deleted}"}
