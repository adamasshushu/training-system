"""培训任务路由"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.task import TrainingTask, TaskCourse, TaskExam, TaskAssignment
from app.models.course import Course
from app.models.exam import Exam
from app.models.user import User
from app.models.department import Department
from app.utils.auth import get_current_user
from app.schemas.task import (
    TrainingTaskCreate, TrainingTaskUpdate,
    TaskAssignmentCreate, TaskCourseCreate, TaskExamCreate
)

router = APIRouter(prefix="/api/tasks", tags=["培训任务"])


@router.get("")
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """培训任务列表"""
    result = await db.execute(
        select(TrainingTask).order_by(TrainingTask.id.desc())
    )
    tasks = result.scalars().all()
    total = len(tasks)
    start = (page - 1) * page_size
    page_tasks = tasks[start:start + page_size]

    task_list = []
    for t in page_tasks:
        creator_name = None
        if t.created_by:
            u_result = await db.execute(select(User).where(User.id == t.created_by))
            u = u_result.scalar_one_or_none()
            if u:
                creator_name = u.real_name
        course_count_result = await db.execute(
            select(TaskCourse).where(TaskCourse.task_id == t.id)
        )
        exam_count_result = await db.execute(
            select(TaskExam).where(TaskExam.task_id == t.id)
        )
        task_list.append({
            "ID": t.id,
            "标题": t.title,
            "描述": t.description,
            "模式": t.mode,
            "创建人": t.created_by,
            "创建人姓名": creator_name,
            "截止日期": str(t.deadline) if t.deadline else None,
            "是否发布": t.is_published,
            "创建时间": str(t.created_at) if t.created_at else None,
            "课程数量": len(course_count_result.scalars().all()),
            "考试数量": len(exam_count_result.scalars().all()),
        })

    return {
        "数据": task_list,
        "共计": total,
        "页码": page,
        "每页数量": page_size,
        "labels": {"数据": "data", "共计": "total"}
    }


@router.get("/my")
async def list_my_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """我的培训任务（学员端）"""
    # 查找指配给当前用户或用户所在部门的所有任务
    result = await db.execute(
        select(TaskAssignment).where(
            TaskAssignment.assignee_type == "user",
            TaskAssignment.assignee_id == current_user["id"],
        )
    )
    user_assignments = result.scalars().all()

    # 查找用户所在部门的指派
    u_result = await db.execute(
        select(User).where(User.id == current_user["id"])
    )
    user = u_result.scalar_one_or_none()
    dept_assignments = []
    if user and user.department_id:
        result = await db.execute(
            select(TaskAssignment).where(
                TaskAssignment.assignee_type == "department",
                TaskAssignment.assignee_id == user.department_id,
            )
        )
        dept_assignments = result.scalars().all()

    task_ids = set()
    for a in user_assignments + dept_assignments:
        task_ids.add(a.task_id)

    my_tasks = []
    for tid in task_ids:
        t_result = await db.execute(
            select(TrainingTask).where(
                TrainingTask.id == tid,
                TrainingTask.is_published == True,
            )
        )
        t = t_result.scalar_one_or_none()
        if t:
            creator_name = None
            if t.created_by:
                uu = await db.execute(select(User).where(User.id == t.created_by))
                cu = uu.scalar_one_or_none()
                if cu:
                    creator_name = cu.real_name
            my_tasks.append({
                "ID": t.id,
                "标题": t.title,
                "描述": t.description,
                "模式": t.mode,
                "创建人姓名": creator_name,
                "截止日期": str(t.deadline) if t.deadline else None,
                "创建时间": str(t.created_at) if t.created_at else None,
            })

    return {
        "数据": my_tasks,
        "共计": len(my_tasks),
        "labels": {"数据": "data", "共计": "total"}
    }


@router.post("")
async def create_task(
    req: TrainingTaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建培训任务（含关联课程/考试）"""
    if current_user.get("角色") not in ("admin", "teacher"):
        raise HTTPException(status_code=403, detail="无权限创建培训任务")
    task = TrainingTask(
        title=req.标题,
        description=req.描述,
        mode=req.模式,
        created_by=current_user["id"],
        is_published=req.是否发布,
        deadline=req.截止日期,
    )
    db.add(task)
    await db.flush()

    # 关联课程
    for idx, tc in enumerate(req.课程列表):
        c_result = await db.execute(select(Course).where(Course.id == tc.课程ID))
        if not c_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail=f"课程ID {tc.课程ID} 不存在")
        task_course = TaskCourse(
            task_id=task.id,
            course_id=tc.课程ID,
            sort=tc.排序 or idx,
        )
        db.add(task_course)

    # 关联考试
    for idx, te in enumerate(req.考试列表):
        e_result = await db.execute(select(Exam).where(Exam.id == te.考试ID))
        if not e_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail=f"考试ID {te.考试ID} 不存在")
        task_exam = TaskExam(
            task_id=task.id,
            exam_id=te.考试ID,
            sort=te.排序 or idx,
        )
        db.add(task_exam)

    await db.flush()
    return {
        "message": "培训任务创建成功",
        "ID": task.id,
        "标题": task.title,
        "labels": {"message": "消息", "ID": "id", "标题": "title"}
    }


