"""文件存储工具：支持本地存储和S3兼容对象存储"""
import os
import aiofiles
from pathlib import Path
from typing import Optional, BinaryIO
from urllib.parse import urljoin

from app.config import settings


class LocalStorage:
    """本地文件存储"""

    async def save(self, file_path: str, content: bytes) -> str:
        """保存文件，返回相对路径"""
        abs_path = os.path.join(settings.UPLOAD_DIR, file_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        async with aiofiles.open(abs_path, 'wb') as f:
            await f.write(content)
        return file_path

    async def delete(self, file_path: str) -> None:
        """删除文件"""
        abs_path = os.path.join(settings.UPLOAD_DIR, file_path)
        if os.path.exists(abs_path):
            os.remove(abs_path)

    def get_url(self, file_path: str) -> str:
        """获取文件访问URL"""
        return f"/api/uploads/{file_path}"

    async def read(self, file_path: str) -> Optional[bytes]:
        """读取文件内容"""
        abs_path = os.path.join(settings.UPLOAD_DIR, file_path)
        if not os.path.exists(abs_path):
            return None
        async with aiofiles.open(abs_path, 'rb') as f:
            return await f.read()


class S3Storage:
    """S3兼容对象存储（阿里OSS、腾讯COS、MinIO等）"""

    def __init__(self):
        self._client = None
        self._bucket = settings.S3_BUCKET

    async def _get_client(self):
        if self._client is None:
            import boto3
            self._client = boto3.client(
                's3',
                endpoint_url=settings.S3_ENDPOINT,
                region_name=settings.S3_REGION or 'auto',
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
            )
        return self._client

    async def save(self, file_path: str, content: bytes) -> str:
        client = await self._get_client()
        client.put_object(Bucket=self._bucket, Key=file_path, Body=content)
        return file_path

    async def delete(self, file_path: str) -> None:
        client = await self._get_client()
        client.delete_object(Bucket=self._bucket, Key=file_path)

    def get_url(self, file_path: str) -> str:
        if settings.S3_PUBLIC_URL:
            return urljoin(settings.S3_PUBLIC_URL.rstrip('/') + '/', file_path)
        return f"/api/uploads/{file_path}"

    async def read(self, file_path: str) -> Optional[bytes]:
        client = await self._get_client()
        try:
            obj = client.get_object(Bucket=self._bucket, Key=file_path)
            return obj['Body'].read()
        except Exception:
            return None


def get_storage() -> LocalStorage | S3Storage:
    """获取当前存储引擎实例"""
    if settings.STORAGE_MODE == "s3" and settings.S3_ENDPOINT:
        return S3Storage()
    return LocalStorage()


# 文件类型分类
FILE_TYPE_DIRS = {
    'image': 'images',
    'video': 'videos',
    'document': 'documents',
    'html': 'html',
    'other': 'other',
}

ALLOWED_EXTENSIONS = {
    'image': {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'ico'},
    'video': {'mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'webm'},
    'document': {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'md', 'csv'},
    'html': {'html', 'htm'},
    'other': {'zip', 'rar', '7z', 'json', 'xml', 'yaml', 'yml'},
}

# 文件类型检测（按扩展名）
EXTENSION_TYPE_MAP = {}
for ftype, exts in ALLOWED_EXTENSIONS.items():
    for ext in exts:
        EXTENSION_TYPE_MAP[ext] = ftype


def get_file_type(filename: str) -> str:
    """根据文件名获取文件类型"""
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return EXTENSION_TYPE_MAP.get(ext, 'other')


def generate_file_path(filename: str, subdir: str = '') -> str:
    """生成存储路径: {type}/{subdir}/{date_hash}_{filename}"""
    import hashlib
    import time
    file_type = get_file_type(filename)
    dir_name = FILE_TYPE_DIRS.get(file_type, 'other')
    if subdir:
        dir_name = f"{dir_name}/{subdir}"
    timestamp = str(int(time.time() * 1000))
    hash_suffix = hashlib.md5(timestamp.encode()).hexdigest()[:8]
    name, ext = os.path.splitext(filename)
    safe_name = f"{name}_{hash_suffix}{ext}"
    return f"{dir_name}/{safe_name}"
