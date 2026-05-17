"""证书管理路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.certificate import CertificateTemplate, Certificate
from app.models.user import User
from app.models.task import TrainingTask
from app.utils.auth import get_current_user
from app.schemas.certificate import (
    CertificateTemplateCreate, CertificateIssueRequest
)

router = APIRouter(prefix="/api/certificates", tags=["证书管理"])


# ========== 证书模板 ==========

@router.get("/templates")
async def list_templates(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """证书模板列表"""
    result = await db.execute(
        select(CertificateTemplate)
        .where(CertificateTemplate.is_active == True)
        .order_by(CertificateTemplate.id.desc())
    )
    templates = result.scalars().all()
    return {
        "数据": [{
            "ID": t.id,
            "名称": t.name,
            "背景图": t.background,
            "样式配置": t.style_config,
            "是否激活": t.is_active,
            "创建时间": str(t.created_at) if t.created_at else None,
        } for t in templates],
        "共计": len(templates),
        "labels": {"数据": "data", "共计": "total"}
    }


@router.post("/templates")
async def create_template(
    req: CertificateTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建证书模板"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可创建证书模板")
    template = CertificateTemplate(
        name=req.名称,
        background=req.背景图,
        style_config=req.样式配置,
    )
    db.add(template)
    await db.flush()
    return {
        "message": "证书模板创建成功",
        "ID": template.id,
        "名称": template.name,
        "labels": {"message": "消息", "ID": "id", "名称": "name"}
    }


@router.put("/templates/{template_id}")
async def update_template(
    template_id: int,
    req: CertificateTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """更新证书模板"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员")
    result = await db.execute(select(CertificateTemplate).where(CertificateTemplate.id == template_id))
    tpl = result.scalar_one_or_none()
    if not tpl:
        raise HTTPException(status_code=404, detail="模板不存在")
    if req.名称 is not None: tpl.name = req.名称
    if req.背景图 is not None: tpl.background = req.背景图
    if req.样式配置 is not None: tpl.style_config = req.样式配置
    await db.flush()
    return {"message": "模板更新成功", "labels": {"message": "消息"}}


@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """删除证书模板"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员")
    result = await db.execute(select(CertificateTemplate).where(CertificateTemplate.id == template_id))
    tpl = result.scalar_one_or_none()
    if not tpl:
        raise HTTPException(status_code=404, detail="模板不存在")
    tpl.is_active = False
    await db.flush()
    return {"message": "模板已停用", "labels": {"message": "消息"}}


@router.get("/my")
async def list_my_certificates(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """学员查看自己的证书"""
    result = await db.execute(
        select(Certificate).where(Certificate.user_id == current_user["id"]).order_by(Certificate.id.desc())
    )
    certs = result.scalars().all()
    cert_list = []
    for c in certs:
        tpl_name = None
        if c.template_id:
            tr = await db.execute(select(CertificateTemplate).where(CertificateTemplate.id == c.template_id))
            t = tr.scalar_one_or_none()
            if t: tpl_name = t.name
        cert_list.append({
            "ID": c.id, "证书编号": c.cert_number,
            "持证人姓名": c.user_name, "模板名称": tpl_name,
            "发放时间": str(c.issued_at) if c.issued_at else None,
        })
    return {"数据": cert_list, "共计": len(cert_list), "labels": {"数据": "data", "共计": "total"}}


# ========== 看板统计 ==========

@router.get("/stats")
async def dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """系统看板数据"""
    from app.models.department import Department
    from app.models.course import Course
    from app.models.exam import Exam, ExamResult
    
    # 员工数
    ur = await db.execute(select(User).where(User.is_active == True))
    user_count = len(ur.scalars().all())
    dept_r = await db.execute(select(Department).where(Department.is_active == True))
    dept_count = len(dept_r.scalars().all())
    
    # 课程数
    cr = await db.execute(select(Course))
    course_count = len(cr.scalars().all())
    
    # 考试
    er = await db.execute(select(Exam))
    exam_count = len(er.scalars().all())
    exr = await db.execute(select(ExamResult))
    results = exr.scalars().all()
    passed = sum(1 for r in results if r.status == "passed")
    
    # 证书数
    cert_r = await db.execute(select(Certificate))
    cert_count = len(cert_r.scalars().all())
    
    # 任务数
    task_r = await db.execute(select(TrainingTask))
    task_count = len(task_r.scalars().all())
    
    return {
        "数据": {
            "部门数量": dept_count,
            "员工数量": user_count,
            "课程数量": course_count,
            "考试数量": exam_count,
            "考试通过次数": passed,
            "证书数量": cert_count,
            "任务数量": task_count,
        },
        "labels": {
            "部门数量": "department_count", "员工数量": "user_count",
            "课程数量": "course_count", "考试数量": "exam_count",
            "考试通过次数": "exam_passed", "证书数量": "certificate_count",
            "任务数量": "task_count"
        }
    }

@router.get("")
async def list_certificates(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """证书列表"""
    result = await db.execute(
        select(Certificate).order_by(Certificate.id.desc())
    )
    certificates = result.scalars().all()
    cert_list = []
    for c in certificates:
        user_name = None
        if c.user_id:
            u_result = await db.execute(select(User).where(User.id == c.user_id))
            u = u_result.scalar_one_or_none()
            if u:
                user_name = u.real_name
        template_name = None
        if c.template_id:
            t_result = await db.execute(
                select(CertificateTemplate).where(CertificateTemplate.id == c.template_id)
            )
            tpl = t_result.scalar_one_or_none()
            if tpl:
                template_name = tpl.name
        cert_list.append({
            "ID": c.id,
            "用户ID": c.user_id,
            "用户姓名": user_name or c.user_name,
            "模板ID": c.template_id,
            "模板名称": template_name,
            "任务ID": c.task_id,
            "证书编号": c.cert_number,
            "持证人姓名": c.user_name,
            "发放时间": str(c.issued_at) if c.issued_at else None,
        })
    return {
        "数据": cert_list,
        "共计": len(cert_list),
        "labels": {"数据": "data", "共计": "total"}
    }


@router.post("/issue")
async def issue_certificate(
    req: CertificateIssueRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """发放证书"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可发放证书")
    # 验证用户
    u_result = await db.execute(select(User).where(User.id == req.用户ID))
    u = u_result.scalar_one_or_none()
    if not u:
        raise HTTPException(status_code=404, detail="用户不存在")
    # 验证模板
    if req.模板ID:
        t_result = await db.execute(
            select(CertificateTemplate).where(CertificateTemplate.id == req.模板ID)
        )
        if not t_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="证书模板不存在")
    # 验证任务
    if req.任务ID:
        tk_result = await db.execute(
            select(TrainingTask).where(TrainingTask.id == req.任务ID)
        )
        if not tk_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="培训任务不存在")
    cert = Certificate(
        user_id=req.用户ID,
        template_id=req.模板ID,
        task_id=req.任务ID,
        cert_number=req.证书编号 or f"CERT-{u.id}-{u.username.upper()}",
        user_name=req.持证人姓名 or u.real_name,
    )
    db.add(cert)
    await db.flush()
    return {
        "message": "证书发放成功",
        "ID": cert.id,
        "证书编号": cert.cert_number,
        "labels": {"message": "消息", "ID": "id", "证书编号": "cert_number"}
    }
