"""文件上传/下载/管理路由"""
import os
import uuid
import mimetypes
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.file import FileRecord
from app.utils.auth import get_current_user
from app.utils.storage import get_storage, generate_file_path, get_file_type

router = APIRouter(prefix="/api/uploads", tags=["文件上传"])


@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    subdir: Optional[str] = Form(None, description="子目录（可选）"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """上传文件（图片/视频/文档/PDF等）"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    # 读取文件内容
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="文件内容为空")

    # 检查文件大小（配置文件限制500MB）
    max_size = 500 * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(status_code=413, detail=f"文件大小超过限制({max_size // (1024*1024)}MB)")

    # 生成存储路径
    file_path = generate_file_path(file.filename, subdir or '')
    file_type = get_file_type(file.filename)
    mime_type = file.content_type or mimetypes.guess_type(file.filename)[0] or 'application/octet-stream'

    # 保存文件
    storage = get_storage()
    await storage.save(file_path, content)

    # 记录到数据库
    record = FileRecord(
        filename=file.filename,
        file_path=file_path,
        file_size=len(content),
        file_type=file_type,
        mime_type=mime_type,
        uploaded_by=current_user.get("id"),
    )
    db.add(record)
    await db.flush()

    return {
        "ID": record.id,
        "文件名": file.filename,
        "文件地址": storage.get_url(file_path),
        "文件类型": file_type,
        "文件大小": len(content),
        "存储路径": file_path,
        "labels": {
            "ID": "id",
            "文件名": "filename",
            "文件地址": "url",
            "文件类型": "file_type",
            "文件大小": "file_size",
            "存储路径": "file_path",
        }
    }


@router.get("")
async def list_files(
    file_type: Optional[str] = Query(None, alias="file_type"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """文件列表"""
    query = select(FileRecord).order_by(FileRecord.id.desc())
    if file_type:
        query = query.where(FileRecord.file_type == file_type)

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
            "文件类型": r.file_type,
            "文件大小": r.file_size,
            "创建时间": str(r.created_at) if r.created_at else None,
        })

    return {
        "数据": records,
        "共计": total,
        "页码": page,
        "每页数量": page_size,
        "labels": {"数据": "data", "共计": "total", "页码": "page", "每页数量": "page_size"}
    }


@router.get("/{file_path:path}")
async def serve_file(file_path: str):
    """提供文件访问（图片、视频直接预览，文档下载）"""
    storage = get_storage()
    content = await storage.read(file_path)
    if content is None:
        raise HTTPException(status_code=404, detail="文件不存在")

    # 猜测MIME类型
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = 'application/octet-stream'

    return Response(content=content, media_type=mime_type)


@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """删除文件"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可删除文件")

    result = await db.execute(select(FileRecord).where(FileRecord.id == file_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="文件不存在")

    # 删除物理文件
    storage = get_storage()
    await storage.delete(record.file_path)

    # 删除数据库记录
    await db.delete(record)
    await db.flush()

    return {"message": "文件已删除", "labels": {"message": "消息"}}
