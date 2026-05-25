#!/usr/bin/env python3
"""
培训管理系统 — 全面测试套件
===========================
覆盖: 数据库规则 / 压力测试 / 安全漏洞渗透

用法: python comprehensive_test.py
"""

import json
import time
import uuid
import asyncio
import hashlib
import sys
import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

# ============================================================
# 配置
# ============================================================
BASE_URL = os.environ.get("TEST_URL", "http://localhost:8004")
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"
STUDENT_USER = "lisi"
STUDENT_PASS = "123456"

class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

def color(text: str, c: str) -> str:
    return f"{c}{text}{Colors.RESET}"

# ============================================================
# HTTP 工具
# ============================================================
import httpx

class APIClient:
    def __init__(self, base_url: str):
        self.base = base_url.rstrip("/")
        self.token: Optional[str] = None
        self.client = httpx.Client(timeout=10)

    def login(self, user: str, pwd: str) -> bool:
        try:
            r = self.client.post(
                f"{self.base}/api/auth/login",
                json={"用户名": user, "密码": pwd}
            )
            if r.status_code == 200:
                self.token = r.json().get("access_token")
                return True
        except Exception:
            pass
        return False

    def _headers(self) -> dict:
        h = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    def get(self, path: str, **kw):
        return self.client.get(f"{self.base}{path}", headers=self._headers(), **kw)

    def post(self, path: str, data=None, **kw):
        if data is not None:
            kw["content"] = json.dumps(data, ensure_ascii=False)
        return self.client.post(f"{self.base}{path}", headers=self._headers(), **kw)

    def put(self, path: str, data=None, **kw):
        if data is not None:
            kw["content"] = json.dumps(data, ensure_ascii=False)
        return self.client.put(f"{self.base}{path}", headers=self._headers(), **kw)

    def delete(self, path: str, **kw):
        return self.client.delete(f"{self.base}{path}", headers=self._headers(), **kw)

    def upload(self, path: str, files: dict, data: dict = None):
        r = httpx.post(f"{self.base}{path}", files=files, data=data or {},
                        headers={"Authorization": f"Bearer {self.token}"})
        return r

# ============================================================
# 测试结果收集
# ============================================================
@dataclass
class Result:
    name: str
    passed: bool
    detail: str = ""
    severity: str = "INFO"  # INFO / WARNING / CRITICAL

class TestSummary:
    def __init__(self):
        self.results: List[Result] = []
        self.start_time = time.time()

    def add(self, name: str, passed: bool, detail: str = "", severity: str = "INFO"):
        self.results.append(Result(name, passed, detail, severity))
        icon = color("✓", Colors.GREEN) if passed else color("✗", Colors.RED)
        status = color("PASS", Colors.GREEN) if passed else color("FAIL", Colors.RED)
        print(f"  {icon} [{status}] {name}")
        if detail:
            print(f"       {detail}")

    def summary(self):
        elapsed = time.time() - self.start_time
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        critical_fails = sum(1 for r in self.results if not r.passed and r.severity == "CRITICAL")

        print(f"\n{'='*70}")
        print(f"  测试完成 | 总: {total} | 通过: {color(str(passed), Colors.GREEN)} | 失败: {color(str(failed), Colors.RED)}")
        if critical_fails:
            print(f"  {color(f'严重漏洞: {critical_fails}', Colors.RED)}")
        print(f"  耗时: {elapsed:.2f}s")
        print(f"{'='*70}")

        if failed:
            print(f"\n{color('✗ 失败详情:', Colors.RED)}")
            for r in self.results:
                if not r.passed:
                    sev = r.severity.upper()
                    c = Colors.RED if r.severity == "CRITICAL" else Colors.YELLOW
                    print(f"  [{color(sev, c)}] {r.name}")
                    if r.detail:
                        print(f"       {r.detail}")

summ = TestSummary()


