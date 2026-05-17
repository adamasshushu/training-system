"""培训管理系统配置"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "培训管理系统"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True

    # 数据库
    DATABASE_URL: str = "sqlite+aiosqlite:///./training.db"

    # JWT
    SECRET_KEY: str = "training-system-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24小时

    # 文件存储（本地模式）
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024  # 500MB

    # ===== 对象存储（可选） =====
    STORAGE_MODE: str = "local"  # "local" 或 "s3"
    S3_ENDPOINT: Optional[str] = None
    S3_REGION: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_BUCKET: Optional[str] = None
    S3_PUBLIC_URL: Optional[str] = None

    class Config:
        env_file = ".env"


settings = Settings()
