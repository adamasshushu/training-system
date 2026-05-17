"""课程评价 + 培训反馈路由"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.course import Course
from app.models.review import CourseReview, TrainerFeedback
from app.models.task import TrainingTask
from app.models.user import User
from app.utils.auth import get_current_user
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/reviews", tags=["评价反馈"])


# ========== Pydantic ==========

class ReviewCreate(BaseModel):
    课程ID: int = Field(..., alias="course_id")
    评分: int = Field(..., alias="rating", ge=1, le=5)
    评价内容: Optional[str] = Field(None, alias="content")
    是否匿名: bool = Field(False, alias="is_anonymous")
    class Config: populate_by_name = True

class FeedbackCreate(BaseModel):
    任务ID: Optional[int] = Field(None, alias="task_id")
    内容评分: int = Field(3, alias="content_rating", ge=1, le=5)
    系统评分: int = Field(3, alias="system_rating", ge=1, le=5)
    建议: Optional[str] = Field(None, alias="suggestion")
    class Config: populate_by_name = True


# ========== 课程评价 ==========

@router.get("/course/{course_id}")
async def list_course_reviews(
    course_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取课程评价列表"""
    query = select(CourseReview).where(CourseReview.course_id == course_id).order_by(CourseReview.id.desc())
    result = await db.execute(query)
    all_reviews = result.scalars().all()
    total = len(all_reviews)
    start = (page - 1) * page_size
    page_reviews = all_reviews[start:start + page_size]

    # 平均分
    avg_result = await db.execute(
        select(func.avg(CourseReview.rating)).where(CourseReview.course_id == course_id)
    )
    avg_rating = round(avg_result.scalar() or 0, 1)

    review_list = []
    for r in page_reviews:
        reviewer_name = "匿名用户" if r.is_anonymous else r.user.real_name
        review_list.append({
            "ID": r.id,
            "评分": r.rating,
            "评价内容": r.content,
            "评价人": reviewer_name,
            "是否匿名": r.is_anonymous,
            "创建时间": str(r.created_at) if r.created_at else None,
        })

    return {
        "数据": review_list,
        "共计": total,
        "平均分": avg_rating,
        "页码": page, "每页数量": page_size,
        "labels": {"数据": "data", "共计": "total", "平均分": "avg_rating"}
    }


@router.post("/course")
async def create_review(
    req: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """提交课程评价"""
    # 检查课程存在
    c_result = await db.execute(select(Course).where(Course.id == req.课程ID))
    if not c_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="课程不存在")

    # 检查是否已评价过
    existing = await db.execute(
        select(CourseReview).where(
            CourseReview.course_id == req.课程ID,
            CourseReview.user_id == current_user["id"],
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="你已经评价过该课程")

    review = CourseReview(
        course_id=req.课程ID,
        user_id=current_user["id"],
        rating=req.评分,
        content=req.评价内容,
        is_anonymous=req.是否匿名,
    )
    db.add(review)
    await db.flush()
    return {"message": "评价已提交", "ID": review.id, "评分": review.rating, "labels": {"message": "消息", "ID": "id", "评分": "rating"}}


# ========== 培训反馈 ==========

@router.post("/feedback")
async def submit_feedback(
    req: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """提交培训反馈（学习完成后）"""
    if req.任务ID:
        t_result = await db.execute(select(TrainingTask).where(TrainingTask.id == req.任务ID))
        if not t_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="任务不存在")

    feedback = TrainerFeedback(
        user_id=current_user["id"],
        task_id=req.任务ID,
        content_rating=req.内容评分,
        system_rating=req.系统评分,
        suggestion=req.建议,
    )
    db.add(feedback)
    await db.flush()
    return {"message": "反馈已提交", "ID": feedback.id, "labels": {"message": "消息", "ID": "id"}}


@router.get("/feedback")
async def list_feedback(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """管理员查看所有培训反馈"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可查看")

    query = select(TrainerFeedback).order_by(TrainerFeedback.id.desc())
    result = await db.execute(query)
    all_fb = result.scalars().all()
    total = len(all_fb)
    start = (page - 1) * page_size
    page_fb = all_fb[start:start + page_size]

    # 平均分
    avg_content = await db.execute(select(func.avg(TrainerFeedback.content_rating)))
    avg_system = await db.execute(select(func.avg(TrainerFeedback.system_rating)))

    fb_list = []
    for f in page_fb:
        u = (await db.execute(select(User).where(User.id == f.user_id))).scalar_one_or_none()
        fb_list.append({
            "ID": f.id,
            "用户": u.real_name if u else "未知",
            "内容评分": f.content_rating,
            "系统评分": f.system_rating,
            "建议": f.suggestion,
            "任务ID": f.task_id,
            "创建时间": str(f.created_at) if f.created_at else None,
        })

    return {
        "数据": fb_list,
        "共计": total,
        "平均内容评分": round(avg_content.scalar() or 0, 1),
        "平均系统评分": round(avg_system.scalar() or 0, 1),
        "页码": page, "每页数量": page_size,
        "labels": {"数据": "data", "共计": "total"}
    }
