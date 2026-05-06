"""Async people service for business logic."""

from __future__ import annotations

from typing import Optional

from choreboss.models.people import People
from choreboss.repositories.people_repository import PeopleRepository


class PeopleService:
    """Service for people-related business logic."""

    def __init__(self, people_repository: PeopleRepository) -> None:
        """Initialize people service.

        Args:
            people_repository: Repository for people data access.
        """
        self.people_repository = people_repository

    async def add_person(
        self,
        first_name: str,
        last_name: str,
        birthday: str,
        pin: str,
        is_admin: bool,
        login_name: str | None = None,
    ) -> People:
        """Add a new person.

        Args:
            first_name: First name.
            last_name: Last name.
            birthday: Birthday.
            pin: PIN (will be hashed).
            is_admin: Admin flag.
            login_name: Optional human-friendly login name.

        Returns:
            People: Created person object.
        """
        return await self.people_repository.add_person(
            first_name=first_name,
            last_name=last_name,
            birthday=birthday,
            pin=pin,
            is_admin=is_admin,
            login_name=login_name,
        )

    async def admins_exist(self) -> bool:
        """Check if any admins exist.

        Returns:
            bool: True if admins exist.
        """
        return await self.people_repository.admins_exist()

    async def delete_person(self, person_id: int) -> None:
        """Delete a person by ID.

        Args:
            person_id: ID of person to delete.
        """
        await self.people_repository.delete_person(person_id)

    async def delete_person_and_adjust_sequence(
        self,
        person_id: int,
    ) -> None:
        """Delete a person and adjust sequence numbers.

        Args:
            person_id: ID of person to delete.
        """
        person_to_delete = await self.get_person_by_id(person_id)
        if person_to_delete:
            deleted_seq = person_to_delete.sequence_num
            await self.delete_person(person_id)
            remaining = await self.get_all_people()
            for person in remaining:
                if person.sequence_num > deleted_seq:
                    person.sequence_num -= 1
                    await self.update_person(person)

    async def get_all_people(self) -> list[People]:
        """Get all people.

        Returns:
            list: All people objects.
        """
        return await self.people_repository.get_all_people()

    async def get_next_person_by_person_id(
        self,
        current_person_id: int,
    ) -> People | None:
        """Get next person in sequence.

        Args:
            current_person_id: Current person ID.

        Returns:
            People: Next person or None.
        """
        return await self.people_repository.get_next_person_by_person_id(
            current_person_id
        )

    async def get_person_by_id(self, person_id: int) -> Optional[People]:
        """Get person by ID.

        Args:
            person_id: ID of person to retrieve.

        Returns:
            People: Person object or None.
        """
        return await self.people_repository.get_person_by_id(person_id)

    async def get_person_by_login_name(self, login_name: str) -> Optional[People]:
        """Get person by login name.

        Args:
            login_name: Login name to look up.

        Returns:
            People: Person object or None.
        """
        return await self.people_repository.get_person_by_login_name(login_name)

    async def get_person_by_pin(self, pin: str) -> Optional[People]:
        """Get person by PIN.

        Args:
            pin: PIN to look up.

        Returns:
            People: Person object or None.
        """
        return await self.people_repository.get_person_by_pin(pin)

    async def is_admin(self, pin: str) -> bool:
        """Check if person with PIN is admin.

        Args:
            pin: PIN to check.

        Returns:
            bool: True if admin.
        """
        return await self.people_repository.is_admin(pin)

    async def update_person(self, person: People) -> People:
        """Update a person.

        Args:
            person: Person object with updated data.

        Returns:
            People: Updated person object.
        """
        return await self.people_repository.update_person(person)

    async def update_sequence(
        self,
        person_id: int,
        new_sequence: int,
    ) -> None:
        """Update person's sequence number.

        Args:
            person_id: ID of person.
            new_sequence: New sequence number.
        """
        await self.people_repository.update_sequence(person_id, new_sequence)

    @staticmethod
    def validate_pin(pin: str) -> bool:
        """Validate a PIN.

        A valid PIN must be 4-6 digit string.

        Args:
            pin: PIN to validate.

        Returns:
            bool: True if valid.
        """
        return 4 <= len(pin) <= 6 and pin.isdigit()

    @staticmethod
    def verify_pin(pin: str, hash: str) -> bool:
        """Verify a PIN against a hash.

        Args:
            pin: Plain PIN.
            hash: Hashed PIN.

        Returns:
            bool: True if PIN matches hash.
        """
        import bcrypt

        return bcrypt.checkpw(
            pin.encode("utf-8"),
            hash.encode("utf-8"),
        )
