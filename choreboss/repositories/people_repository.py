"""Async people repository for database access."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from choreboss.models.chore import Chore
from choreboss.models.people import People


class PeopleRepository:
    """Repository for People model database operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with async session.

        Args:
            session: AsyncSession for database access.
        """
        self.session = session

    async def add_person(
        self,
        first_name: str,
        last_name: str,
        birthday: str,
        pin: str,
        is_admin: bool,
        login_name: str | None = None,
    ) -> People:
        """Add a new person to the database.

        Args:
            first_name: First name of the person.
            last_name: Last name of the person.
            birthday: Birthday of the person.
            pin: PIN of the person (will be hashed).
            is_admin: Whether the person is an admin.
            login_name: Optional human-friendly login name.

        Returns:
            People: Created person object.
        """
        next_seq = await self.get_next_sequence_num()
        resolved_login_name = login_name or f"{first_name.lower()}{next_seq}"
        person = People(
            first_name=first_name,
            last_name=last_name,
            login_name=resolved_login_name,
            birthday=birthday,
            pin=pin,
            is_admin=is_admin,
            sequence_num=next_seq,
        )
        person.set_pin(pin)
        self.session.add(person)
        await self.session.flush()
        return person

    async def admins_exist(self) -> bool:
        """Check if any admins exist in the database.

        Returns:
            bool: True if admins exist, False otherwise.
        """
        stmt = select(People).where(People.is_admin.is_(True))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def delete_person(self, person_id: int) -> None:
        """Delete a person from the database.

        Args:
            person_id: ID of person to delete.
        """
        await self.session.execute(
            update(Chore)
            .where(
                (Chore.person_id == person_id)
                | (Chore.last_completed_id == person_id)
            )
            .values(person_id=None, last_completed_id=None)
        )
        person = await self.get_person_by_id(person_id)
        if person:
            await self.session.delete(person)
            await self.session.flush()

    async def get_all_people(self) -> list[People]:
        """Get all people from the database.

        Returns:
            list: All People objects ordered by sequence_num.
        """
        stmt = select(People).order_by(People.sequence_num).options(
            selectinload(People.chores),
        )
        result = await self.session.execute(stmt)
        return result.scalars().unique().all()

    async def get_next_person_by_person_id(
        self,
        current_person_id: int,
    ) -> People | None:
        """Get the next person in sequence rotation.

        Args:
            current_person_id: ID of current person.

        Returns:
            People: Next person in sequence or None.
        """
        current = await self.get_person_by_id(current_person_id)
        if not current:
            return None

        # Get next person by sequence
        stmt = (
            select(People)
            .where(People.sequence_num > current.sequence_num)
            .order_by(People.sequence_num)
            .limit(1)
        )
        result = await self.session.execute(stmt)
        next_person = result.scalar_one_or_none()

        # If no one after, wrap to first
        if not next_person:
            stmt = select(People).order_by(People.sequence_num).limit(1)
            result = await self.session.execute(stmt)
            next_person = result.scalar_one_or_none()

        return next_person

    async def get_next_sequence_num(self) -> int:
        """Get the next sequence number for a new person.

        Returns:
            int: Next sequence number.
        """
        stmt = select(func.max(People.sequence_num))
        result = await self.session.execute(stmt)
        max_seq = result.scalar()
        return 1 if max_seq is None else max_seq + 1

    async def get_person_by_login_name(self, login_name: str) -> People | None:
        """Get a person by their login name."""
        stmt = select(People).where(People.login_name == login_name.lower()).options(
            selectinload(People.chores),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_person_by_id(self, person_id: int) -> People | None:
        """Get a person by their ID.

        Args:
            person_id: ID of person to retrieve.

        Returns:
            People: Person object or None if not found.
        """
        stmt = select(People).where(People.id == person_id).options(
            selectinload(People.chores),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_person_by_pin(self, pin: str) -> Optional[People]:
        """Get a person by their PIN.

        Args:
            pin: PIN to look up.

        Returns:
            People: Person object or None if not found.
        """
        stmt = select(People)
        result = await self.session.execute(stmt)
        people = result.scalars().all()

        for person in people:
            if person.verify_pin(pin):
                return person
        return None

    async def is_admin(self, pin: str) -> bool:
        """Check if a person with given PIN is an admin.

        Args:
            pin: PIN to check.

        Returns:
            bool: True if person is admin, False otherwise.
        """
        stmt = select(People).where(People.is_admin.is_(True))
        result = await self.session.execute(stmt)
        admins = result.scalars().all()

        for person in admins:
            if person.verify_pin(pin):
                return True
        return False

    async def update_person(self, person: People) -> People:
        """Update a person's data.

        Args:
            person: Person object with updated data.

        Returns:
            People: Updated person object.
        """
        await self.session.flush()
        return person

    async def update_sequence(
        self,
        person_id: int,
        new_sequence: int,
    ) -> None:
        """Update a person's sequence number.

        Args:
            person_id: ID of person to update.
            new_sequence: New sequence number.
        """
        person = await self.get_person_by_id(person_id)
        if person:
            person.sequence_num = new_sequence
            await self.session.flush()
