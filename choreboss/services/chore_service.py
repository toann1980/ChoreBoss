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
        self.chore_repository = chore_repository
        self.people_repository = people_repository

    def add_chore(self, name, description):
        self.chore_repository.add_chore(name, description)

    def complete_chore(self, chore):
        self.chore_repository.complete_chore(chore)

        chore.person_id = self.people_repository.get_next_person_by_person_id(
            chore.person_id
        ).id
        self.update_chore(chore)

    def delete_chore(self, chore_id):
        self.chore_repository.delete_chore(chore_id)

    def get_all_chores(self):
        return self.chore_repository.get_all_chores()

    def get_chore_by_id(self, chore_id):
        return self.chore_repository.get_chore_by_id(chore_id)

    def update_chore(self, chore):
        self.chore_repository.update_chore(chore)
