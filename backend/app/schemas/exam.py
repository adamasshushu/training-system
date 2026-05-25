"""考试相关Pydantic模型"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ========== 题目 ==========

class QuestionCreate(BaseModel):
    """创建题目"""
    分类ID: Optional[int] = Field(None, alias="category_id")
    题型: str = Field(..., alias="question_type", pattern="^(single|multi|judge|fill|short_answer)$")
    题目内容: str = Field(..., alias="title")
    选项: Optional[str] = Field(None, alias="options")
    正确答案: Optional[str] = Field(None, alias="answer")
    分值: float = Field(10, alias="score", ge=0)
    难度: int = Field(1, alias="difficulty", ge=1, le=5)

    class Config:
        populate_by_name = True


class QuestionUpdate(BaseModel):
    分类ID: Optional[int] = Field(None, alias="category_id")
    题型: Optional[str] = Field(None, alias="question_type")
    题目内容: Optional[str] = Field(None, alias="title")
    选项: Optional[str] = Field(None, alias="options")
    正确答案: Optional[str] = Field(None, alias="answer")
    分值: Optional[float] = Field(None, ge=0, alias="score")
    难度: Optional[int] = Field(None, alias="difficulty")

    class Config:
        populate_by_name = True


class QuestionResponse(BaseModel):
    """题目响应"""
    ID: int = Field(..., alias="id")
    分类ID: Optional[int] = Field(None, alias="category_id")
    题型: str = Field(..., alias="question_type")
    题目内容: str = Field(..., alias="title")
    选项: Optional[str] = Field(None, alias="options")
    正确答案: Optional[str] = Field(None, alias="answer")
    分值: float = Field(10, alias="score")
    难度: int = Field(1, alias="difficulty")
    创建时间: Optional[str] = Field(None, alias="created_at")
    labels: dict = {
        "ID": "id",
        "分类ID": "category_id",
        "题型": "question_type",
        "题目内容": "title",
        "选项": "options",
        "正确答案": "answer",
        "分值": "score",
        "难度": "difficulty",
        "创建时间": "created_at"
    }

    class Config:
        populate_by_name = True


# ========== 试卷与选题 ==========

class ExamQuestionCreate(BaseModel):
    题目ID: int
    分值: float = Field(10, alias="score", ge=0)
    排序: int = 0


class ExamCreate(BaseModel):
    """创建试卷"""
    标题: str = Field(..., alias="title", min_length=1, max_length=200)
    描述: Optional[str] = Field(None, alias="description")
    考试时长: int = Field(60, alias="duration")
    总分: float = Field(100, alias="total_score")
    及格分: float = Field(60, alias="pass_score")
    是否发布: bool = Field(False, alias="is_published")
    选题列表: List[ExamQuestionCreate] = []

    class Config:
        populate_by_name = True


class ExamUpdate(BaseModel):
    标题: Optional[str] = Field(None, alias="title")
    描述: Optional[str] = Field(None, alias="description")
    考试时长: Optional[int] = Field(None, alias="duration")
    总分: Optional[float] = Field(None, alias="total_score")
    及格分: Optional[float] = Field(None, alias="pass_score")
    是否发布: Optional[bool] = Field(None, alias="is_published")

    class Config:
        populate_by_name = True


class ExamResponse(BaseModel):
    """试卷响应"""
    ID: int = Field(..., alias="id")
    标题: str = Field(..., alias="title")
    描述: Optional[str] = Field(None, alias="description")
    考试时长: int = Field(60, alias="duration")
    总分: float = Field(100, alias="total_score")
    及格分: float = Field(60, alias="pass_score")
    是否发布: bool = Field(False, alias="is_published")
    题目数量: int = 0
    创建时间: Optional[str] = Field(None, alias="created_at")
    labels: dict = {
        "ID": "id",
        "标题": "title",
        "描述": "description",
        "考试时长": "duration",
        "总分": "total_score",
        "及格分": "pass_score",
        "是否发布": "is_published",
        "题目数量": "question_count",
        "创建时间": "created_at"
    }

    class Config:
        populate_by_name = True


class ExamDetailResponse(BaseModel):
    """试卷详情（含题目）"""
    ID: int
    标题: str
    描述: Optional[str] = None
    考试时长: int = 60
    总分: float = 100
    及格分: float = 60
    是否发布: bool = False
    题目列表: List[Any] = []
    创建时间: Optional[str] = None
    labels: dict = {
        "ID": "id",
        "标题": "title",
        "描述": "description",
        "考试时长": "duration",
        "总分": "total_score",
        "及格分": "pass_score",
        "是否发布": "is_published",
        "题目列表": "questions",
        "创建时间": "created_at"
    }


# ========== 考试结果 ==========

class ExamResultSubmit(BaseModel):
    """提交考试答案"""
    答案: Dict[str, str] = Field(..., alias="answers", description="题目ID -> 用户答案")

    class Config:
        populate_by_name = True


class ExamResultResponse(BaseModel):
    """考试结果响应"""
    ID: int
    试卷ID: int
    用户ID: int
    得分: float = 0
    状态: str = "pending"
    开始时间: Optional[str] = None
    提交时间: Optional[str] = None
    labels: dict = {
        "ID": "id",
        "试卷ID": "exam_id",
        "用户ID": "user_id",
        "得分": "score",
        "状态": "status",
        "开始时间": "started_at",
        "提交时间": "submitted_at"
    }


class ExamResultDetailResponse(BaseModel):
    """考试结果详情"""
    ID: int
    试卷ID: int
    试卷标题: Optional[str] = None
    用户ID: int
    用户姓名: Optional[str] = None
    得分: float = 0
    总分: float = 100
    及格分: float = 60
    状态: str = "pending"
    详细答案: Optional[Any] = None
    开始时间: Optional[str] = None
    提交时间: Optional[str] = None
    labels: dict = {
        "ID": "id",
        "试卷ID": "exam_id",
        "试卷标题": "exam_title",
        "用户ID": "user_id",
        "用户姓名": "user_name",
        "得分": "score",
        "总分": "total_score",
        "及格分": "pass_score",
        "状态": "status",
        "详细答案": "answers_detail",
        "开始时间": "started_at",
        "提交时间": "submitted_at"
    }
