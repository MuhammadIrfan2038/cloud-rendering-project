from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base
from datetime import datetime

class RenderMetadata(Base):
    __tablename__ = "render_metadata"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255))
    frame_start = Column(Integer)
    frame_end = Column(Integer)
    output_format = Column(String(50))
    output_dir = Column(String(255))
    status = Column(String(50))
    rendered_at = Column(DateTime, default=datetime.utcnow)

class RenderResult(Base):
    __tablename__ = "render_result"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255))
    output_path = Column(String(255))

class RenderProgress(Base):
    __tablename__ = "render_progress"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(255), unique=True, index=True)
    total_frames = Column(Integer)
    rendered_frames = Column(Integer, default=0)
    current_frame = Column(Integer, default=0)
    status = Column(String(50), default="in_progress")  # or: done, error
