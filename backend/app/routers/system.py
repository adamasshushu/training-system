"""系统设置路由：品牌定制、对象存储配置等"""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from typing import Optional, Any
from app.database import get_db
from app.models.system_settings import SystemSetting
from app.utils.auth import get_current_user
from app.config import settings

router = APIRouter(prefix="/api/system", tags=["系统设置"])


# ========== Pydantic模型 ==========

class SystemSettingUpdate(BaseModel):
    """更新系统设置"""
    value: Any = Field(..., description="设置值（字符串或JSON对象）")
    说明: Optional[str] = Field(None, alias="description")

    class Config:
        populate_by_name = True


class ObjectStorageConfig(BaseModel):
    """对象存储配置"""
    存储模式: str = Field("local", alias="storage_mode", pattern="^(local|s3)$")
    S3地址: Optional[str] = Field(None, alias="s3_endpoint")
    S3区域: Optional[str] = Field(None, alias="s3_region")
    S3密钥AK: Optional[str] = Field(None, alias="s3_access_key")
    S3密钥SK: Optional[str] = Field(None, alias="s3_secret_key")
    S3存储桶: Optional[str] = Field(None, alias="s3_bucket")
    S3公网地址: Optional[str] = Field(None, alias="s3_public_url")

    class Config:
        populate_by_name = True


class BrandingConfig(BaseModel):
    """品牌配置"""
    Logo地址: Optional[str] = Field(None, alias="logo_url")
    登录页标语: Optional[str] = Field(None, alias="login_tagline", max_length=500)
    系统名称: Optional[str] = Field(None, alias="system_name", max_length=100)

    class Config:
        populate_by_name = True


# ========== 工具函数 ==========

async def get_setting(db: AsyncSession, key: str, default: Any = None) -> Any:
    """获取系统设置值"""
    result = await db.execute(
        select(SystemSetting).where(SystemSetting.key == key)
    )
    setting = result.scalar_one_or_none()
    if setting is None:
        return default
    try:
        return json.loads(setting.value)
    except (json.JSONDecodeError, TypeError):
        return setting.value


async def set_setting(db: AsyncSession, key: str, value: Any, description: str = "") -> SystemSetting:
    """设置系统设置值"""
    result = await db.execute(
        select(SystemSetting).where(SystemSetting.key == key)
    )
    setting = result.scalar_one_or_none()
    if setting:
        setting.value = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
        if description:
            setting.description = description
    else:
        setting = SystemSetting(
            key=key,
            value=json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value,
            description=description,
        )
        db.add(setting)
    await db.flush()
    return setting


# ========== API端点 ==========

@router.get("/settings/all")
async def get_all_settings(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取所有系统设置"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可查看系统设置")

    result = await db.execute(select(SystemSetting))
    all_settings = result.scalars().all()

    settings_dict = {}
    for s in all_settings:
        try:
            settings_dict[s.key] = json.loads(s.value)
        except (json.JSONDecodeError, TypeError):
            settings_dict[s.key] = s.value

    return {
        "数据": settings_dict,
        "labels": {"数据": "data"}
    }


@router.get("/settings/{key}")
async def get_setting_by_key(
    key: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取单个系统设置"""
    value = await get_setting(db, key)
    return {key: value}


@router.put("/settings/{key}")
async def update_setting(
    key: str,
    req: SystemSettingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """更新系统设置"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可修改系统设置")

    await set_setting(db, key, req.value, req.说明 or "")
    return {"message": "设置已更新", "键": key, "值": req.value, "labels": {"message": "消息", "键": "key", "值": "value"}}


# ========== 品牌设置 ==========

# ========== 公开品牌信息（无需登录） ==========

@router.get("/branding/public")
async def get_public_branding(
    db: AsyncSession = Depends(get_db),
):
    """获取公开品牌信息（无需登录，登录页用）"""
    return {
        "数据": {
            "Logo地址": await get_setting(db, "logo_url", ""),
            "登录页标语": await get_setting(db, "login_tagline", "企业内部培训管理平台"),
            "系统名称": await get_setting(db, "system_name", settings.APP_NAME),
        },
        "labels": {"数据": "data"}
    }


@router.get("/branding")
async def get_branding(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取品牌配置"""
    return {
        "数据": {
            "Logo地址": await get_setting(db, "logo_url", ""),
            "登录页标语": await get_setting(db, "login_tagline", "企业内部培训管理平台"),
            "系统名称": await get_setting(db, "system_name", settings.APP_NAME),
        },
        "labels": {"数据": "data"}
    }


@router.put("/branding")
async def update_branding(
    req: BrandingConfig,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """更新品牌配置"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可修改品牌配置")

    if req.Logo地址 is not None:
        await set_setting(db, "logo_url", req.Logo地址, "系统Logo URL")
    if req.登录页标语 is not None:
        await set_setting(db, "login_tagline", req.登录页标语, "登录页标语")
    if req.系统名称 is not None:
        await set_setting(db, "system_name", req.系统名称, "系统名称")

    return {
        "message": "品牌配置已更新",
        "labels": {"message": "消息"}
    }


# ========== 对象存储配置 ==========

@router.get("/storage-config")
async def get_storage_config(
    current_user: dict = Depends(get_current_user),
):
    """获取当前存储配置（不返回密钥）"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可查看存储配置")
    return {
        "数据": {
            "存储模式": settings.STORAGE_MODE,
            "S3地址": settings.S3_ENDPOINT,
            "S3区域": settings.S3_REGION,
            "S3存储桶": settings.S3_BUCKET,
            "S3公网地址": settings.S3_PUBLIC_URL,
            # 密钥不返回
        },
        "labels": {"数据": "data"}
    }


@router.put("/storage-config")
async def update_storage_config(
    req: ObjectStorageConfig,
    current_user: dict = Depends(get_current_user),
):
    """更新对象存储配置（写入.env文件）"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可修改存储配置")

    # 更新内存中的配置
    settings.STORAGE_MODE = req.存储模式
    if req.S3地址:
        settings.S3_ENDPOINT = req.S3地址
    if req.S3区域:
        settings.S3_REGION = req.S3区域
    if req.S3密钥AK:
        settings.S3_ACCESS_KEY = req.S3密钥AK
    if req.S3密钥SK:
        settings.S3_SECRET_KEY = req.S3密钥SK
    if req.S3存储桶:
        settings.S3_BUCKET = req.S3存储桶
    if req.S3公网地址:
        settings.S3_PUBLIC_URL = req.S3公网地址

    # 写入.env文件
    env_path = ".env"
    env_vars = {
        "STORAGE_MODE": settings.STORAGE_MODE,
        "S3_ENDPOINT": settings.S3_ENDPOINT or "",
        "S3_REGION": settings.S3_REGION or "",
        "S3_ACCESS_KEY": settings.S3_ACCESS_KEY or "",
        "S3_SECRET_KEY": settings.S3_SECRET_KEY or "",
        "S3_BUCKET": settings.S3_BUCKET or "",
        "S3_PUBLIC_URL": settings.S3_PUBLIC_URL or "",
    }

    try:
        import os
        existing = {}
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        k, v = line.split('=', 1)
                        existing[k.strip()] = v.strip()

        existing.update(env_vars)
        with open(env_path, 'w') as f:
            for k, v in existing.items():
                f.write(f"{k}={v}\n")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"写入配置文件失败: {e}")

    return {
        "message": "存储配置已更新（重启后完全生效）",
        "labels": {"message": "消息"}
    }
