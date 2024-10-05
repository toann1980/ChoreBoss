from choreboss.repositories.people_repository import PeopleRepository


class PeopleService:
    def __init__(self, people_repository: PeopleRepository):
        self.people_repository = people_repository

    def add_person(self, first_name, last_name, birthday, pin, is_admin):
        return self.people_repository.add_person(
            first_name, last_name, birthday, pin, is_admin
        )

    def admins_exist(self):
        return self.people_repository.admins_exist()

    def delete_person(self, person_id):
        return self.people_repository.delete_person(person_id)

    def delete_person_and_adjust_sequence(self, person_id):
        person_to_delete = self.get_person_by_id(person_id)
        if person_to_delete:
            deleted_person_sequence = person_to_delete.sequence_num
            self.delete_person(person_id)
            remaining_people = self.get_all_people_in_sequence_order()
            for person in remaining_people:
                if person.sequence_num > deleted_person_sequence:
                    person.sequence_num -= 1
                    self.update_person(person)

    def get_next_person_by_person_id(self, current_person_id):
        return self.people_repository.get_next_person_by_person_id(current_person_id)

    def get_next_sequence_num_by_person_id(self):
        return self.people_repository.get_next_sequence_num_by_person_id()

    def get_all_people(self):
        return self.people_repository.get_all_people()

    def get_all_people_in_sequence_order(self):
        return self.people_repository.get_all_people_in_sequence_order()

    def get_person_by_id(self, person_id):
        return self.people_repository.get_person_by_id(person_id)

    def get_person_by_pin(self, pin):
        return self.people_repository.get_person_by_pin(pin)

    def is_admin(self, pin):
        return self.people_repository.is_admin(pin)

    def update_pin(self, person_id, new_pin):
        return self.people_repository.update_pin(person_id, new_pin)

    def update_person(self, person):
        return self.people_repository.update_person(person)

    def update_sequence(self, person_id, new_sequence):
        return self.people_repository.update_sequence(person_id, new_sequence)

    def verify_pin(self, person_id, pin):
        return self.people_repository.verify_pin(person_id, pin)
