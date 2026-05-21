"""Database configuration and session management."""

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from choreboss.config import get_config

# Lazy initialization - don't create engine at import time
_engine = None
_AsyncSessionLocal = None


def _get_engine():
    """Get or create the async engine.

    Returns:
        AsyncEngine: Database engine.
    """
    global _engine
    if _engine is None:
        config = get_config()
        _engine = create_async_engine(
            config.database_url,
            echo=config.debug,
            future=True,
        )
    return _engine


def _get_session_local():
    """Get or create the session factory.

    Returns:
        sessionmaker: Async session factory.
    """
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        engine = _get_engine()
        _AsyncSessionLocal = sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _AsyncSessionLocal


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session.

    Yields:
        AsyncSession: Database session.
    """
    AsyncSessionLocal = _get_session_local()
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
