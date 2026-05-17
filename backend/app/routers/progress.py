"""学习进度概览路由（管理员查看全员进度）"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func as sa_func
from app.database import get_db
from app.models.user import User
from app.models.department import Department
from app.models.course import Course, CourseProgress, Chapter, Lesson
from app.models.exam import Exam, ExamResult
from app.models.task import TrainingTask, TaskCourse, TaskAssignment
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/progress", tags=["学习进度"])


@router.get("/overview")
async def get_progress_overview(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """管理员端：学习概览统计"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可查看")

    # 用户总数(有效)
    user_result = await db.execute(select(User).where(User.is_active == True))
    total_users = len(user_result.scalars().all())

    # 课程/考试总数
    course_result = await db.execute(select(Course).where(Course.is_published == True))
    total_courses = len(course_result.scalars().all())

    exam_result = await db.execute(select(Exam).where(Exam.is_published == True))
    total_exams = len(exam_result.scalars().all())

    # 学习进度记录数
    progress_result = await db.execute(select(CourseProgress))
    total_progress = len(progress_result.scalars().all())

    # 考试结果数
    exam_result_all = await db.execute(select(ExamResult))
    total_exam_results = len(exam_result_all.scalars().all())

    return {
        "数据": {
            "总员工数": total_users,
            "总课程数": total_courses,
            "总考试数": total_exams,
            "学习记录数": total_progress,
            "考试记录数": total_exam_results,
        },
        "labels": {
            "总员工数": "total_users", "总课程数": "total_courses",
            "总考试数": "total_exams", "学习记录数": "learning_records",
            "考试记录数": "exam_records",
        }
    }


@router.get("/by-department")
async def get_progress_by_department(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """按部门统计学习进度"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可查看")

    dept_result = await db.execute(
        select(Department).where(Department.is_active == True).order_by(Department.sort)
    )
    departments = dept_result.scalars().all()

    dept_stats = []
    # 总课程数
    total_lessons_result = await db.execute(
        select(Lesson).join(Chapter)
    )
    total_lessons = len(total_lessons_result.scalars().all())

    for dept in departments:
        users_in_dept = await db.execute(
            select(User).where(User.department_id == dept.id, User.is_active == True)
        )
        dept_users = users_in_dept.scalars().all()
        user_count = len(dept_users)

        if user_count == 0:
            dept_stats.append({"部门ID": dept.id, "部门名称": dept.name, "员工数": 0, "平均进度": 0})
            continue

        total_progress_sum = 0
        total_progress_count = 0
        for u in dept_users:
            prog_result = await db.execute(
                select(CourseProgress).where(CourseProgress.user_id == u.id)
            )
            user_progresses = prog_result.scalars().all()
            total_progress_sum += sum(p.progress or 0 for p in user_progresses)
            total_progress_count += len(user_progresses)

        avg_progress = round(total_progress_sum / total_progress_count, 1) if total_progress_count > 0 else 0
        dept_stats.append({
            "部门ID": dept.id, "部门名称": dept.name,
            "员工数": user_count, "平均进度": avg_progress,
        })

    return {
        "数据": dept_stats,
        "labels": {"数据": "data"}
    }


@router.get("/course/{course_id}")
async def get_course_progress(
    course_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """查看某门课程的学员学习进度"""
    if current_user.get("角色") not in ("admin", "teacher"):
        raise HTTPException(status_code=403, detail="无权限")

    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")

    # 获取所有学员
    user_result = await db.execute(
        select(User).where(User.is_active == True, User.role == "student").order_by(User.id)
    )
    all_students = user_result.scalars().all()
    total_students = len(all_students)
    start = (page - 1) * page_size
    page_students = all_students[start:start + page_size]

    # 总课时数
    total_lessons_result = await db.execute(
        select(Lesson).join(Chapter).where(Chapter.course_id == course_id)
    )
    total_lessons = len(total_lessons_result.scalars().all())

    student_list = []
    for s in page_students:
        dept_name = None
        if s.department_id:
            dept = (await db.execute(select(Department).where(Department.id == s.department_id))).scalar_one_or_none()
            if dept: dept_name = dept.name

        completed_result = await db.execute(
            select(CourseProgress).where(
                CourseProgress.course_id == course_id,
                CourseProgress.user_id == s.id,
                CourseProgress.completed == True,
            )
        )
        completed = len(completed_result.scalars().all())

        student_list.append({
            "用户ID": s.id, "姓名": s.real_name, "部门": dept_name,
            "总课时": total_lessons, "已完成": completed,
            "进度": round(completed / total_lessons * 100, 1) if total_lessons > 0 else 0,
        })

    return {
        "数据": {
            "课程ID": course_id,
            "课程标题": course.title,
            "学员列表": student_list,
        },
        "共计": total_students, "页码": page, "每页数量": page_size,
        "labels": {"数据": "data", "共计": "total"}
    }
