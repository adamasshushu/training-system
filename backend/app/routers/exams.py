"""考试管理路由"""
from typing import Optional
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.exam import Question, Exam, ExamQuestion, ExamResult
from app.models.user import User
from app.utils.auth import get_current_user
from app.schemas.exam import (
    QuestionCreate, QuestionUpdate, ExamCreate, ExamUpdate,
    ExamResultSubmit, ExamQuestionCreate
)

router = APIRouter(prefix="/api", tags=["考试管理"])


# ========== 题库管理 ==========

@router.get("/questions")
async def list_questions(
    question_type: Optional[str] = Query(None, alias="question_type"),
    category_id: Optional[int] = Query(None, alias="category_id"),
    keyword: Optional[str] = Query(None, alias="keyword"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """题目列表"""
    query = select(Question)
    if question_type:
        query = query.where(Question.question_type == question_type)
    if category_id:
        query = query.where(Question.category_id == category_id)
    if keyword:
        query = query.where(Question.title.contains(keyword))
    query = query.order_by(Question.id.desc())

    result = await db.execute(query)
    questions = result.scalars().all()
    total = len(questions)
    start = (page - 1) * page_size
    page_qs = questions[start:start + page_size]

    return {
        "数据": [{
            "ID": q.id,
            "分类ID": q.category_id,
            "题型": q.question_type,
            "题目内容": q.title,
            "选项": q.options,
            "正确答案": q.answer,
            "分值": q.score,
            "难度": q.difficulty,
            "创建时间": str(q.created_at) if q.created_at else None,
        } for q in page_qs],
        "共计": total,
        "页码": page,
        "每页数量": page_size,
        "labels": {
            "ID": "id", "题型": "question_type",
            "题目内容": "title", "选项": "options",
            "正确答案": "answer", "分值": "score"
        }
    }


@router.post("/questions")
async def create_question(
    req: QuestionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建题目"""
    if current_user.get("角色") not in ("admin", "teacher"):
        raise HTTPException(status_code=403, detail="无权限创建题目")
    question = Question(
        category_id=req.分类ID,
        question_type=req.题型,
        title=req.题目内容,
        options=req.选项,
        answer=req.正确答案,
        score=req.分值,
        difficulty=req.难度,
    )
    db.add(question)
    await db.flush()
    return {
        "message": "题目创建成功",
        "ID": question.id,
        "labels": {"message": "消息", "ID": "id"}
    }


@router.put("/questions/{question_id}")
async def update_question(
    question_id: int,
    req: QuestionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """更新题目"""
    if current_user.get("角色") not in ("admin", "teacher"):
        raise HTTPException(status_code=403, detail="无权限修改题目")
    result = await db.execute(select(Question).where(Question.id == question_id))
    q = result.scalar_one_or_none()
    if not q:
        raise HTTPException(status_code=404, detail="题目不存在")
    if req.分类ID is not None:
        q.category_id = req.分类ID
    if req.题型 is not None:
        q.question_type = req.题型
    if req.题目内容 is not None:
        q.title = req.题目内容
    if req.选项 is not None:
        q.options = req.选项
    if req.正确答案 is not None:
        q.answer = req.正确答案
    if req.分值 is not None:
        q.score = req.分值
    if req.难度 is not None:
        q.difficulty = req.难度
    await db.flush()
    return {"message": "题目更新成功", "labels": {"message": "消息"}}


@router.delete("/questions/{question_id}")
async def delete_question(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """删除题目"""
    if current_user.get("角色") not in ("admin", "teacher"):
        raise HTTPException(status_code=403, detail="无权限删除题目")
    result = await db.execute(select(Question).where(Question.id == question_id))
    q = result.scalar_one_or_none()
    if not q:
        raise HTTPException(status_code=404, detail="题目不存在")
    await db.delete(q)
    await db.flush()
    return {"message": "题目已删除", "labels": {"message": "消息"}}


# ========== 试卷管理 ==========

@router.get("/exams")
async def list_exams(
    is_published: Optional[bool] = Query(None, alias="is_published"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """试卷列表"""
    query = select(Exam)
    if is_published is not None:
        query = query.where(Exam.is_published == is_published)
    query = query.order_by(Exam.id.desc())
    result = await db.execute(query)
    exams = result.scalars().all()
    total = len(exams)
    start = (page - 1) * page_size
    page_exams = exams[start:start + page_size]

    exam_list = []
    for e in page_exams:
        eq_result = await db.execute(
            select(ExamQuestion).where(ExamQuestion.exam_id == e.id)
        )
        exam_list.append({
            "ID": e.id,
            "标题": e.title,
            "描述": e.description,
            "考试时长": e.duration,
            "总分": e.total_score,
            "及格分": e.pass_score,
            "是否发布": e.is_published,
            "题目数量": len(eq_result.scalars().all()),
            "创建时间": str(e.created_at) if e.created_at else None,
        })

    return {
        "数据": exam_list,
        "共计": total,
        "页码": page,
        "每页数量": page_size,
        "labels": {"数据": "data", "共计": "total"}
    }


@router.post("/exams")
async def create_exam(
    req: ExamCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建试卷（含选题）"""
    if current_user.get("角色") not in ("admin", "teacher"):
        raise HTTPException(status_code=403, detail="无权限创建试卷")
    exam = Exam(
        title=req.标题,
        description=req.描述,
        duration=req.考试时长,
        total_score=req.总分,
        pass_score=req.及格分,
        is_published=req.是否发布,
    )
    db.add(exam)
    await db.flush()

    # 添加选题
    for idx, eq in enumerate(req.选题列表):
        # 验证题目存在
        q_result = await db.execute(
            select(Question).where(Question.id == eq.题目ID)
        )
        if not q_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail=f"题目ID {eq.题目ID} 不存在")
        exam_q = ExamQuestion(
            exam_id=exam.id,
            question_id=eq.题目ID,
            score=eq.分值,
            sort=eq.排序 or idx,
        )
        db.add(exam_q)
    await db.flush()
    return {
        "message": "试卷创建成功",
        "ID": exam.id,
        "标题": exam.title,
        "labels": {"message": "消息", "ID": "id", "标题": "title"}
    }


@router.get("/exams/{exam_id}")
async def get_exam_detail(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """试卷详情（含题目）"""
    result = await db.execute(select(Exam).where(Exam.id == exam_id))
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="试卷不存在")

    eq_result = await db.execute(
        select(ExamQuestion)
        .where(ExamQuestion.exam_id == exam_id)
        .order_by(ExamQuestion.sort)
    )
    exam_questions = eq_result.scalars().all()

    questions = []
    for eq in exam_questions:
        q_result = await db.execute(
            select(Question).where(Question.id == eq.question_id)
        )
        q = q_result.scalar_one_or_none()
        if q:
            questions.append({
                "ID": q.id,
                "题型": q.question_type,
                "题目内容": q.title,
                "选项": q.options,
                "分值": eq.score or q.score,
                "难度": q.difficulty,
            })

    return {
        "数据": {
            "ID": exam.id,
            "标题": exam.title,
            "描述": exam.description,
            "考试时长": exam.duration,
            "总分": exam.total_score,
            "及格分": exam.pass_score,
            "是否发布": exam.is_published,
            "题目列表": questions,
            "创建时间": str(exam.created_at) if exam.created_at else None,
        },
        "labels": {
            "ID": "id", "标题": "title", "描述": "description",
            "考试时长": "duration", "总分": "total_score",
            "及格分": "pass_score", "题目列表": "questions"
        }
    }




@router.put("/exams/{exam_id}")
async def update_exam(
    exam_id: int,
    req: ExamUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """更新试卷"""
    if current_user.get("角色") not in ("admin", "teacher"):
        raise HTTPException(status_code=403, detail="无权限")
    result = await db.execute(select(Exam).where(Exam.id == exam_id))
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="试卷不存在")
    if req.标题 is not None:
        exam.title = req.标题
    if req.描述 is not None:
        exam.description = req.描述
    if req.考试时长 is not None:
        exam.duration = req.考试时长
    if req.总分 is not None:
        exam.total_score = req.总分
    if req.及格分 is not None:
        exam.pass_score = req.及格分
    if req.是否发布 is not None:
        exam.is_published = req.是否发布
    await db.flush()
    return {"message": "试卷更新成功", "labels": {"message": "消息"}}


@router.delete("/exams/{exam_id}")
async def delete_exam(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """删除试卷"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可删除")
    result = await db.execute(select(Exam).where(Exam.id == exam_id))
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="试卷不存在")
    await db.delete(exam)
    await db.flush()
    return {"message": "试卷已删除", "labels": {"message": "消息"}}


# ========== 考试提交与结果 ==========

@router.post("/exams/{exam_id}/submit")
async def submit_exam(
    exam_id: int,
    req: ExamResultSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """提交考试答案并自动判分"""
    result = await db.execute(select(Exam).where(Exam.id == exam_id))
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="试卷不存在")

    # 获取试卷中的题目
    eq_result = await db.execute(
        select(ExamQuestion).where(ExamQuestion.exam_id == exam_id)
    )
    exam_questions = eq_result.scalars().all()

    total_score = 0
    answers_detail = {}
    for eq in exam_questions:
        q_result = await db.execute(
            select(Question).where(Question.id == eq.question_id)
        )
        q = q_result.scalar_one_or_none()
        if not q:
            continue
        qid_str = str(q.id)
        user_answer = req.答案.get(qid_str, "")
        correct = q.answer
        is_correct = user_answer.strip() == (correct or "").strip()
        score = eq.score if eq.score else q.score
        if is_correct:
            total_score += score
        answers_detail[qid_str] = {
            "题目内容": q.title,
            "你的答案": user_answer,
            "正确答案": correct,
            "是否正确": is_correct,
            "得分": score if is_correct else 0,
        }

    status_val = "passed" if total_score >= exam.pass_score else "failed"

    exam_result = ExamResult(
        exam_id=exam_id,
        user_id=current_user["id"],
        score=total_score,
        answers=json.dumps(answers_detail, ensure_ascii=False),
        status=status_val,
    )
    db.add(exam_result)
    await db.flush()

    return {
        "message": "考试已提交",
        "得分": total_score,
        "总分": exam.total_score,
        "状态": "及格" if status_val == "passed" else "不及格",
        "labels": {"message": "消息", "得分": "score", "总分": "total_score", "状态": "status"}
    }


@router.get("/exams/{exam_id}/results")
async def get_exam_results(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """查看考试成绩"""
    result = await db.execute(select(Exam).where(Exam.id == exam_id))
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="试卷不存在")

    query = select(ExamResult).where(ExamResult.exam_id == exam_id)
    # 学员只能看自己的成绩
    if current_user.get("角色") == "student":
        query = query.where(ExamResult.user_id == current_user["id"])
    query = query.order_by(ExamResult.submitted_at.desc())
    result = await db.execute(query)
    results = result.scalars().all()

    result_list = []
    for r in results:
        user_result = await db.execute(select(User).where(User.id == r.user_id))
        u = user_result.scalar_one_or_none()
        result_list.append({
            "ID": r.id,
            "试卷ID": r.exam_id,
            "试卷标题": exam.title,
            "用户ID": r.user_id,
            "用户姓名": u.real_name if u else None,
            "得分": r.score,
            "总分": exam.total_score,
            "及格分": exam.pass_score,
            "状态": r.status,
            "开始时间": str(r.started_at) if r.started_at else None,
            "提交时间": str(r.submitted_at) if r.submitted_at else None,
        })

    return {
        "数据": result_list,
        "共计": len(result_list),
        "labels": {"数据": "data", "共计": "total"}
    }
