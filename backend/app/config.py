"""培训管理系统配置 — 生产环境"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "培训管理系统"
    APP_VERSION: str = "2.2.0"
    DEBUG: bool = False

    # ===== 数据库 =====
    # 生产环境推荐 PostgreSQL: postgresql+asyncpg://user:pass@host/dbname
    # 当前使用 SQLite WAL 模式（高性能 + 并发安全）
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./training_prod.db"
    )

    # ===== JWT =====
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production-use-env-var")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    # ===== 文件存储 =====
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", str(500 * 1024 * 1024)))

    # ===== 对象存储（可选） =====
    STORAGE_MODE: str = os.getenv("STORAGE_MODE", "local")
    S3_ENDPOINT: Optional[str] = os.getenv("S3_ENDPOINT")
    S3_REGION: Optional[str] = os.getenv("S3_REGION")
    S3_ACCESS_KEY: Optional[str] = os.getenv("S3_ACCESS_KEY")
    S3_SECRET_KEY: Optional[str] = os.getenv("S3_SECRET_KEY")
    S3_BUCKET: Optional[str] = os.getenv("S3_BUCKET")
    S3_PUBLIC_URL: Optional[str] = os.getenv("S3_PUBLIC_URL")

    class Config:
        env_file = ".env"


settings = Settings()
