from choreboss.repositories.chore_repository import ChoreRepository


class ChoreService:
    def __init__(self, chore_repository: ChoreRepository):
        self.chore_repository = chore_repository

    def add_chore(self, name, description):
        return self.chore_repository.add_chore(name, description)

    def get_all_chores(self):
        return self.chore_repository.get_all_chores()

    def get_chore_by_id(self, chore_id):
        return self.chore_repository.get_chore_by_id(chore_id)
