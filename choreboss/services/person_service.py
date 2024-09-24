from choreboss.repositories.person_repository import PersonRepository


class PersonService:
    def __init__(self, person_repository: PersonRepository):
        self.person_repository = person_repository

    def add_person(self, name):
        return self.person_repository.add_person(name)

    def get_all_people(self):
        return self.person_repository.get_all_people()
