"""文件记录模型"""
from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func
from app.database import Base


class FileRecord(Base):
    """上传文件记录"""
    __tablename__ = "file_records"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, comment="原始文件名")
    file_path = Column(String(500), nullable=False, comment="存储路径")
    file_size = Column(Float, default=0, comment="文件大小(字节)")
    file_type = Column(String(20), nullable=False, comment="文件类型(image/video/document/html/other)")
    mime_type = Column(String(100), nullable=True, comment="MIME类型")
    uploaded_by = Column(Integer, nullable=True, comment="上传用户ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
