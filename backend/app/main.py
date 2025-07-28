from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import zipfile
from pathlib import Path
from app.routers import render
from app.database import SessionLocal
from app.models import RenderMetadata
import io

app = FastAPI(
    title="Cloud-Based Blender Render API",
    description="API untuk rendering file Blender dan melihat riwayat hasil render.",
    version="1.0"
)

# 📁 Path ke folder project
BASE_DIR = Path(__file__).resolve().parent.parent
RENDER_OUTPUT_PATH = BASE_DIR / "render_output"

# 🌐 Akses static file output (gambar/zip) melalui URL
app.mount("/render_output", StaticFiles(directory=str(RENDER_OUTPUT_PATH)), name="render_output")

# 🔗 Daftarkan router untuk endpoint render
app.include_router(render.router)

# 🌍 CORS Middleware (agar frontend Next.js bisa akses)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # boleh dibatasi ke http://localhost:3000 jika perlu
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/download-zip/{render_id}")
def download_zip(render_id: int):
    db = SessionLocal()
    metadata = db.query(RenderMetadata).filter(RenderMetadata.id == render_id).first()
    db.close()

    if not metadata:
        raise HTTPException(status_code=404, detail="Render ID tidak ditemukan.")

    folder_path = Path(metadata.output_dir)
    if not folder_path.exists() or not folder_path.is_dir():
        raise HTTPException(status_code=404, detail="Folder hasil render tidak ditemukan.")

    # Kompres folder ke zip dalam memori
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file in folder_path.rglob("*"):
            zip_file.write(file, arcname=file.relative_to(folder_path))
    zip_buffer.seek(0)

    # 💡 Gunakan nama file .blend sebagai nama zip
    blend_name = Path(metadata.filename).stem
    zip_filename = f"render_result_{blend_name}.zip"

    return StreamingResponse(zip_buffer, media_type="application/zip", headers={
        "Content-Disposition": f"attachment; filename={zip_filename}"
    })

