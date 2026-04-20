"""Test configuration and fixtures for ChoreBoss."""

from __future__ import annotations

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.dependencies.db import get_session
from api.main import create_app
from choreboss.models import Base


@pytest_asyncio.fixture
async def async_engine():
    """Create async engine with in-memory SQLite.

    Yields:
        AsyncEngine: Database engine.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def async_session(async_engine):
    """Create async session for a single test.

    Args:
        async_engine: Async database engine.

    Yields:
        AsyncSession: Database session.
    """
    async_session_local = sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_local() as session:
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
        """Override get_session dependency with test session."""
        yield async_session

    app.dependency_overrides[get_session] = override_get_session

    return app


@pytest.fixture
def test_client(test_app):
    """Create TestClient for FastAPI app.

    Args:
        test_app: FastAPI application.

    Returns:
        TestClient: Test HTTP client.
    """
    return TestClient(test_app)
