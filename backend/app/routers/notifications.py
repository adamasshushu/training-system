"""通知路由"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.database import get_db
from app.models.notification import Notification
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["通知"])


@router.get("")
async def list_notifications(
    unread_only: bool = Query(False, alias="unread_only"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取我的通知列表"""
    query = select(Notification).where(
        Notification.user_id == current_user["id"]
    )
    if unread_only:
        query = query.where(Notification.is_read == False)
    query = query.order_by(Notification.id.desc())

    result = await db.execute(query)
    all_notifs = result.scalars().all()
    total = len(all_notifs)
    start = (page - 1) * page_size
    page_notifs = all_notifs[start:start + page_size]

    notif_list = []
    for n in page_notifs:
        notif_list.append({
            "ID": n.id,
            "标题": n.title,
            "内容": n.content,
            "类型": n.notification_type,
            "关联ID": n.reference_id,
            "已读": n.is_read,
            "创建时间": str(n.created_at) if n.created_at else None,
        })

    # 未读数
    unread_count = sum(1 for n in all_notifs if not n.is_read)

    return {
        "数据": notif_list,
        "共计": total,
        "未读数": unread_count,
        "页码": page, "每页数量": page_size,
        "labels": {"数据": "data", "共计": "total", "未读数": "unread_count"}
    }


@router.put("/{notif_id}/read")
async def mark_as_read(
    notif_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """标记通知为已读"""
    result = await db.execute(
        select(Notification).where(
            Notification.id == notif_id,
            Notification.user_id == current_user["id"],
        )
    )
    notif = result.scalar_one_or_none()
    if not notif:
        raise HTTPException(status_code=404, detail="通知不存在")
    notif.is_read = True
    await db.flush()
    return {"message": "已标记为已读", "labels": {"message": "消息"}}


@router.put("/read-all")
async def mark_all_as_read(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """标记所有通知为已读"""
    await db.execute(
        update(Notification)
        .where(
            Notification.user_id == current_user["id"],
            Notification.is_read == False,
        )
        .values(is_read=True)
    )
    await db.flush()
    return {"message": "全部已读", "labels": {"message": "消息"}}


@router.get("/unread-count")
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取未读通知数"""
    result = await db.execute(
        select(Notification).where(
            Notification.user_id == current_user["id"],
            Notification.is_read == False,
        )
    )
    count = len(result.scalars().all())
    return {"未读数": count, "labels": {"未读数": "unread_count"}}
