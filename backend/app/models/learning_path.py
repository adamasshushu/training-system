"""学习路径模型"""
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class LearningPath(Base):
    """学习路径"""
    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, comment="路径名称")
    description = Column(Text, nullable=True, comment="路径描述")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_published = Column(Boolean, default=False)
    sort = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    courses = relationship("LearningPathCourse", back_populates="path", order_by="LearningPathCourse.sort", lazy="selectin", cascade="all, delete-orphan")


class LearningPathCourse(Base):
    """学习路径关联课程"""
    __tablename__ = "learning_path_courses"

    id = Column(Integer, primary_key=True, index=True)
    path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    sort = Column(Integer, default=0, comment="排序(学习顺序)")
    required = Column(Boolean, default=True, comment="是否必修")
    estimated_hours = Column(Float, default=0, comment="预估学习时长(小时)")

    path = relationship("LearningPath", back_populates="courses", lazy="selectin")
    course = relationship("Course", lazy="selectin")


class UserLearningPath(Base):
    """用户学习路径进度"""
    __tablename__ = "user_learning_paths"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=False)
    status = Column(String(20), default="in_progress", comment="状态: not_started/in_progress/completed")
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
