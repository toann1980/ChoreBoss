from choreboss.repositories.chore_repository import ChoreRepository
from choreboss.models.people import People
from choreboss.repositories.people_repository import PeopleRepository
from choreboss.services.people_service import PeopleService


class ChoreService:
    def __init__(
            self,
            chore_repository: ChoreRepository,
            people_repository: PeopleRepository
    ) -> None:
        """Initializes the ChoreService.

        Args:
            chore_repository (ChoreRepository): The repository for chore data.
            people_repository (PeopleRepository): The repository for people data.
        """
        self.chore_repository = chore_repository
        self.people_repository = people_repository

    def add_chore(self, name, description):
        """Adds a new chore.

        Args:
            name (str): The name of the chore.
            description (str): The description of the chore.
        """
        self.chore_repository.add_chore(name, description)

    def complete_chore(self, chore):
        """Marks a chore as complete and assigns it to the next person.

        Args:
            chore (Chore): The chore to be completed.
        """
        self.chore_repository.complete_chore(chore)

        chore.person_id = self.people_repository.get_next_person_by_person_id(
            chore.person_id
        ).id
        self.update_chore(chore)

    def delete_chore(self, chore_id):
        """Deletes a chore by its ID.

        Args:
            chore_id (int): The ID of the chore to be deleted.
        """
        self.chore_repository.delete_chore(chore_id)

    def get_all_chores(self):
        """Retrieves all chores.

        Returns:
            list: A list of all chores.
        """
        return self.chore_repository.get_all_chores()

    def get_chore_by_id(self, chore_id):
        """Retrieves a chore by its ID.

        Args:
            chore_id (int): The ID of the chore to be retrieved.

        Returns:
            Chore: The chore with the specified ID.
        """
        return self.chore_repository.get_chore_by_id(chore_id)

    def update_chore(self, chore):
        """Updates a chore.

        Args:
            chore (Chore): The chore to be updated.
        """
        self.chore_repository.update_chore(chore)
