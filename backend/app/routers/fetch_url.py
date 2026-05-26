"""网址抓取路由：将URL内容保存为HTML本地副本"""
import ipaddress
import socket
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from typing import Optional
from app.database import get_db
from app.models.file import FileRecord
from app.utils.auth import get_current_user
from app.utils.storage import get_storage

router = APIRouter(prefix="/api/fetch-url", tags=["网址抓取"])

# 禁止访问的内网IP范围
BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
]

BLOCKED_SCHEMES = {"file", "ftp"}


def validate_url(url: str) -> None:
    """验证URL安全性：阻止内网IP和危险协议"""
    parsed = urlparse(url)

    # 阻止危险协议
    if parsed.scheme in BLOCKED_SCHEMES:
        raise HTTPException(
            status_code=400,
            detail=f"不允许使用 {parsed.scheme}:// 协议",
        )

    # 只允许 http/https
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="仅支持 http/https 协议")

    hostname = parsed.hostname
    if not hostname:
        raise HTTPException(status_code=400, detail="URL 中缺少主机名")

    # 解析主机名为IP地址
    try:
        addr = ipaddress.ip_address(hostname)
    except ValueError:
        # 可能是域名，需要DNS解析
        try:
            resolved_ips = socket.getaddrinfo(hostname, None)
        except socket.gaierror:
            raise HTTPException(status_code=400, detail=f"无法解析域名: {hostname}")
        for res in resolved_ips:
            ip_str = res[4][0]
            try:
                addr = ipaddress.ip_address(ip_str)
            except ValueError:
                continue
            if any(addr in net for net in BLOCKED_NETWORKS):
                raise HTTPException(
                    status_code=400,
                    detail=f"禁止访问内网地址: {ip_str}",
                )
        return  # 域名解析后无内网IP，放行

    # 直接是IP地址，检查是否在内网范围
    if any(addr in net for net in BLOCKED_NETWORKS):
        raise HTTPException(
            status_code=400,
            detail=f"禁止访问内网地址: {hostname}",
        )


class FetchUrlRequest(BaseModel):
    """抓取URL请求"""
    url: str = Field(..., description="要抓取的网页URL")
    title: Optional[str] = Field(None, description="自定义标题（可选）")

    class Config:
        populate_by_name = True


@router.post("")
async def fetch_url(
    req: FetchUrlRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """抓取网页HTML并保存到本地"""
    if current_user.get("角色") not in ("admin", "teacher"):
        raise HTTPException(status_code=403, detail="无权限")

    # 验证URL安全性（防SSRF）
    validate_url(req.url)

    # 获取网页内容
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get(req.url)
            resp.raise_for_status()
            html_content = resp.text
    except httpx.HTTPError as e:
        raise HTTPException(status_code=400, detail=f"无法访问该网址: {str(e)}")

    # 提取标题
    soup = BeautifulSoup(html_content, 'html.parser')
    page_title = req.title or soup.title.string if soup.title else req.url

    # 添加本地标记
    saved_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{page_title}</title>
<base href="{req.url}">
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; }}
  .hermes-saved-banner {{
    background: #304156; color: #fff; padding: 8px 16px;
    font-size: 13px; text-align: center; position: sticky; top: 0; z-index: 9999;
  }}
  .hermes-saved-banner a {{ color: #409EFF; }}
</style>
</head>
<body>
<div class="hermes-saved-banner">
  📄 本地保存的网页 | 来源: <a href="{req.url}" target="_blank">{req.url}</a>
  | 保存时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
</div>
{soup.body.decode() if soup.body else html_content}
</body>
</html>"""

    # 生成文件名并保存
    import hashlib
    import time
    url_hash = hashlib.md5(req.url.encode()).hexdigest()[:8]
    timestamp = str(int(time.time()))
    filename = f"{page_title}_{url_hash}_{timestamp}.html"
    # 清理文件名中的非法字符
    import re
    safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    file_path = f"html/{safe_filename}"

    storage = get_storage()
    html_bytes = saved_html.encode('utf-8')
    await storage.save(file_path, html_bytes)

    # 记录到数据库
    record = FileRecord(
        filename=safe_filename,
        file_path=file_path,
        file_size=len(html_bytes),
        file_type="html",
        mime_type="text/html",
        uploaded_by=current_user.get("id"),
    )
    db.add(record)
    await db.flush()

    return {
        "ID": record.id,
        "标题": page_title,
        "来源网址": req.url,
        "文件地址": storage.get_url(file_path),
        "文件大小": len(html_bytes),
        "保存路径": file_path,
        "labels": {
            "ID": "id",
            "标题": "title",
            "来源网址": "source_url",
            "文件地址": "url",
            "文件大小": "file_size",
            "保存路径": "file_path",
        }
    }
