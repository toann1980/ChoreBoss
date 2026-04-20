"""Test configuration and fixtures for FastAPI."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.dependencies.db import get_session
from api.main import create_app
from choreboss.models import Base


@pytest.fixture
async def async_session_maker():
    """Create async session maker with in-memory SQLite.

    Yields:
        sessionmaker: Async session factory.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    yield AsyncSessionLocal

    await engine.dispose()


@pytest.fixture
async def async_session(async_session_maker):
    """Create async session for a single test.

    Args:
        async_session_maker: Session factory.

    Yields:
        AsyncSession: Database session.
    """
    async with async_session_maker() as session:
        yield session


@pytest.fixture
def test_app(async_session):
    """Create FastAPI test app with mocked session dependency.

    Args:
        async_session: Test database session.

    Returns:
        FastAPI: App configured for testing.
    """
    app = create_app()

    async def override_get_session():
        """Override session dependency."""
        yield async_session

    app.dependency_overrides[get_session] = override_get_session
    return app


@pytest.fixture
def test_client(test_app):
    """Create TestClient for FastAPI app.

    Args:
        test_app: FastAPI app.

    Returns:
        TestClient: Test client.
    """
    return TestClient(test_app)
