"""Tests for chore routes."""

from __future__ import annotations

import pytest
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from tests.setup_memory_records import setup_test_chores, setup_test_people


@pytest.mark.asyncio
async def test_list_chores_authenticated(
    test_client,
    async_session: AsyncSession,
) -> None:
    """Test listing chores with authentication.

    Args:
        test_client: FastAPI test client.
        async_session: Database session.
    """
    # Setup
    people = await setup_test_people(async_session, 1)
    chores = await setup_test_chores(async_session, 3)
    await async_session.commit()
    person = people[0]

    # Login to get token
    login_response = test_client.post(
        "/api/auth/login",
        json={"login_name": person.login_name, "pin": "1234"},
    )
    token = login_response.json()["access_token"]

    # List chores
    response = test_client.get(
        "/api/chores/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 3


@pytest.mark.asyncio
async def test_list_chores_unauthenticated(test_client) -> None:
    """Test listing chores without authentication.

    Args:
        test_client: FastAPI test client.
    """
    response = test_client.get("/api/chores/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_chore(
    test_client,
    async_session: AsyncSession,
) -> None:
    """Test getting a single chore.

    Args:
        test_client: FastAPI test client.
        async_session: Database session.
    """
    # Setup
    people = await setup_test_people(async_session, 1)
    chores = await setup_test_chores(async_session, 1)
    await async_session.commit()
    person = people[0]
    chore = chores[0]

    # Login
    login_response = test_client.post(
        "/api/auth/login",
        json={"login_name": person.login_name, "pin": "1234"},
    )
    token = login_response.json()["access_token"]

    # Get chore
    response = test_client.get(
        f"/api/chores/{chore.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == chore.name
    assert data["description"] == chore.description


@pytest.mark.asyncio
async def test_get_chore_not_found(
    test_client,
    async_session: AsyncSession,
) -> None:
    """Test getting non-existent chore.

    Args:
        test_client: FastAPI test client.
        async_session: Database session.
    """
    # Setup
    people = await setup_test_people(async_session, 1)
    await async_session.commit()
    person = people[0]

    # Login
    login_response = test_client.post(
        "/api/auth/login",
        json={"login_name": person.login_name, "pin": "1234"},
    )
    token = login_response.json()["access_token"]

    # Get non-existent chore
    response = test_client.get(
        "/api/chores/9999",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_create_chore_admin(
    test_client,
    async_session: AsyncSession,
) -> None:
    """Test creating chore as admin.

    Args:
        test_client: FastAPI test client.
        async_session: Database session.
    """
    # Setup
    people = await setup_test_people(async_session, 1)
    await async_session.commit()
    person = people[0]

    # Login
    login_response = test_client.post(
        "/api/auth/login",
        json={"login_name": person.login_name, "pin": "1234"},
    )
    token = login_response.json()["access_token"]

    # Create chore
    response = test_client.post(
        "/api/chores/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Wash Dishes",
            "description": "This is a test chore with content",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Wash Dishes"
    assert data["description"] == "This is a test chore with content"


@pytest.mark.asyncio
async def test_create_chore_non_admin(
    test_client,
    async_session: AsyncSession,
) -> None:
    """Test creating chore as non-admin (should fail).

    Args:
        test_client: FastAPI test client.
        async_session: Database session.
    """
    # Setup non-admin person
    people = await setup_test_people(async_session, 2)
    await async_session.commit()
    person = people[1]  # Jane is not admin

    # Login
    login_response = test_client.post(
        "/api/auth/login",
        json={"login_name": person.login_name, "pin": "5678"},
    )
    token = login_response.json()["access_token"]

    # Try to create chore
    response = test_client.post(
        "/api/chores/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Wash Dishes",
            "description": "This is a test chore with content",
        },
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_complete_chore(
    test_client,
    async_session: AsyncSession,
) -> None:
    """Test marking chore as complete.

    Args:
        test_client: FastAPI test client.
        async_session: Database session.
    """
    # Setup
    people = await setup_test_people(async_session, 1)
    chores = await setup_test_chores(async_session, 1)
    await async_session.commit()
    person = people[0]
    chore = chores[0]

    # Login
    login_response = test_client.post(
        "/api/auth/login",
        json={"login_name": person.login_name, "pin": "1234"},
    )
    token = login_response.json()["access_token"]

    # Complete chore
    response = test_client.post(
        f"/api/chores/{chore.id}/complete",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["last_completed_id"] == person.id
    assert data["last_completed_date"] is not None
