"""Tests for authentication routes."""

from __future__ import annotations

import pytest
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from choreboss.models.people import People
from tests.setup_memory_records import setup_test_people


@pytest.mark.asyncio
async def test_login_success(
    test_client,
    async_session: AsyncSession,
) -> None:
    """Test successful login with valid PIN.

    Args:
        test_client: FastAPI test client.
        async_session: Database session.
    """
    # Setup test person
    people = await setup_test_people(async_session, 1)
    await async_session.commit()
    person = people[0]

    # Login
    response = test_client.post(
        "/api/auth/login",
        json={"person_id": person.id, "pin": "1234"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["person_id"] == person.id
    assert data["is_admin"] is True


@pytest.mark.asyncio
async def test_login_invalid_pin(
    test_client,
    async_session: AsyncSession,
) -> None:
    """Test login with invalid PIN.

    Args:
        test_client: FastAPI test client.
        async_session: Database session.
    """
    # Setup test person
    people = await setup_test_people(async_session, 1)
    await async_session.commit()
    person = people[0]

    # Login with wrong PIN
    response = test_client.post(
        "/api/auth/login",
        json={"person_id": person.id, "pin": "9999"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid PIN" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_person_not_found(test_client) -> None:
    """Test login with non-existent person.

    Args:
        test_client: FastAPI test client.
    """
    response = test_client.post(
        "/api/auth/login",
        json={"person_id": 9999, "pin": "1234"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Person not found" in response.json()["detail"]