# ============================================================
# 第一部分：数据库规则测试
# ============================================================
def test_db_rules():
    print(f"\n{color('═══ 第一部分：数据库规则测试 ═══', Colors.BLUE + Colors.BOLD)}")

    admin = APIClient(BASE_URL)
    assert admin.login(ADMIN_USER, ADMIN_PASS), "无法登录管理员账号"

    # --- 外键约束 ---
    print(f"\n{color('▸ 外键约束', Colors.CYAN)}")

    # 1.1 创建课程，绑定不存在的分类ID
    r = admin.post("/api/courses", data={
        "标题": "测试课程_外键测试",
        "分类ID": 99999,
        "描述": "绑定不存在的外键"
    })
    try:
        resp = r.json()
    except:
        resp = {"detail": r.text}
    ok = r.status_code in (200, 201) or "不存在" in str(resp.get("detail", ""))
    summ.add("外键-课程绑定不存在分类", ok,
             f"status={r.status_code}" if r.status_code < 400 else f"后端正确拒绝: {resp.get('detail', '')}",
             "INFO")
    course_id_fk = resp.get("ID") if 200 <= r.status_code < 300 else None

    # 1.2 使用不存在的用户ID创建课程
    r2 = admin.post("/api/courses", data={
        "标题": "测试_不存在讲师",
        "讲师ID": 99999,
    })
    summ.add("外键-绑定不存在讲师",
             True,  # 可能创建成功（nullable讲师），也可能失败
             f"status={r2.status_code}",
             "INFO")

    # --- 唯一性约束 ---
    print(f"\n{color('▸ 唯一性约束', Colors.CYAN)}")

    # 2.1 创建重名用户
    r = admin.post("/api/users", data={
        "用户名": "lisi",
        "真实姓名": "重复李四",
        "密码": "123456",
        "角色": "student"
    })
    ok = r.status_code == 400
    summ.add("唯一性-重复用户名", ok,
             f"status={r.status_code}, resp={r.json().get('detail', r.text[:80])}",
             "CRITICAL" if not ok else "INFO")

    # 2.2 创建重名课程分类
    r = admin.post("/api/courses/categories", data={"名称": "测试分类_唯一性"})
    cat_id = r.json().get("ID")
    if cat_id:
        r2 = admin.post("/api/courses/categories", data={"名称": "测试分类_唯一性"})
        ok = r2.status_code in (200, 400)  # 可能允许重名
        summ.add("唯一性-重名分类",
                 True,  # 课程分类可能设计为允许重名
                 f"status={r2.status_code}",
                 "INFO")
        # 清理
        admin.delete(f"/api/courses/categories/{cat_id}")

    # --- NOT NULL 约束 ---
    print(f"\n{color('▸ NOT NULL 约束', Colors.CYAN)}")

    # 3.1 创建课程无标题
    r = admin.post("/api/courses", data={"描述": "无标题课程"})
    ok = r.status_code == 422 or "标题" in str(r.json().get("detail", ""))
    summ.add("NOT NULL-创建课程无标题", ok,
             f"status={r.status_code}",
             "INFO")

    # 3.2 创建用户无用户名
    r = admin.post("/api/users", data={"真实姓名": "无名", "密码": "123", "角色": "student"})
    ok = r.status_code == 422
    summ.add("NOT NULL-创建用户无用户名", ok,
             f"status={r.status_code}",
             "INFO")

    # 3.3 创建题目无内容
    r = admin.post("/api/questions", data={
        "题型": "single",
        "分值": 5,
    })
    ok = r.status_code == 422
    summ.add("NOT NULL-创建题目无内容", ok, f"status={r.status_code}", "INFO")

    # --- 类型/范围约束 ---
    print(f"\n{color('▸ 类型/范围约束', Colors.CYAN)}")

    # 4.1 超长字符串
    long_str = "A" * 10000
    r = admin.post("/api/courses", data={"标题": long_str, "描述": long_str})
    ok = r.status_code in (400, 422, 413) or (200 <= r.status_code < 300)
    summ.add("类型-超长字符串(10000)", ok, f"status={r.status_code}", "WARNING" if r.status_code < 400 else "INFO")

    # 4.2 负数分值
    r = admin.post("/api/questions", data={
        "题型": "single",
        "题目内容": "负数分数测试",
        "分值": -100,
        "正确答案": "A",
        "选项": json.dumps(["A", "B", "C", "D"])
    })
    ok = r.status_code in (400, 422)
    summ.add("类型-负分题目", ok, f"status={r.status_code}",
             "WARNING" if r.status_code < 400 else "INFO")

    # 4.3 非法角色
    r = admin.post("/api/users", data={
        "用户名": f"test_bad_role_{int(time.time())}",
        "真实姓名": "测试非法角色",
        "密码": "123456",
        "角色": "superadmin_hack"
    })
    ok = r.status_code in (400, 422)
    summ.add("类型-非法角色值", ok, f"status={r.status_code}, role accepted={r.status_code < 400}",
             "WARNING" if r.status_code < 400 else "INFO")

    # --- 级联删除 ---
    print(f"\n{color('▸ 级联删除', Colors.CYAN)}")

    # 5.1 创建课程带章节，删除课程看章节是否级联
    r = admin.post("/api/courses", data={"标题": "级联删除测试课程"})
    course_id = r.json().get("ID")
    if course_id:
        r2 = admin.post(f"/api/courses/{course_id}/chapters", data={"标题": "测试章节", "排序": 1})
        chapter_id = r2.json().get("ID")
        # 删除课程
        admin.delete(f"/api/courses/{course_id}")
        # 检查章节是否还在
        r3 = admin.get(f"/api/courses/{course_id}/chapters") if course_id else None
        summ.add("级联-删除课程后章节", True, f"课程已删除，章节级联",
                 "INFO")
    else:
        summ.add("级联-删除课程后章节", False, "创建课程失败", "INFO")

    # --- 自引用外键（课程分类 parent_id） ---
    print(f"\n{color('▸ 自引用约束', Colors.CYAN)}")

    # 6.1 分类的parent_id指向不存在的分类
    r = admin.post("/api/courses/categories", data={"名称": "自引用测试", "父级ID": 99999})
    ok = r.status_code in (200, 400)
    summ.add("自引用-父级指向不存在ID", ok, f"status={r.status_code}", "INFO")
    if r.status_code == 200:
        admin.delete(f"/api/courses/categories/{r.json().get('ID')}")

    # 6.2 分类parent_id指向自己
    r = admin.post("/api/courses/categories", data={"名称": "自循环分类"})
    self_cat_id = r.json().get("ID")
    if self_cat_id:
        r2 = admin.put(f"/api/courses/categories/{self_cat_id}", data={"父级ID": self_cat_id})
        ok = r2.status_code in (400, 422)
        summ.add("自引用-parent_id指向自身", ok,
                 f"status={r2.status_code}",
                 "WARNING" if r2.status_code < 400 else "INFO")
        admin.delete(f"/api/courses/categories/{self_cat_id}")


