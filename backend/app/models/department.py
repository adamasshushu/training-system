"""部门模型"""
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="部门名称")
    parent_id = Column(Integer, ForeignKey("departments.id"), nullable=True, comment="上级部门ID")
    sort = Column(Integer, default=0, comment="排序")
    is_active = Column(Boolean, default=True)

    children = relationship("Department", backref="parent", remote_side=[id], lazy="selectin")
    users = relationship("User", back_populates="department", lazy="selectin")
