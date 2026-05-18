"""视频管理路由：上传/列表/流媒体/删除"""
import os
import uuid
import mimetypes
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database import get_db
from app.models.file import FileRecord
from app.utils.auth import get_current_user
from app.utils.storage import get_storage
from app.config import settings

router = APIRouter(prefix="/api/videos", tags=["视频管理"])

# 视频文件存储目录
VIDEO_DIR = "videos"

# 允许的视频格式
VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'webm', 'm4v'}


@router.post("")
async def upload_video(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None, description="视频标题"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """上传视频文件"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    # 检查扩展名
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的视频格式: {ext}，支持的格式: {', '.join(VIDEO_EXTENSIONS)}"
        )

    # 读取文件内容
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="文件内容为空")

    # 检查文件大小（配置文件限制500MB）
    max_size = settings.MAX_UPLOAD_SIZE
    if len(content) > max_size:
        raise HTTPException(status_code=413, detail=f"文件大小超过限制({max_size // (1024*1024)}MB)")

    # 生成唯一文件名
    name, ext = os.path.splitext(file.filename)
    unique_name = f"{uuid.uuid4().hex[:16]}_{name[:48]}{ext}"
    file_path = f"{VIDEO_DIR}/{unique_name}"

    # 保存文件
    storage = get_storage()
    await storage.save(file_path, content)

    # 视频标题
    video_title = title or file.filename

    # 记录到数据库
    record = FileRecord(
        filename=video_title,
        file_path=file_path,
        file_size=len(content),
        file_type="video",
        mime_type=file.content_type or mimetypes.guess_type(file.filename)[0] or 'video/mp4',
        uploaded_by=current_user.get("id"),
    )
    db.add(record)
    await db.flush()

    return {
        "ID": record.id,
        "文件名": video_title,
        "原始文件名": file.filename,
        "文件地址": storage.get_url(file_path),
        "文件大小": len(content),
        "存储路径": file_path,
        "创建时间": str(record.created_at) if record.created_at else None,
        "labels": {
            "ID": "id",
            "文件名": "title",
            "原始文件名": "original_filename",
            "文件地址": "url",
            "文件大小": "file_size",
            "存储路径": "file_path",
            "创建时间": "created_at",
        }
    }


@router.get("")
async def list_videos(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """视频列表（支持搜索和分页）"""
    query = select(FileRecord).where(FileRecord.file_type == "video").order_by(desc(FileRecord.id))

    if keyword:
        query = query.where(FileRecord.filename.ilike(f"%{keyword}%"))

    result = await db.execute(query)
    all_records = result.scalars().all()
    total = len(all_records)
    start = (page - 1) * page_size
    page_records = all_records[start:start + page_size]

    storage = get_storage()
    records = []
    for r in page_records:
        records.append({
            "ID": r.id,
            "文件名": r.filename,
            "文件地址": storage.get_url(r.file_path),
            "文件大小": r.file_size,
            "文件类型": r.file_type,
            "存储路径": r.file_path,
            "创建时间": str(r.created_at) if r.created_at else None,
        })

    return {
        "数据": records,
        "共计": total,
        "页码": page,
        "每页数量": page_size,
        "labels": {"数据": "data", "共计": "total", "页码": "page", "每页数量": "page_size"}
    }


@router.get("/{video_id}")
async def get_video(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取单个视频详细信息"""
    result = await db.execute(
        select(FileRecord).where(FileRecord.id == video_id, FileRecord.file_type == "video")
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="视频不存在")

    storage = get_storage()
    return {
        "ID": record.id,
        "文件名": record.filename,
        "文件地址": storage.get_url(record.file_path),
        "文件大小": record.file_size,
        "存储路径": record.file_path,
        "创建时间": str(record.created_at) if record.created_at else None,
        "labels": {
            "ID": "id",
            "文件名": "title",
            "文件地址": "url",
            "文件大小": "file_size",
            "存储路径": "file_path",
            "创建时间": "created_at",
        }
    }


@router.delete("/{video_id}")
async def delete_video(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """删除视频"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可删除视频")

    result = await db.execute(
        select(FileRecord).where(FileRecord.id == video_id, FileRecord.file_type == "video")
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="视频不存在")

    # 删除物理文件
    storage = get_storage()
    await storage.delete(record.file_path)

    # 删除数据库记录
    await db.delete(record)
    await db.flush()

    return {"message": "视频已删除", "labels": {"message": "消息"}}


@router.get("/stream/{video_id:int}")
async def stream_video(video_id: int, db: AsyncSession = Depends(get_db)):
    """流式播放视频（支持范围请求实现进度条拖拽）"""
    from sqlalchemy import select
    result = await db.execute(
        select(FileRecord).where(FileRecord.id == video_id, FileRecord.file_type == "video")
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="视频不存在")

    abs_path = os.path.join(settings.UPLOAD_DIR, record.file_path)
    if not os.path.exists(abs_path):
        raise HTTPException(status_code=404, detail="视频文件不存在")

    from starlette.responses import FileResponse
    return FileResponse(
        path=abs_path,
        media_type=record.mime_type or "video/mp4",
        filename=record.filename or os.path.basename(record.file_path),
        headers={"Accept-Ranges": "bytes"},
    )
