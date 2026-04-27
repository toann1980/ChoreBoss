"""Chores router."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_admin_person, get_current_person, get_session
from api.schemas import ChoreCreate, ChoreRead, ChoreUpdate
from choreboss.repositories import ChoreRepository, PeopleRepository
from choreboss.services import ChoreService

router = APIRouter()


@router.get("/", response_model=list[ChoreRead])
async def list_chores(
    session: AsyncSession = Depends(get_session),
    current_person: dict[str, Any] = Depends(get_current_person),
) -> list[Any]:
    """List all chores.

    Args:
        session: Database session.
        current_person: Authenticated person.

    Returns:
        list: All chores.
    """
    chore_repo = ChoreRepository(session)
    people_repo = PeopleRepository(session)
    service = ChoreService(chore_repo, people_repo)
    return await service.get_all_chores()


@router.get("/{chore_id}", response_model=ChoreRead)
async def get_chore(
    chore_id: int,
    session: AsyncSession = Depends(get_session),
    current_person: dict[str, Any] = Depends(get_current_person),
) -> Any:
    """Get a specific chore.

    Args:
        chore_id: Chore ID.
        session: Database session.
        current_person: Authenticated person.

    Returns:
        dict: Chore data.

    Raises:
        HTTPException: If chore not found.
    """
    chore_repo = ChoreRepository(session)
    people_repo = PeopleRepository(session)
    service = ChoreService(chore_repo, people_repo)
    chore = await service.get_chore_by_id(chore_id)

    if not chore:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chore not found",
        )

    return chore


@router.post("/", response_model=ChoreRead)
async def create_chore(
    chore: ChoreCreate,
    session: AsyncSession = Depends(get_session),
    admin: dict[str, Any] = Depends(get_admin_person),
) -> Any:
    """Create a new chore (admin only).

    Args:
        chore: Chore creation data.
        session: Database session.
        admin: Authenticated admin person.

    Returns:
        dict: Created chore.
    """
    chore_repo = ChoreRepository(session)
    people_repo = PeopleRepository(session)
    service = ChoreService(chore_repo, people_repo)
    result = await service.add_chore(
        name=chore.name,
        description=chore.description,
        person_id=chore.person_id,
    )
    await session.commit()
    return result


@router.put("/{chore_id}", response_model=ChoreRead)
async def update_chore(
    chore_id: int,
    chore_update: ChoreUpdate,
    session: AsyncSession = Depends(get_session),
    admin: dict[str, Any] = Depends(get_admin_person),
) -> Any:
    """Update a chore (admin only).

    Args:
        chore_id: Chore ID.
        chore_update: Update data.
        session: Database session.
        admin: Authenticated admin person.

    Returns:
        dict: Updated chore.

    Raises:
        HTTPException: If chore not found.
    """
    chore_repo = ChoreRepository(session)
    people_repo = PeopleRepository(session)
    service = ChoreService(chore_repo, people_repo)
    chore = await service.get_chore_by_id(chore_id)

    if not chore:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chore not found",
        )

    # Update fields if provided
    if chore_update.name is not None:
        chore.name = chore_update.name
    if chore_update.description is not None:
        chore.description = chore_update.description
    if chore_update.person_id is not None:
        chore.person_id = chore_update.person_id

    result = await service.update_chore(chore)
    await session.commit()
    return result


@router.delete("/{chore_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_chore(
    chore_id: int,
    session: AsyncSession = Depends(get_session),
    admin: dict[str, Any] = Depends(get_admin_person),
) -> None:
    """Delete a chore (admin only).

    Args:
        chore_id: Chore ID.
        session: Database session.
        admin: Authenticated admin person.

    Raises:
        HTTPException: If chore not found.
    """
    chore_repo = ChoreRepository(session)
    people_repo = PeopleRepository(session)
    service = ChoreService(chore_repo, people_repo)
    chore = await service.get_chore_by_id(chore_id)

    if not chore:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chore not found",
        )

    await service.delete_chore(chore_id)
    await session.commit()


@router.post("/{chore_id}/complete", response_model=ChoreRead)
async def complete_chore(
    chore_id: int,
    session: AsyncSession = Depends(get_session),
    current_person: dict[str, Any] = Depends(get_current_person),
) -> Any:
    """Mark a chore as complete and auto-assign next person.

    Args:
        chore_id: Chore ID.
        session: Database session.
        current_person: Authenticated person.

    Returns:
        dict: Updated chore.

    Raises:
        HTTPException: If chore not found.
    """
    chore_repo = ChoreRepository(session)
    people_repo = PeopleRepository(session)
    service = ChoreService(chore_repo, people_repo)
    chore = await service.get_chore_by_id(chore_id)

    if not chore:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chore not found",
        )

    # Mark complete
    result = await service.complete_chore(
        chore_id,
        current_person["person_id"],
    )
    await session.commit()
    return result
