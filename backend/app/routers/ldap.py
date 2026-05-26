"""
LDAP/AD 实时操作 API

对标 AdDomainPlatform 的 Controllers：
- OUsController  → /api/ldap/ous
- AdUsersController → /api/ldap/users
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.database import get_db
from app.utils.auth import get_current_user
from app.services.ldap_service import get_ldap_service

router = APIRouter(prefix="/api/ldap", tags=["LDAP/AD"])


class ResetPasswordRequest(BaseModel):
    新密码: str = Field(..., alias="new_password", min_length=6)
    class Config:
        populate_by_name = True


# ═══════════════ OU 树 ═══════════════

@router.get("/ous")
async def ldap_ou_tree(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """实时获取 AD OU 树 — 对标 AdDomainPlatform OUsController"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可访问")

    svc = await get_ldap_service(db)
    if not svc:
        raise HTTPException(status_code=400, detail="LDAP/AD 未配置或未启用")

    tree = await svc.get_ou_tree()
    return {"数据": tree, "labels": {"数据": "data"}}


# ═══════════════ 用户搜索 ═══════════════

@router.get("/users")
async def ldap_search_users(
    keyword: str = Query("", alias="keyword"),
    ou_dn: str = Query("", alias="ou_dn"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    实时搜索 AD 用户 — 对标 AdDomainPlatform AdUsersController
    
    - keyword: 搜索 sAMAccountName / displayName / mail
    - ou_dn: 限定 OU (留空搜索整个域)
    """
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可访问")

    svc = await get_ldap_service(db)
    if not svc:
        raise HTTPException(status_code=400, detail="LDAP/AD 未配置或未启用")

    users = await svc.search_users(keyword=keyword, ou_dn=ou_dn)
    return {"数据": users, "共计": len(users), "labels": {"数据": "data", "共计": "total"}}


# ═══════════════ 用户详情 ═══════════════

@router.get("/users/detail")
async def ldap_user_detail(
    dn: str = Query(..., alias="dn"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取 AD 用户完整详情 — 对标 AdDomainPlatform 7 个属性 Tab"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可访问")

    svc = await get_ldap_service(db)
    if not svc:
        raise HTTPException(status_code=400, detail="LDAP/AD 未配置或未启用")

    detail = await svc.get_user_detail(dn)
    if not detail:
        raise HTTPException(status_code=404, detail="用户不存在")

    return {"数据": detail, "labels": {"数据": "data"}}


# ═══════════════ 用户操作 ═══════════════

@router.post("/users/reset-password")
async def ldap_reset_password(
    req: ResetPasswordRequest,
    dn: str = Query(..., alias="dn"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """重置 AD 用户密码 — 对标 AdDomainPlatform ResetPasswordAsync"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可操作")

    svc = await get_ldap_service(db)
    if not svc:
        raise HTTPException(status_code=400, detail="LDAP/AD 未配置或未启用")

    ok, msg = await svc.reset_password(dn, req.新密码)
    if not ok:
        raise HTTPException(status_code=500, detail=msg)

    return {"message": msg, "labels": {"message": "消息"}}


@router.post("/users/enable")
async def ldap_enable_user(
    dn: str = Query(..., alias="dn"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """启用 AD 用户"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可操作")

    svc = await get_ldap_service(db)
    if not svc:
        raise HTTPException(status_code=400, detail="LDAP/AD 未配置或未启用")

    ok, msg = await svc.set_user_status(dn, enable=True)
    if not ok:
        raise HTTPException(status_code=500, detail=msg)

    return {"message": msg, "labels": {"message": "消息"}}


@router.post("/users/disable")
async def ldap_disable_user(
    dn: str = Query(..., alias="dn"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """禁用 AD 用户"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可操作")

    svc = await get_ldap_service(db)
    if not svc:
        raise HTTPException(status_code=400, detail="LDAP/AD 未配置或未启用")

    ok, msg = await svc.set_user_status(dn, enable=False)
    if not ok:
        raise HTTPException(status_code=500, detail=msg)

    return {"message": msg, "labels": {"message": "消息"}}


@router.post("/users/unlock")
async def ldap_unlock_user(
    dn: str = Query(..., alias="dn"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """解锁 AD 账户"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可操作")

    svc = await get_ldap_service(db)
    if not svc:
        raise HTTPException(status_code=400, detail="LDAP/AD 未配置或未启用")

    ok, msg = await svc.unlock_user(dn)
    if not ok:
        raise HTTPException(status_code=500, detail=msg)

    return {"message": msg, "labels": {"message": "消息"}}
