from choreboss.repositories.chore_repository import ChoreRepository


class ChoreService:
    def __init__(self, chore_repository: ChoreRepository):
        self.chore_repository = chore_repository

    def add_chore(self, description):
        return self.chore_repository.add_chore(description)

    def get_all_chores(self):
        return self.chore_repository.get_all_chores()
