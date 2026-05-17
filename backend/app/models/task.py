"""培训任务模型"""
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class TrainingTask(Base):
    """培训任务"""
    __tablename__ = "training_tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    mode = Column(String(20), default="free", comment="模式: free自由/level闯关")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deadline = Column(DateTime(timezone=True), nullable=True, comment="截止日期")


class TaskCourse(Base):
    """任务关联课程"""
    __tablename__ = "task_courses"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("training_tasks.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    sort = Column(Integer, default=0)

    task = relationship("TrainingTask", backref="courses", lazy="selectin")
    course = relationship("Course", lazy="selectin")


class TaskExam(Base):
    """任务关联考试"""
    __tablename__ = "task_exams"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("training_tasks.id"), nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    sort = Column(Integer, default=0)

    task = relationship("TrainingTask", backref="exams", lazy="selectin")
    exam = relationship("Exam", lazy="selectin")


class TaskAssignment(Base):
    """任务指派"""
    __tablename__ = "task_assignments"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("training_tasks.id"), nullable=False)
    assignee_type = Column(String(20), comment="department/user")
    assignee_id = Column(Integer, nullable=False, comment="部门ID或用户ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    task = relationship("TrainingTask", backref="assignments", lazy="selectin")
