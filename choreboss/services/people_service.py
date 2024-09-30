from choreboss.repositories.people_repository import PeopleRepository


class PeopleService:
    def __init__(self, people_repository: PeopleRepository):
        self.people_repository = people_repository

    def add_person(self, first_name, last_name, birthday, pin, is_admin):
        return self.people_repository.add_person(
            first_name, last_name, birthday, pin, is_admin
        )

    def get_all_people(self):
        return self.people_repository.get_all_people()

    def get_person_by_id(self, person_id):
        return self.people_repository.get_person_by_id(person_id)

    def get_person_by_pin(self, pin):
        return self.people_repository.get_person_by_pin(pin)

    def admins_exist(self):
        return self.people_repository.admins_exist()

    def verify_pin(self, person_id, pin):
        person = self.people_repository.get_person_by_id(person_id)
        if person and person.verify_pin(pin):
            return True
        return False
