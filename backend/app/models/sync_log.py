"""同步日志模型"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database import Base


class SyncLog(Base):
    """企业平台同步日志"""
    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    platform = Column(String(20), nullable=False, comment="平台: ldap/dingtalk/feishu/wecom")
    status = Column(String(20), nullable=False, comment="success/error")
    ous_synced = Column(Integer, default=0, comment="同步的部门数")
    users_added = Column(Integer, default=0, comment="新增用户数")
    users_updated = Column(Integer, default=0, comment="更新用户数")
    users_skipped = Column(Integer, default=0, comment="跳过的用户数")
    errors = Column(Text, nullable=True, comment="错误详情 JSON")
    operator = Column(String(50), nullable=True, comment="操作人")
    created_at = Column(DateTime, default=datetime.utcnow, comment="同步时间")
