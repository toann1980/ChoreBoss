"""Authentication router."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import create_access_token, get_session
from api.schemas import PersonLogin, TokenResponse
from choreboss.repositories import PeopleRepository
from choreboss.services import PeopleService

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: PersonLogin,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Authenticate person with PIN and return JWT token.

    Args:
        credentials: Login credentials (person_id, pin).
        session: Database session.

    Returns:
        dict: JWT token and person info.

    Raises:
        HTTPException: If person not found or PIN invalid.
    """
    people_repo = PeopleRepository(session)
    service = PeopleService(people_repo)

    person = await service.get_person_by_id(credentials.person_id)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found",
        )

    # Verify PIN (bcrypt comparison)
    if not service.verify_pin(credentials.pin, person.pin):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid PIN",
        )

    # Create token
    access_token = create_access_token(
        person_id=person.id,
        is_admin=person.is_admin,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "person_id": person.id,
        "is_admin": person.is_admin,
    }
