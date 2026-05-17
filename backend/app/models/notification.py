"""通知模型"""
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class Notification(Base):
    """系统通知"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="接收用户")
    title = Column(String(200), nullable=False, comment="通知标题")
    content = Column(Text, nullable=True, comment="通知内容")
    notification_type = Column(String(50), nullable=False, comment="类型: task_assigned/deadline_reminder/exam_result/cert_issued")
    reference_id = Column(Integer, nullable=True, comment="关联业务ID(任务ID/考试ID)")
    is_read = Column(Boolean, default=False, comment="是否已读")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
