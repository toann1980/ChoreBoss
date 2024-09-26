from choreboss.repositories.people_repository import PeopleRepository


class PeopleService:
    def __init__(self, people_repository: PeopleRepository):
        self.people_repository = people_repository

    def add_person(self, first_name, last_name, birthday):
        return self.people_repository.add_person(first_name, last_name, birthday)

    def get_all_people(self):
        return self.people_repository.get_all_people()
