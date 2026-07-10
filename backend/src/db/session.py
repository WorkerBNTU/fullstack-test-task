from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import get_settings

settings = get_settings()

# One engine / one session factory for the whole process, shared by the
# FastAPI app and the Celery worker (previously each module created its own,
# resulting in two separate connection pools against the same database).
engine = create_async_engine(settings.database_url)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def session_scope() -> AsyncIterator[AsyncSession]:
    """Provide a transactional session, usable from both API and worker code."""
    async with async_session_maker() as session:
        yield session


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency variant of ``session_scope``."""
    async with async_session_maker() as session:
        yield session
