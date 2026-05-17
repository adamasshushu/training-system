"""培训任务相关Pydantic模型"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class TaskCourseCreate(BaseModel):
    课程ID: int
    排序: int = 0


class TaskExamCreate(BaseModel):
    考试ID: int
    排序: int = 0


class TrainingTaskCreate(BaseModel):
    """创建培训任务"""
    标题: str = Field(..., alias="title", min_length=1, max_length=200)
    描述: Optional[str] = Field(None, alias="description")
    模式: str = Field("free", alias="mode", pattern="^(free|level)$")
    截止日期: Optional[str] = Field(None, alias="deadline")
    是否发布: bool = Field(False, alias="is_published")
    课程列表: List[TaskCourseCreate] = []
    考试列表: List[TaskExamCreate] = []

    class Config:
        populate_by_name = True


class TrainingTaskUpdate(BaseModel):
    标题: Optional[str] = Field(None, alias="title")
    描述: Optional[str] = Field(None, alias="description")
    模式: Optional[str] = Field(None, alias="mode")
    截止日期: Optional[str] = Field(None, alias="deadline")
    是否发布: Optional[bool] = Field(None, alias="is_published")

    class Config:
        populate_by_name = True


class TaskAssignmentCreate(BaseModel):
    """指派任务"""
    指派类型: str = Field(..., alias="assignee_type", pattern="^(department|user)$")
    指派对象ID: int = Field(..., alias="assignee_id")

    class Config:
        populate_by_name = True


class TaskAssignmentResponse(BaseModel):
    ID: int
    任务ID: int
    指派类型: str
    指派对象ID: int
    创建时间: Optional[str] = None
    labels: dict = {
        "ID": "id",
        "任务ID": "task_id",
        "指派类型": "assignee_type",
        "指派对象ID": "assignee_id",
        "创建时间": "created_at"
    }


class TrainingTaskResponse(BaseModel):
    """培训任务响应"""
    ID: int = Field(..., alias="id")
    标题: str = Field(..., alias="title")
    描述: Optional[str] = Field(None, alias="description")
    模式: str = Field("free", alias="mode")
    创建人: Optional[int] = Field(None, alias="created_by")
    创建人姓名: Optional[str] = None
    截止日期: Optional[str] = Field(None, alias="deadline")
    是否发布: bool = Field(False, alias="is_published")
    创建时间: Optional[str] = Field(None, alias="created_at")
    课程数量: int = 0
    考试数量: int = 0
    labels: dict = {
        "ID": "id",
        "标题": "title",
        "描述": "description",
        "模式": "mode",
        "创建人": "created_by",
        "创建人姓名": "creator_name",
        "截止日期": "deadline",
        "是否发布": "is_published",
        "创建时间": "created_at",
        "课程数量": "course_count",
        "考试数量": "exam_count"
    }

    class Config:
        populate_by_name = True


class TrainingTaskDetailResponse(BaseModel):
    """培训任务详情"""
    ID: int
    标题: str
    描述: Optional[str] = None
    模式: str = "free"
    创建人: Optional[int] = None
    创建人姓名: Optional[str] = None
    截止日期: Optional[str] = None
    是否发布: bool = False
    创建时间: Optional[str] = None
    关联课程: List[Any] = []
    关联考试: List[Any] = []
    指派记录: List[Any] = []
    labels: dict = {
        "ID": "id",
        "标题": "title",
        "描述": "description",
        "模式": "mode",
        "创建人": "created_by",
        "创建人姓名": "creator_name",
        "截止日期": "deadline",
        "是否发布": "is_published",
        "创建时间": "created_at",
        "关联课程": "courses",
        "关联考试": "exams",
        "指派记录": "assignments"
    }
