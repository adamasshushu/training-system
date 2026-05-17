"""网址抓取路由：将URL内容保存为HTML本地副本"""
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
