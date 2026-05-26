"""速率限制工具 — 基于 slowapi"""
from slowapi import Limiter
from slowapi.util import get_remote_address

# 全局限制器
limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])

# 各端点速率限制
RATE_LIMITS = {
    "login": "10/minute",       # 登录接口：防暴力破解
    "api": "120/minute",        # 通用 API
    "upload": "30/minute",      # 文件上传
    "sync": "5/5minutes",       # LDAP 同步（昂贵操作）
    "fetch_url": "10/minute",   # URL 抓取
}
