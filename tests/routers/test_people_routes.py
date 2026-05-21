"""Tests for people routes."""

from __future__ import annotations

import pytest
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from choreboss.models.chore import Chore
from tests.setup_memory_records import setup_test_people, setup_test_chores


@pytest.mark.asyncio
async def test_list_people_authenticated(
    test_client,
    async_session: AsyncSession,
) -> None:
    """Test listing people with authentication.

    Args:
        test_client: FastAPI test client.
        async_session: Database session.
    """
    # Setup
    people = await setup_test_people(async_session, 2)
    await async_session.commit()
    admin = people[0]

    # Login
    login_response = test_client.post(
        "/api/auth/login",
        json={"login_name": admin.login_name, "pin": "1234"},
    )
    token = login_response.json()["access_token"]

    # List people
    response = test_client.get(
        "/api/people/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 2


@pytest.mark.asyncio
async def test_list_people_unauthenticated(test_client) -> None:
    """Test listing people without authentication.

    Args:
        test_client: FastAPI test client.
    """
    response = test_client.get("/api/people/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_person(
    test_client,
    async_session: AsyncSession,
) -> None:
    """Test getting a single person.

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

    # Get person
    response = test_client.get(
        f"/api/people/{person.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["first_name"] == person.first_name
    assert data["last_name"] == person.last_name
    assert data["assign_chores"] is True


@pytest.mark.asyncio
async def test_delete_person_unassigns_chores(
    test_client,
    async_session: AsyncSession,
) -> None:
    """Test deleting a person unassigns their chores instead of breaking them."""
    people = await setup_test_people(async_session, 1)
    chores = await setup_test_chores(async_session, 1)
    await async_session.commit()
    admin = people[0]
    chore = chores[0]
    chore.person_id = admin.id
    chore.last_completed_id = admin.id
    await async_session.commit()

    login_response = test_client.post(
        "/api/auth/login",
        json={"login_name": admin.login_name, "pin": "1234"},
    )
    token = login_response.json()["access_token"]

    response = test_client.delete(
        f"/api/people/{admin.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    updated_chore = (await async_session.get(Chore, chore.id))
    assert updated_chore.person_id is None
    assert updated_chore.last_completed_id is None


@pytest.mark.asyncio
async def test_create_person_admin(
    test_client,
    async_session: AsyncSession,
) -> None:
    """Test creating person as admin.

    Args:
        test_client: FastAPI test client.
        async_session: Database session.
    """
    # Setup
    people = await setup_test_people(async_session, 1)
    await async_session.commit()
    admin = people[0]

    # Login
    login_response = test_client.post(
        "/api/auth/login",
        json={"login_name": admin.login_name, "pin": "1234"},
    )
    token = login_response.json()["access_token"]

    # Create person
    from datetime import date
    response = test_client.post(
        "/api/people/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Jane",
            "last_name": "Doe",
            "login_name": "jane_doe_2",
            "birthday": "2015-05-15",  # String is OK, Pydantic will convert
            "pin": "5678",
            "is_admin": False,
            "assign_chores": False,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["first_name"] == "Jane"
    assert data["last_name"] == "Doe"
    assert data["login_name"] == "jane_doe_2"
    assert data["is_admin"] is False
    assert data["assign_chores"] is False


@pytest.mark.asyncio
async def test_create_first_person_without_auth_when_no_admins_exist(
    test_client,
    async_session: AsyncSession,
) -> None:
    """Test bootstrap person creation without auth when no admins exist."""
    response = test_client.post(
        "/api/people/",
        json={
            "first_name": "First",
            "last_name": "User",
            "login_name": "firstuser",
            "birthday": "2015-05-15",
            "pin": "5678",
            "is_admin": True,
            "assign_chores": True,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["login_name"] == "firstuser"
    assert data["is_admin"] is True
    assert data["assign_chores"] is True


@pytest.mark.asyncio
async def test_create_person_duplicate_login_name_fails(
    test_client,
    async_session: AsyncSession,
) -> None:
    """Test creating a person with a duplicate login_name returns a clean error."""
    people = await setup_test_people(async_session, 1)
    await async_session.commit()
    admin = people[0]

    login_response = test_client.post(
        "/api/auth/login",
        json={"login_name": admin.login_name, "pin": "1234"},
    )
    token = login_response.json()["access_token"]

    response = test_client.post(
        "/api/people/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Duplicate",
            "last_name": "User",
            "login_name": admin.login_name,
            "birthday": "2015-05-15",
            "pin": "5678",
            "is_admin": False,
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Login name already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_person_non_admin_with_multiple_admins(
    test_client,
    async_session: AsyncSession,
) -> None:
    """Test creating person as non-admin when multiple admins exist still returns 403."""
    people = await setup_test_people(async_session, 3)
    people[1].is_admin = True
    await async_session.commit()
    non_admin = people[2]

    login_response = test_client.post(
        "/api/auth/login",
        json={"login_name": non_admin.login_name, "pin": "9012"},
    )
    token = login_response.json()["access_token"]

    response = test_client.post(
        "/api/people/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Blocked",
            "last_name": "Case",
            "login_name": "blocked_multi_admin",
            "birthday": "2015-05-15",
            "pin": "9012",
            "is_admin": False,
        },
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_create_person_non_admin(
    test_client,
    async_session: AsyncSession,
) -> None:
    """Test creating person as non-admin (should fail).

    Args:
        test_client: FastAPI test client.
        async_session: Database session.
    """
    # Setup non-admin person
    people = await setup_test_people(async_session, 2)
    await async_session.commit()
    non_admin = people[1]  # Jane is not admin

    # Login
    login_response = test_client.post(
        "/api/auth/login",
        json={"login_name": non_admin.login_name, "pin": "5678"},
    )
    token = login_response.json()["access_token"]

    # Try to create person
    response = test_client.post(
        "/api/people/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Jane",
            "last_name": "Doe",
            "login_name": "jane_doe_3",
            "birthday": "2015-05-15",  # String is OK, Pydantic will convert
            "pin": "5678",
        },
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
