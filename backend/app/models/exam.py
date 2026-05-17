"""考试模型"""
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Question(Base):
    """题库题目"""
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("course_categories.id"), nullable=True)
    question_type = Column(String(20), nullable=False, comment="题型: single/multi/judge/fill/short_answer")
    title = Column(Text, nullable=False, comment="题目内容")
    options = Column(Text, nullable=True, comment="选项(JSON)")
    answer = Column(Text, nullable=True, comment="正确答案")
    score = Column(Float, default=10, comment="分值")
    difficulty = Column(Integer, default=1, comment="难度 1-5")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Exam(Base):
    """试卷"""
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    duration = Column(Integer, default=60, comment="考试时长(分钟)")
    total_score = Column(Float, default=100)
    pass_score = Column(Float, default=60, comment="及格分")
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ExamQuestion(Base):
    """试卷题目关联"""
    __tablename__ = "exam_questions"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    score = Column(Float, default=10)
    sort = Column(Integer, default=0)

    exam = relationship("Exam", backref="questions", lazy="selectin")
    question = relationship("Question", lazy="selectin")


class ExamResult(Base):
    """考试结果"""
    __tablename__ = "exam_results"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    score = Column(Float, default=0)
    answers = Column(Text, nullable=True, comment="答题记录(JSON)")
    status = Column(String(20), default="pending", comment="pending/grading/passed/failed")
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    submitted_at = Column(DateTime(timezone=True), nullable=True)