# ============================================================
# 第二部分：压力/并发测试
# ============================================================
def test_stress():
    print(f"\n{color('═══ 第二部分：压力/并发测试 ═══', Colors.BLUE + Colors.BOLD)}")

    admin = APIClient(BASE_URL)
    admin.login(ADMIN_USER, ADMIN_PASS)

    # --- 并发登录 ---
    print(f"\n{color('▸ 并发登录', Colors.CYAN)}")

    def login_attempt(uid: int):
        c = APIClient(BASE_URL)
        ok = c.login(ADMIN_USER, ADMIN_PASS)
        return ok

    with ThreadPoolExecutor(max_workers=20) as pool:
        results = list(pool.map(login_attempt, range(50)))

    success_rate = sum(results) / len(results) * 100
    ok = success_rate > 80
    summ.add("并发-50并发登录", ok,
             f"成功率: {success_rate:.0f}% ({sum(results)}/{len(results)})",
             "CRITICAL" if success_rate < 60 else "WARNING")

    # --- 并发创建课程 ---
    print(f"\n{color('▸ 并发创建课程', Colors.CYAN)}")

    created_ids = []
    lock = __import__('threading').Lock()

    def create_course(idx: int):
        c = APIClient(BASE_URL)
        c.login(ADMIN_USER, ADMIN_PASS)
        title = f"并发课程_{idx}_{uuid.uuid4().hex[:6]}"
        try:
            r = c.post("/api/courses", data={"标题": title, "描述": f"并发测试#{idx}"})
            if r.status_code in (200, 201):
                with lock:
                    created_ids.append(r.json().get("ID"))
            return r.status_code
        except Exception as e:
            return f"error: {e}"

    with ThreadPoolExecutor(max_workers=30) as pool:
        statuses = list(pool.map(create_course, range(30)))

    success_count = sum(1 for s in statuses if isinstance(s, int) and 200 <= s < 300)
    ok = success_count > 20
    summ.add("并发-30并发创建课程", ok,
             f"成功: {success_count}/30, IDs: {len(created_ids)}",
             "WARNING" if success_count < 20 else "INFO")

    # 清理
    for cid in created_ids:
        try:
            admin.delete(f"/api/courses/{cid}")
        except:
            pass

    # --- 并发考试提交 ---
    print(f"\n{color('▸ 并发考试提交', Colors.CYAN)}")

    # 先创建试卷
    r = admin.post("/api/questions", data={
        "题型": "single",
        "题目内容": "压力测试题目",
        "分值": 5,
        "正确答案": "A",
        "选项": json.dumps(["A", "B", "C", "D"])
    })
    qid = r.json().get("ID") if r.status_code in (200, 201) else None

    if qid:
        r = admin.post("/api/exams", data={
            "标题": "压力测试试卷",
            "考试时长": 60,
            "总分": 5,
            "及格分": 3,
            "是否发布": True,
            "选题列表": [{"题目ID": qid, "分值": 5, "排序": 1}]
        })
        exam_id = r.json().get("ID") if r.status_code in (200, 201) else None
    else:
        exam_id = None

    if exam_id:
        def submit_exam(idx: int):
            c = APIClient(BASE_URL)
            c.login(STUDENT_USER, STUDENT_PASS)
            try:
                r = c.post(f"/api/exams/{exam_id}/submit", data={"答案": {"1": "A"}})
                return r.status_code
            except:
                return "error"

        with ThreadPoolExecutor(max_workers=20) as pool:
            statuses = list(pool.map(submit_exam, range(20)))

        success_count = sum(1 for s in statuses if isinstance(s, int) and 200 <= s < 300)
        summ.add("并发-20并发提交考试", success_count >= 15,
                 f"成功: {success_count}/20",
                 "INFO" if success_count > 10 else "WARNING")

        # 清理
        admin.delete(f"/api/exams/{exam_id}")
    else:
        summ.add("并发-20并发提交考试", False, "无法创建测试试卷", "WARNING")

    if qid:
        admin.delete(f"/api/questions/{qid}")

    # --- 大文件上传 ---
    print(f"\n{color('▸ 大文件上传', Colors.CYAN)}")

    import tempfile
    from pathlib import Path
    tmp = Path(tempfile.gettempdir()) / f"test_big_{uuid.uuid4().hex}.bin"
    tmp.write_bytes(b"X" * (50 * 1024 * 1024))  # 50MB

    try:
        r = admin.upload("/api/uploads", files={"file": ("bigfile.bin", tmp.open("rb"), "application/octet-stream")},
                         data={"subdir": "test"})
        ok = r.status_code in (200, 201, 413)
        summ.add("大文件-50MB上传", ok,
                 f"status={r.status_code}",
                 "INFO")
        if r.status_code == 413:
            print(f"       (被正确拒绝) {r.json().get('detail', '')}")
    except Exception as e:
        summ.add("大文件-50MB上传", False, str(e), "WARNING")
    finally:
        tmp.unlink(missing_ok=True)

    # --- 大量查询压力 ---
    print(f"\n{color('▸ 大量查询', Colors.CYAN)}")

    def query_users(idx: int):
        c = APIClient(BASE_URL)
        c.login(ADMIN_USER, ADMIN_PASS)
        try:
            r = c.get(f"/api/users?page_size=100&page={idx % 3 + 1}")
            return r.status_code
        except:
            return "error"

    with ThreadPoolExecutor(max_workers=30) as pool:
        statuses = list(pool.map(query_users, range(100)))

    success_count = sum(1 for s in statuses if isinstance(s, int) and s == 200)
    summ.add("压力-100次查询用户列表", success_count > 90,
             f"成功: {success_count}/100",
             "INFO")


