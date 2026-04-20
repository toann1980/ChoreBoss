"""Async chore repository for database access."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from choreboss.models.chore import Chore


class ChoreRepository:
    """Repository for Chore model database operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with async session.

        Args:
            session: AsyncSession for database access.
        """
        self.session = session

    async def add_chore(
        self,
        name: str,
        description: str,
        person_id: int | None = None,
    ) -> Chore:
        """Add a new chore to the database.

        Args:
            name: Name of the chore.
            description: Description of the chore.
            person_id: Optional person ID to assign chore to.

        Returns:
            Chore: Created chore object.
        """
        chore = Chore(
            name=name,
            description=description,
            person_id=person_id,
        )
        self.session.add(chore)
        await self.session.flush()
        return chore

    async def complete_chore(
        self,
        chore_id: int,
        person_id: int,
    ) -> Chore | None:
        """Mark a chore as completed.

        Args:
            chore_id: ID of chore to complete.
            person_id: ID of person completing chore.

        Returns:
            Chore: Updated chore object or None if not found.
        """
        chore = await self.get_chore_by_id(chore_id)
        if chore:
            chore.last_completed_id = person_id
            chore.last_completed_date = datetime.utcnow()
            await self.session.flush()
        return chore

    async def delete_chore(self, chore_id: int) -> None:
        """Delete a chore from the database.

        Args:
            chore_id: ID of chore to delete.
        """
        chore = await self.get_chore_by_id(chore_id)
        if chore:
            await self.session.delete(chore)
            await self.session.flush()

    async def get_all_chores(self) -> list[Chore]:
        """Retrieve all chores from the database.

        Returns:
            list: All Chore objects.
        """
        stmt = select(Chore).options(
            selectinload(Chore.person),
        )
        result = await self.session.execute(stmt)
        return result.scalars().unique().all()

    async def get_chore_by_id(self, chore_id: int) -> Chore | None:
        """Retrieve a chore by its ID.

        Args:
            chore_id: ID of chore to retrieve.

        Returns:
            Chore: Chore object or None if not found.
        """
        stmt = select(Chore).where(Chore.id == chore_id).options(
            selectinload(Chore.person),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_chore(self, chore: Chore) -> Chore:
        """Update an existing chore in the database.

        Args:
            chore: Chore object with updated information.

        Returns:
            Chore: Updated chore object.
        """
        await self.session.flush()
        return chore