@router.get("/{task_id}")
async def get_task_detail(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """培训任务详情"""
    result = await db.execute(select(TrainingTask).where(TrainingTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    creator_name = None
    if task.created_by:
        u_result = await db.execute(select(User).where(User.id == task.created_by))
        u = u_result.scalar_one_or_none()
        if u:
            creator_name = u.real_name

    # 关联课程
    tc_result = await db.execute(
        select(TaskCourse).where(TaskCourse.task_id == task_id).order_by(TaskCourse.sort)
    )
    courses = []
    for tc in tc_result.scalars().all():
        c_result = await db.execute(select(Course).where(Course.id == tc.course_id))
        c = c_result.scalar_one_or_none()
        if c:
            courses.append({"课程ID": c.id, "标题": c.title})

    # 关联考试
    te_result = await db.execute(
        select(TaskExam).where(TaskExam.task_id == task_id).order_by(TaskExam.sort)
    )
    exams = []
    for te in te_result.scalars().all():
        e_result = await db.execute(select(Exam).where(Exam.id == te.exam_id))
        e = e_result.scalar_one_or_none()
        if e:
            exams.append({"考试ID": e.id, "标题": e.title})

    # 指派记录
    ta_result = await db.execute(
        select(TaskAssignment).where(TaskAssignment.task_id == task_id)
    )
    assignments = []
    for ta in ta_result.scalars().all():
        name = None
        if ta.assignee_type == "user":
            uu = await db.execute(select(User).where(User.id == ta.assignee_id))
            uu_obj = uu.scalar_one_or_none()
            if uu_obj:
                name = uu_obj.real_name
        elif ta.assignee_type == "department":
            dd = await db.execute(select(Department).where(Department.id == ta.assignee_id))
            dd_obj = dd.scalar_one_or_none()
            if dd_obj:
                name = dd_obj.name
        assignments.append({
            "ID": ta.id,
            "指派类型": "用户" if ta.assignee_type == "user" else "部门",
            "指派对象名称": name,
            "创建时间": str(ta.created_at) if ta.created_at else None,
        })

    return {
        "数据": {
            "ID": task.id,
            "标题": task.title,
            "描述": task.description,
            "模式": task.mode,
            "创建人": task.created_by,
            "创建人姓名": creator_name,
            "截止日期": str(task.deadline) if task.deadline else None,
            "是否发布": task.is_published,
            "创建时间": str(task.created_at) if task.created_at else None,
            "关联课程": courses,
            "关联考试": exams,
            "指派记录": assignments,
        },
        "labels": {
            "ID": "id", "标题": "title",
            "关联课程": "courses", "关联考试": "exams",
            "指派记录": "assignments"
        }
    }


@router.put("/{task_id}")
async def update_task(
    task_id: int,
    req: TrainingTaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """更新培训任务"""
    if current_user.get("角色") not in ("admin", "teacher"):
        raise HTTPException(status_code=403, detail="无权限修改任务")
    result = await db.execute(select(TrainingTask).where(TrainingTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    if req.标题 is not None:
        task.title = req.标题
    if req.描述 is not None:
        task.description = req.描述
    if req.模式 is not None:
        task.mode = req.模式
    if req.截止日期 is not None:
        task.deadline = req.截止日期
    if req.是否发布 is not None:
        task.is_published = req.是否发布
    await db.flush()
    return {"message": "任务更新成功", "labels": {"message": "消息"}}


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """删除培训任务"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可删除")
    result = await db.execute(select(TrainingTask).where(TrainingTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    # 先删子记录
    tc_result = await db.execute(select(TaskCourse).where(TaskCourse.task_id == task_id))
    for tc in tc_result.scalars().all():
        await db.delete(tc)
    te_result = await db.execute(select(TaskExam).where(TaskExam.task_id == task_id))
    for te in te_result.scalars().all():
        await db.delete(te)
    ta_result = await db.execute(select(TaskAssignment).where(TaskAssignment.task_id == task_id))
    for ta in ta_result.scalars().all():
        await db.delete(ta)
    await db.delete(task)
    await db.flush()
    return {"message": "任务已删除", "labels": {"message": "消息"}}


@router.delete("/{task_id}/assign/{assignment_id}")
async def remove_assignment(
    task_id: int,
    assignment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """取消指派"""
    if current_user.get("角色") not in ("admin", "teacher"):
        raise HTTPException(status_code=403, detail="无权限")
    result = await db.execute(
        select(TaskAssignment).where(
            TaskAssignment.id == assignment_id,
            TaskAssignment.task_id == task_id
        )
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail="指派记录不存在")
    await db.delete(assignment)
    await db.flush()
    return {"message": "指派已取消", "labels": {"message": "消息"}}


@router.get("/{task_id}/progress")
async def get_task_progress(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取学员在任务中的进度"""
    result = await db.execute(select(TrainingTask).where(TrainingTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 统计课程进度
    tc_result = await db.execute(
        select(TaskCourse).where(TaskCourse.task_id == task_id).order_by(TaskCourse.sort)
    )
    task_courses = tc_result.scalars().all()
    
    course_progress = []
    for tc in task_courses:
        c = (await db.execute(select(Course).where(Course.id == tc.course_id))).scalar_one_or_none()
        if not c:
            continue
        # Count completed lessons
        from app.models.course import CourseProgress, Lesson, Chapter
        total_lessons_result = await db.execute(
            select(Lesson).join(Chapter).where(Chapter.course_id == tc.course_id)
        )
        total_lessons = len(total_lessons_result.scalars().all())
        completed_result = await db.execute(
            select(CourseProgress).where(
                CourseProgress.course_id == tc.course_id,
                CourseProgress.user_id == current_user["id"],
                CourseProgress.completed == True,
            )
        )
        completed = len(completed_result.scalars().all())
        course_progress.append({
            "课程ID": tc.course_id,
            "标题": c.title,
            "总课时": total_lessons,
            "已完成": completed,
            "进度": round(completed / total_lessons * 100, 1) if total_lessons > 0 else 0,
        })

    # 统计考试进度
    te_result = await db.execute(
        select(TaskExam).where(TaskExam.task_id == task_id).order_by(TaskExam.sort)
    )
    task_exams = te_result.scalars().all()
    
    exam_progress = []
    for te in task_exams:
        e = (await db.execute(select(Exam).where(Exam.id == te.exam_id))).scalar_one_or_none()
        if not e:
            continue
        from app.models.exam import ExamResult
        er_result = await db.execute(
            select(ExamResult).where(
                ExamResult.exam_id == te.exam_id,
                ExamResult.user_id == current_user["id"],
                ExamResult.status.in_(["passed", "failed"]),
            ).order_by(ExamResult.submitted_at.desc()).limit(1)
        )
        er = er_result.scalar_one_or_none()
        exam_progress.append({
            "考试ID": te.exam_id,
            "标题": e.title,
            "状态": er.status if er else "pending",
            "得分": er.score if er else None,
            "总分": e.total_score,
        })

    total_items = len(course_progress) + len(exam_progress)
    done_courses = sum(1 for c in course_progress if c["进度"] >= 100)
    done_exams = sum(1 for e in exam_progress if e["状态"] == "passed")
    done = done_courses + done_exams

    return {
        "数据": {
            "任务ID": task.id,
            "任务标题": task.title,
            "总项目数": total_items,
            "已完成数": done,
            "总进度": round(done / total_items * 100, 1) if total_items > 0 else 0,
            "课程进度": course_progress,
            "考试进度": exam_progress,
        },
        "labels": {
            "任务ID": "task_id", "任务标题": "task_title",
            "总项目数": "total_items", "已完成数": "completed_items",
            "总进度": "overall_progress",
            "课程进度": "course_progress", "考试进度": "exam_progress"
        }
    }

@router.post("/{task_id}/assign")
async def assign_task(
    task_id: int,
    req: TaskAssignmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """指派培训任务"""
    if current_user.get("角色") not in ("admin", "teacher"):
        raise HTTPException(status_code=403, detail="无权限指派任务")
    result = await db.execute(select(TrainingTask).where(TrainingTask.id == task_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="任务不存在")
    # 检查指派对象存在
    if req.指派类型 == "user":
        u_result = await db.execute(
            select(User).where(User.id == req.指派对象ID)
        )
        if not u_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="用户不存在")
    elif req.指派类型 == "department":
        d_result = await db.execute(
            select(Department).where(Department.id == req.指派对象ID)
        )
        if not d_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="部门不存在")
    assignment = TaskAssignment(
        task_id=task_id,
        assignee_type=req.指派类型,
        assignee_id=req.指派对象ID,
    )
    db.add(assignment)
    await db.flush()
    return {
        "message": "任务指派成功",
        "ID": assignment.id,
        "labels": {"message": "消息", "ID": "id"}
    }