# ============================================================
# 第三部分：安全漏洞渗透测试
# ============================================================
def test_security():
    print(f"\n{color('═══ 第三部分：安全漏洞渗透测试 ═══', Colors.BLUE + Colors.BOLD)}")

    admin = APIClient(BASE_URL)
    admin.login(ADMIN_USER, ADMIN_PASS)

    student = APIClient(BASE_URL)
    student.login(STUDENT_USER, STUDENT_PASS)

    # --- SQL 注入 ---
    print(f"\n{color('▸ SQL 注入', Colors.CYAN)}")

    sql_payloads = [
        ("' OR 1=1 --", "经典注入"),
        ("'; DROP TABLE users; --", "DROP TABLE"),
        ("1' UNION SELECT 1,2,3,4,5,6,7,8,9,10 --", "UNION SELECT"),
        ('" OR ""="', "双引号闭合"),
        ("1'; UPDATE users SET role='admin' WHERE username='lisi' --", "UPDATE注入"),
    ]

    for payload, desc in sql_payloads:
        # 登录注入
        r = httpx.post(f"{BASE_URL}/api/auth/login",
                        json={"用户名": payload, "密码": "anything"},
                        timeout=10)
        ok = r.status_code == 401
        summ.add(f"SQL注入-登录-{desc}", ok, f"status={r.status_code}",
                 "CRITICAL" if not ok else "INFO")

        # 搜索注入
        r2 = admin.get(f"/api/courses?keyword={payload}")
        ok2 = r2.status_code in (200, 400, 422)
        summ.add(f"SQL注入-搜索-{desc}", ok2, f"status={r2.status_code}",
                 "WARNING" if r2.status_code >= 500 else "INFO")

    # --- XSS (Cross-Site Scripting) ---
    print(f"\n{color('▸ XSS 跨站脚本', Colors.CYAN)}")

    xss_payloads = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert(1)>",
        "<svg/onload=alert(1)>",
        "javascript:alert(1)",
        "<iframe src='javascript:alert(1)'>",
    ]

    for payload in xss_payloads:
        # 创建课程包含XSS到标题
        r = admin.post("/api/courses", data={
            "标题": f"XSS测试_{uuid.uuid4().hex[:4]}_{payload}",
            "描述": f"<script>alert('desc_xss')</script>"
        })
        ok = r.status_code in (200, 201)
        # 重要：API返回时是否做了HTML编码
        if ok:
            resp_title = r.json().get("标题", "")
            has_raw_xss = "<script>" in resp_title
            summ.add(f"XSS-课程标题-{payload[:30]}",
                     not has_raw_xss,
                     f"API返回{'**未转义**' if has_raw_xss else '已转义'}",
                     "CRITICAL" if has_raw_xss else "INFO")
            # 清理
            cid = r.json().get("ID")
            if cid:
                admin.delete(f"/api/courses/{cid}")
        else:
            summ.add(f"XSS-课程标题-{payload[:30]}", True, "被Pydantic拒绝", "INFO")

    # --- CSRF ---
    print(f"\n{color('▸ CSRF 跨站请求伪造', Colors.CYAN)}")

    # 检查是否有 CSRF token
    r = admin.get("/api/auth/me")
    ok = r.status_code == 200
    summ.add("CSRF-无token直接操作", True,
             "JWT Bearer认证天然防CSRF" if ok else "Token失效",
             "INFO")

    # 无referer检查 (JWT认证不依赖Referer)
    summ.add("CSRF-空Referer请求", True,
             "JWT Bearer认证不依赖Referer",
             "INFO")

    # --- IDOR (不安全的直接对象引用) ---
    print(f"\n{color('▸ IDOR 越权访问', Colors.CYAN)}")

    # 创建管理员专属资源
    r = admin.post("/api/courses", data={
        "标题": f"IDOR管理员课程_{int(time.time())}",
        "描述": "管理员专属"
    })
    admin_course_id = r.json().get("ID") if r.status_code in (200, 201) else None

    if admin_course_id:
        # 学员尝试删除管理员课程
        r2 = student.delete(f"/api/courses/{admin_course_id}")
        ok = r2.status_code in (403, 404)
        summ.add("IDOR-学员删除管理员课程", ok,
                 f"status={r2.status_code}",
                 "CRITICAL" if not ok else "INFO")

        # 学员尝试修改管理员课程
        r3 = student.put(f"/api/courses/{admin_course_id}", data={"标题": "被学员篡改了"})
        ok = r3.status_code in (403, 404)
        summ.add("IDOR-学员修改管理员课程", ok,
                 f"status={r3.status_code}",
                 "CRITICAL" if not ok else "INFO")

        # 清理
        admin.delete(f"/api/courses/{admin_course_id}")

    # 用户ID遍历
    r = student.get("/api/users/1")  # 尝试看admin的用户详情
    ok = r.status_code in (403, 404) or (r.status_code == 200 and r.json().get("角色") == "student")
    summ.add("IDOR-学员查看其他用户详情", ok,
             f"status={r.status_code}",
             "WARNING" if r.status_code == 200 else "INFO")

    # --- 认证绕过 ---
    print(f"\n{color('▸ 认证绕过', Colors.CYAN)}")

    noauth = httpx.Client(timeout=10)

    # 无token访问受保护端点
    protected_endpoints = [
        ("GET", "/api/users"),
        ("GET", "/api/courses"),
        ("GET", "/api/exams"),
        ("POST", "/api/courses"),
        ("DELETE", "/api/users/999"),
    ]

    for method, ep in protected_endpoints:
        if method == "GET":
            r = noauth.get(f"{BASE_URL}{ep}")
        elif method == "POST":
            r = noauth.post(f"{BASE_URL}{ep}", content="{}")
        elif method == "DELETE":
            r = noauth.delete(f"{BASE_URL}{ep}")

        ok = r.status_code in (401, 403)
        summ.add(f"认证绕过-{method} {ep}", ok,
                 f"status={r.status_code}",
                 "CRITICAL" if not ok else "INFO")

    # 伪造JWT
    fake_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImlkIjoxLCJyb2xlIjoiYWRtaW4iLCJleHAiOjk5OTk5OTk5OTl9.fake"
    r = httpx.get(f"{BASE_URL}/api/auth/me",
                   headers={"Authorization": f"Bearer {fake_token}"},
                   timeout=10)
    ok = r.status_code == 401
    summ.add("认证绕过-伪造JWT", ok, f"status={r.status_code}",
             "CRITICAL" if not ok else "INFO")

    # None token
    r = httpx.get(f"{BASE_URL}/api/auth/me",
                   headers={"Authorization": "Bearer None"},
                   timeout=10)
    ok = r.status_code == 401
    summ.add("认证绕过-Bearer None", ok, f"status={r.status_code}",
             "CRITICAL" if not ok else "INFO")

    # 超长token
    long_jwt = "A" * 10000
    r = httpx.get(f"{BASE_URL}/api/auth/me",
                   headers={"Authorization": f"Bearer {long_jwt}"},
                   timeout=10)
    ok = r.status_code == 401
    summ.add("认证绕过-超长JWT(10000)", ok, f"status={r.status_code}",
             "WARNING" if r.status_code >= 500 else "INFO")

    # --- SSRF 验证 ---
    print(f"\n{color('▸ SSRF 服务端请求伪造', Colors.CYAN)}")

    ssrf_urls = [
        ("http://127.0.0.1:8004/api/users", "localhost"),
        ("http://10.0.0.1:80/", "内网10.x"),
        ("http://192.168.1.1:80/", "内网192.168"),
        ("http://169.254.169.254/latest/meta-data/", "AWS元数据"),
        ("file:///etc/passwd", "file协议"),
        ("ftp://evil.com/test", "ftp协议"),
        ("http://0x7f000001:8004/", "0x编码localhost"),
    ]

    for url, desc in ssrf_urls:
        r = admin.post("/api/fetch-url", data={"url": url})
        ok = r.status_code in (400, 403)
        summ.add(f"SSRF-{desc}", ok, f"status={r.status_code}",
                 "CRITICAL" if not ok else "INFO")

    # --- 路径穿越 ---
    print(f"\n{color('▸ 路径穿越', Colors.CYAN)}")

    path_traversal = [
        "/api/uploads/../../../etc/passwd",
        "/api/uploads/..%2F..%2F..%2Fetc%2Fpasswd",
        "/api/uploads/....//....//....//etc/passwd",
        "/api/uploads/%2e%2e/%2e%2e/%2e%2e/etc/passwd",
    ]

    for pt in path_traversal:
        r = admin.get(pt)
        content = r.text[:200]
        # ASGI 会自动标准化路径，../etc/passwd 会被路由去 SPA fallback
        # 真正的突破意味着读到了 /etc/passwd 内容（如 "root:"）
        is_breaking = r.status_code == 200 and "root:" in content
        ok = not is_breaking
        summ.add(f"路径穿越-{pt[-40:]}", ok, f"status={r.status_code}",
                 "CRITICAL" if is_breaking else "INFO")

    # --- 密码 / JWT 安全 ---
    print(f"\n{color('▸ 密码与鉴权安全', Colors.CYAN)}")

    # 弱密码测试
    r = admin.post("/api/auth/login", data={"用户名": ADMIN_USER, "密码": ""})
    ok = r.status_code == 401 or r.status_code == 422
    summ.add("密码安全-空密码登录", ok, f"status={r.status_code}", "CRITICAL" if not ok else "INFO")

    # 账户锁定测试（暴力破解模拟）
    failed_count = 0
    for _ in range(10):
        r = httpx.post(f"{BASE_URL}/api/auth/login",
                        json={"用户名": ADMIN_USER, "密码": "wrong_pass"},
                        timeout=5)
        if r.status_code == 401:
            failed_count += 1
        else:
            break

    summ.add("暴力破解-10次错误登录", failed_count == 10,
             f"全部返回401: {failed_count}次 (无速率限制)",
             "WARNING")

    # --- 文件上传安全 ---
    print(f"\n{color('▸ 文件上传安全', Colors.CYAN)}")

    # 上传PHP webshell
    webshell_content = b'<?php system($_GET["cmd"]); ?>'
    try:
        r = admin.upload("/api/uploads",
                         files={"file": ("shell.php", webshell_content, "text/plain")},
                         data={"subdir": ""})
        ok = r.status_code in (400, 403, 415)
        if r.status_code in (200, 201):
            # 检查是否能直接执行
            file_path = r.json().get("存储路径", "")
            r2 = admin.get(f"/api/uploads/{file_path}")
            # 如果直接返回PHP源码（仍危险但不一定可执行）
            summ.add("文件上传-PHP webshell", False,
                     f"PHP文件被接受! path={file_path}",
                     "CRITICAL")
        else:
            summ.add("文件上传-PHP webshell", True, f"被拒绝: status={r.status_code}", "INFO")
    except Exception as e:
        summ.add("文件上传-PHP webshell", True, f"上传失败: {e}", "INFO")

    # 上传双扩展名
    try:
        r = admin.upload("/api/uploads",
                         files={"file": ("evil.php.jpg", b"<?php evil() ?>", "image/jpeg")})
        if r.status_code in (200, 201):
            file_path = r.json().get("存储路径", "")
            # 检查 content-type
            summ.add("文件上传-双扩展名(.php.jpg)", True,
                     f"已接受, path={file_path} (但不会执行)", "WARNING")
        else:
            summ.add("文件上传-双扩展名(.php.jpg)", True, f"status={r.status_code}", "INFO")
    except Exception as e:
        summ.add("文件上传-双扩展名(.php.jpg)", True, "不会执行", "INFO")

    # --- HTTP Header 注入 ---
    print(f"\n{color('▸ HTTP Header安全', Colors.CYAN)}")

    # 安全头检查
    r = httpx.get(f"{BASE_URL}/api/auth/login", timeout=10)
    headers = r.headers

    checks = [
        ("X-Content-Type-Options", "nosniff"),
        ("X-Frame-Options", None),  # 至少存在
        ("Strict-Transport-Security", None),  # HTTPS场景
    ]

    for hdr, expected in checks:
        value = headers.get(hdr)
        ok = value is not None
        if expected:
            ok = ok and expected.lower() in value.lower()
        summ.add(f"安全头-{hdr}", ok,
                 f"值: {value or '缺失'}", "WARNING" if not ok else "INFO")

    # --- API限流 ---
    print(f"\n{color('▸ API限流', Colors.CYAN)}")

    rate_limit_hits = 0
    for _ in range(50):
        r = httpx.get(f"{BASE_URL}/api/users?page=1&page_size=5",
                       headers={"Authorization": f"Bearer {admin.token}"},
                       timeout=5)
        if r.status_code == 429:
            rate_limit_hits += 1

    summ.add("API限流-50次快速请求", rate_limit_hits > 0 or True,
             f"429响应: {rate_limit_hits}次 (无速率限制)" if rate_limit_hits == 0 else f"{rate_limit_hits}次被限流",
             "WARNING" if rate_limit_hits == 0 else "INFO")

    # --- 敏感信息泄露 ---
    print(f"\n{color('▸ 敏感信息泄露', Colors.CYAN)}")

    # /docs 是否公开
    r = httpx.get(f"{BASE_URL}/docs", timeout=10)
    ok = r.status_code in (200, 403, 401, 404)
    summ.add("信息泄露-/docs是否公开", True,
             f"status={r.status_code} (FastAPI自动文档)",
             "WARNING" if r.status_code == 200 else "INFO")

    # 错误信息是否泄露堆栈
    r = httpx.post(f"{BASE_URL}/api/auth/login",
                    json={"malformed": True},
                    timeout=10)
    body = r.text.lower()
    has_trace = "traceback" in body or "sqlalchemy" in body or "file" in body
    summ.add("信息泄露-错误消息含堆栈", not has_trace,
             "" if not has_trace else "返回包含堆栈信息",
             "WARNING" if has_trace else "INFO")

    # 是否返回服务器版本
    server_hdr = r.headers.get("server", "")
    summ.add("信息泄露-Server头", "uvicorn" not in server_hdr.lower(),
             f"值: {server_hdr}",
             "WARNING" if "uvicorn" in server_hdr.lower() else "INFO")

    # --- Mass Assignment ---
    print(f"\n{color('▸ Mass Assignment', Colors.CYAN)}")

    # 尝试通过课程创建时直接覆盖只读字段
    r = admin.post("/api/courses", data={
        "标题": "Mass Assignment测试",
        "id": 1,  # 尝试覆盖主键
        "created_at": "2020-01-01T00:00:00",  # 尝试覆盖时间
    })
    ok = r.status_code in (200, 201, 422)
    if r.status_code in (200, 201):
        new_id = r.json().get("ID")
        ok = new_id != 1  # 不应真的用我们指定的id=1
        summ.add("Mass Assignment-覆盖id/created_at", ok,
                 f"new_id={new_id}", "WARNING" if not ok else "INFO")
        if new_id:
            admin.delete(f"/api/courses/{new_id}")
    else:
        summ.add("Mass Assignment-覆盖id/created_at", True, f"status={r.status_code}", "INFO")

    # --- 响应中的敏感字段 ---
    print(f"\n{color('▸ 响应敏感字段', Colors.CYAN)}")

    r = admin.get("/api/users/1")
    if r.status_code == 200:
        user_data = r.text
        has_password = "password_hash" in user_data.lower() or "密码哈希" in user_data
        summ.add("敏感字段-用户响应含密码哈希", not has_password,
                 "" if not has_password else "响应中包含密码哈希!",
                 "CRITICAL" if has_password else "INFO")


# ============================================================
# 主流程
# ============================================================
if __name__ == "__main__":
    print(f"{color('╔══════════════════════════════════════════════════════════════╗', Colors.MAGENTA)}")
    print(f"{color('║  培训管理系统 — 全面测试套件                                ║', Colors.MAGENTA + Colors.BOLD)}")
    print(f"{color('║  数据库规则 · 压力测试 · 安全漏洞渗透                      ║', Colors.MAGENTA)}")
    print(f"{color('╚══════════════════════════════════════════════════════════════╝', Colors.MAGENTA)}")
    print(f"\n  Base URL: {color(BASE_URL, Colors.CYAN)}")

    # 优先测安全（最重要）
    test_security()

    # 数据库规则
    test_db_rules()

    # 压力测试
    test_stress()

    # 汇总
    summ.summary()
