from choreboss.repositories.people_repository import PeopleRepository
from choreboss.models.people import People
from typing import List, Optional


class PeopleService:
    def __init__(self, people_repository: PeopleRepository) -> None:
        """Initializes the PeopleService with a PeopleRepository.

        Args:
            people_repository (PeopleRepository): The repository to manage
                people data.
        """
        self.people_repository = people_repository

    def add_person(
            self,
            first_name: str,
            last_name: str,
            birthday: str,
            pin: str,
            is_admin: bool
    ) -> None:
        """Adds a new person to the repository.

        Args:
            first_name (str): The first name of the person.
            last_name (str): The last name of the person.
            birthday (str): The birthday of the person.
            pin (str): The PIN of the person.
            is_admin (bool): Whether the person is an admin.
        """
        return self.people_repository.add_person(
            first_name, last_name, birthday, pin, is_admin
        )

    def admins_exist(self) -> bool:
        """Checks if any admins exist in the repository.

        Returns:
            bool: True if admins exist, False otherwise.
        """
        return self.people_repository.admins_exist()

    def delete_person(self, person_id: int) -> None:
        """Deletes a person from the repository by their ID.

        Args:
            person_id (int): The ID of the person to delete.
        """
        self.people_repository.delete_person(person_id)

    def delete_person_and_adjust_sequence(self, person_id: int) -> None:
        """Deletes a person and adjusts the sequence numbers.

        Args:
            person_id (int): The ID of the person to delete.
        """
        person_to_delete = self.get_person_by_id(person_id)
        if person_to_delete:
            deleted_person_sequence = person_to_delete.sequence_num
            self.delete_person(person_id)
            remaining_people = self.get_all_people_in_sequence_order()
            for person in remaining_people:
                if person.sequence_num > deleted_person_sequence:
                    person.sequence_num -= 1
                    self.update_person(person)

    def get_next_person_by_person_id(
            self,
            current_person_id: int
    ) -> People:
        """Gets the next person by the current person's ID.

        Args:
            current_person_id (int): The ID of the current person.

        Returns:
            People: The next person's data.
        """
        return self.people_repository.get_next_person_by_person_id(
            current_person_id
        )

    def get_all_people(self) -> List[People]:
        """Gets all people from the repository.

        Returns:
            List[People]: A list of all people.
        """
        return self.people_repository.get_all_people()

    def get_all_people_in_sequence_order(self) -> List[People]:
        """Gets all people in sequence order.

        Returns:
            List[dict]: A list of all people in sequence order.
        """
        return self.people_repository.get_all_people_in_sequence_order()

    def get_person_by_id(self, person_id: int) -> Optional[People]:
        """Gets a person by their ID.

        Args:
            person_id (int): The ID of the person.

        Returns:
            Optional[dict]: The person's data or None if not found.
        """
        return self.people_repository.get_person_by_id(person_id)

    def get_person_by_pin(self, pin: str) -> Optional[People]:
        """Gets a person by their PIN.

        Args:
            pin (str): The PIN of the person.

        Returns:
            Optional[People]: The person object or None if not found.
        """
        return self.people_repository.get_person_by_pin(pin)

    def is_admin(self, pin: str) -> bool:
        """Checks if a person is an admin by their PIN.

        Args:
            pin (str): The PIN of the person.

        Returns:
            bool: True if the person is an admin, False otherwise.
        """
        return self.people_repository.is_admin(pin)

    def update_person(self, person: dict) -> People:
        """Updates a person's data.

        Args:
            person (dict): The person's data to update.
        Returns:
            People: The person object or None if not found.            
        """
        return self.people_repository.update_person(person)

    def update_pin(self, person_id: int, new_pin: str) -> None:
        """Updates a person's PIN.

        Args:
            person_id (int): The ID of the person.
            new_pin (str): The new PIN of the person.
        """
        self.people_repository.update_pin(person_id, new_pin)

    def update_sequence(self, person_id: int, new_sequence: int) -> None:
        """Updates a person's sequence number.

        Args:
            person_id (int): The ID of the person.
            new_sequence (int): The new sequence number.
        """
        self.people_repository.update_sequence(person_id, new_sequence)

    def verify_pin(self, person_id: int, pin: str) -> bool:
        """Verifies a person's PIN.

        Args:
            person_id (int): The ID of the person.
            pin (str): The PIN to verify.

        Returns:
            bool: True if the PIN is correct, False otherwise.
        """
        return self.people_repository.verify_pin(person_id, pin)
