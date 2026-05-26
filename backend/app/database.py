"""数据库连接 — 生产环境（SQLite WAL 模式 + 异步并发）"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event
from app.config import settings

# ===== 生产级 SQLite 配置 =====
# WAL 模式：读写并发、性能更高、更安全
# busy_timeout：避免 "database is locked" 错误
# 详见 https://www.sqlite.org/wal.html
connect_args = {}
if "sqlite" in settings.DATABASE_URL:
    connect_args = {
        "check_same_thread": False,
    }

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # 生产环境关闭 SQL 日志
    connect_args=connect_args,
)

# WAL 模式 + 性能优化（仅 SQLite）
if "sqlite" in settings.DATABASE_URL:
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")      # WAL 模式
        cursor.execute("PRAGMA busy_timeout=5000;")      # 5s 超时
        cursor.execute("PRAGMA synchronous=NORMAL;")      # 平衡安全/性能
        cursor.execute("PRAGMA cache_size=-20000;")       # 20MB 缓存
        cursor.execute("PRAGMA foreign_keys=ON;")         # 外键约束
        cursor.execute("PRAGMA temp_store=MEMORY;")       # 临时表存内存
        cursor.close()

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    """FastAPI 依赖注入：获取数据库会话"""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """初始化数据库表"""
    async with engine.begin() as conn:
        from app.models import department, user, course, exam, task, certificate, file, system_settings, learning_path, enterprise, review, notification, bookmark, sync_log  # noqa
        await conn.run_sync(Base.metadata.create_all)
