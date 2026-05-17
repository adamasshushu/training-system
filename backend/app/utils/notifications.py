"""通知工具：创建通知并推送到企业平台"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification


async def create_notification(
    db: AsyncSession,
    user_id: int,
    title: str,
    content: Optional[str] = None,
    notification_type: str = "system",
    reference_id: Optional[int] = None,
) -> Notification:
    """创建系统通知"""
    notif = Notification(
        user_id=user_id,
        title=title,
        content=content,
        notification_type=notification_type,
        reference_id=reference_id,
    )
    db.add(notif)
    await db.flush()
    return notif


async def notify_task_assigned(db: AsyncSession, user_id: int, task_id: int, task_title: str, deadline: Optional[str] = None):
    """通知：任务已指派"""
    deadline_str = f"\n⏰ 截止日期: {deadline}" if deadline else ""
    content = f"你有一个新的培训任务「{task_title}」，请尽快查看并完成学习。{deadline_str}"
    await create_notification(
        db, user_id=user_id,
        title=f"📋 新任务: {task_title}",
        content=content,
        notification_type="task_assigned",
        reference_id=task_id,
    )


async def notify_deadline_reminder(db: AsyncSession, user_id: int, task_id: int, task_title: str, deadline: str):
    """通知：任务即将到期"""
    await create_notification(
        db, user_id=user_id,
        title=f"⏰ 任务即将到期: {task_title}",
        content=f"培训任务「{task_title}」将于 {deadline} 截止，请尽快完成！",
        notification_type="deadline_reminder",
        reference_id=task_id,
    )


async def notify_exam_result(db: AsyncSession, user_id: int, exam_id: int, exam_title: str, score: float, passed: bool):
    """通知：考试结果"""
    status = "✅ 通过" if passed else "❌ 未通过"
    await create_notification(
        db, user_id=user_id,
        title=f"{status} {exam_title}",
        content=f"考试「{exam_title}」得分: {score}分，{'恭喜通过！' if passed else '未达到及格线，请重新考试。'}",
        notification_type="exam_result",
        reference_id=exam_id,
    )
