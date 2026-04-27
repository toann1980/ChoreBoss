"""People router."""

from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_admin_person, get_current_person, get_session
from api.schemas import PersonCreate, PersonRead, PersonUpdate
from choreboss.repositories import PeopleRepository
from choreboss.services import PeopleService

router = APIRouter()


@router.get("/", response_model=list[PersonRead])
async def list_people(
    session: AsyncSession = Depends(get_session),
    current_person: dict[str, Any] = Depends(get_current_person),
) -> list[Any]:
    """List all people.

    Args:
        session: Database session.
        current_person: Authenticated person.

    Returns:
        list: All people.
    """
    people_repo = PeopleRepository(session)
    service = PeopleService(people_repo)
    return await service.get_all_people()


@router.get("/{person_id}", response_model=PersonRead)
async def get_person(
    person_id: int,
    session: AsyncSession = Depends(get_session),
    current_person: dict[str, Any] = Depends(get_current_person),
) -> Any:
    """Get a specific person.

    Args:
        person_id: Person ID.
        session: Database session.
        current_person: Authenticated person.

    Returns:
        dict: Person data.

    Raises:
        HTTPException: If person not found.
    """
    people_repo = PeopleRepository(session)
    service = PeopleService(people_repo)
    person = await service.get_person_by_id(person_id)

    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found",
        )

    return person


@router.post("/", response_model=PersonRead)
async def create_person(
    person: PersonCreate,
    session: AsyncSession = Depends(get_session),
    admin: dict[str, Any] = Depends(get_admin_person),
) -> Any:
    """Create a new person (admin only).

    Args:
        person: Person creation data.
        session: Database session.
        admin: Authenticated admin person.

    Returns:
        dict: Created person.
    """
    people_repo = PeopleRepository(session)
    service = PeopleService(people_repo)
    result = await service.add_person(
        first_name=person.first_name,
        last_name=person.last_name,
        birthday=person.birthday,
        pin=person.pin,
        is_admin=person.is_admin,
    )
    await session.commit()
    return result


@router.put("/{person_id}", response_model=PersonRead)
async def update_person(
    person_id: int,
    person_update: PersonUpdate,
    session: AsyncSession = Depends(get_session),
    admin: dict[str, Any] = Depends(get_admin_person),
) -> Any:
    """Update a person (admin only).

    Args:
        person_id: Person ID.
        person_update: Update data.
        session: Database session.
        admin: Authenticated admin person.

    Returns:
        dict: Updated person.

    Raises:
        HTTPException: If person not found.
    """
    people_repo = PeopleRepository(session)
    service = PeopleService(people_repo)
    person = await service.get_person_by_id(person_id)

    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found",
        )

    # Update fields if provided
    if person_update.first_name is not None:
        person.first_name = person_update.first_name
    if person_update.last_name is not None:
        person.last_name = person_update.last_name
    if person_update.birthday is not None:
        person.birthday = person_update.birthday
    if person_update.is_admin is not None:
        person.is_admin = person_update.is_admin

    result = await service.update_person(person)
    await session.commit()
    return result


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_person(
    person_id: int,
    session: AsyncSession = Depends(get_session),
    admin: dict[str, Any] = Depends(get_admin_person),
) -> None:
    """Delete a person (admin only).

    Args:
        person_id: Person ID.
        session: Database session.
        admin: Authenticated admin person.

    Raises:
        HTTPException: If person not found.
    """
    people_repo = PeopleRepository(session)
    service = PeopleService(people_repo)
    person = await service.get_person_by_id(person_id)

    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found",
        )

    await service.delete_person(person_id)
    await session.commit()
