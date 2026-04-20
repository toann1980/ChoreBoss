"""Async chore service for business logic."""

from __future__ import annotations

from choreboss.repositories.chore_repository import ChoreRepository
from choreboss.repositories.people_repository import PeopleRepository


class ChoreService:
    """Service for chore-related business logic."""

    def __init__(
        self,
        chore_repository: ChoreRepository,
        people_repository: PeopleRepository,
    ) -> None:
        """Initialize chore service.

        Args:
            chore_repository: Repository for chore data access.
            people_repository: Repository for people data access.
        """
        self.chore_repository = chore_repository
        self.people_repository = people_repository

    async def add_chore(
        self,
        name: str,
        description: str,
        person_id: int | None = None,
    ):
        """Add a new chore.

        Args:
            name: Name of the chore.
            description: Description of the chore.
            person_id: Optional ID of person to assign to.

        Returns:
            Chore: Created chore object.
        """
        return await self.chore_repository.add_chore(
            name=name,
            description=description,
            person_id=person_id,
        )

    async def complete_chore(
        self,
        chore_id: int,
        person_id: int,
    ):
        """Mark a chore as complete and auto-assign next person.

        Args:
            chore_id: ID of chore to complete.
            person_id: ID of person completing it.

        Returns:
            Chore: Updated chore object.
        """
        # Mark complete
        chore = await self.chore_repository.complete_chore(chore_id, person_id)

        if chore and chore.person_id:
            # Auto-assign next person in rotation
            next_person = await self.people_repository.get_next_person_by_person_id(
                chore.person_id
            )
            if next_person:
                chore.person_id = next_person.id
                await self.chore_repository.update_chore(chore)

        return chore

    async def delete_chore(self, chore_id: int) -> None:
        """Delete a chore by its ID.

        Args:
            chore_id: ID of chore to delete.
        """
        await self.chore_repository.delete_chore(chore_id)

    async def get_all_chores(self):
        """Retrieve all chores.

        Returns:
            list: All chore objects.
        """
        return await self.chore_repository.get_all_chores()

    async def get_chore_by_id(self, chore_id: int):
        """Retrieve a chore by its ID.

        Args:
            chore_id: ID of chore to retrieve.

        Returns:
            Chore: Chore object or None.
        """
        return await self.chore_repository.get_chore_by_id(chore_id)

    async def update_chore(self, chore):
        """Update a chore.

        Args:
            chore: Chore object with updated data.

        Returns:
            Chore: Updated chore object.
        """
        return await self.chore_repository.update_chore(chore)
