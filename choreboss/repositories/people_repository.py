import bcrypt

from choreboss.models.people import People
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import func


class PeopleRepository:
    def __init__(self, engine):
        self.Session = sessionmaker(bind=engine)

    def add_person(self, first_name, last_name, birthday, pin, is_admin):
        session = self.Session()
        person = People(
            first_name=first_name,
            last_name=last_name,
            birthday=birthday,
            pin=pin,
            is_admin=is_admin,
            sequence_num=self.get_next_sequence_num()
        )
        person.set_pin(pin)
        session.add(person)
        session.commit()
        session.close()
        return person

    def admins_exist(self):
        session = self.Session()
        admin_exists = session.query(People).filter_by(
            is_admin=True).first() is not None
        session.close()
        return admin_exists

    def delete_person(self, person_id: int) -> None:
        session = self.Session()
        person = session.query(People).filter_by(id=person_id).first()
        if person:
            session.delete(person)
            session.commit()
        session.close()

    def get_all_people(self):
        session = self.Session()
        people = session.query(People).options(
            joinedload(People.chore_person_id_back_populate),
            joinedload(People.last_completed_id_back_populate)
        ).all()
        session.close()
        return people

    def get_all_people_in_sequence_order(self):
        people = self.get_all_people()
        sorted_people = sorted(people, key=lambda x: x.sequence_num)
        return sorted_people

    def get_next_sequence_num(self):
        session = self.Session()
        max_sequence_num = None
        try:
            max_sequence_num = session.query(
                func.max(People.sequence_num)).scalar()
        finally:
            session.close()

        return 1 if max_sequence_num is None else max_sequence_num + 1

    def get_person_by_id(self, person_id):
        session = self.Session()
        person = session.query(People).options(
            joinedload(People.chore_person_id_back_populate),
            joinedload(People.last_completed_id_back_populate)
        ).filter(People.id == person_id).first()
        session.close()
        return person

    def get_person_by_pin(self, pin):
        session = self.Session()
        people = session.query(People).all()
        session.close()
        for person in people:
            if bcrypt.checkpw(pin.encode('utf-8'), person.pin.encode('utf-8')):
                return person
        return None

    def update_person(self, person):
        session = self.Session()
        session.add(person)
        session.commit()
        session.close()
        return person

    def update_pin(self, person_id, new_pin):
        person = self.get_person_by_id(person_id)
        if person:
            person.set_pin(new_pin)
            self.update_person(person)

    def update_sequence(self, person_id, new_sequence):
        session = self.Session()
        person = session.query(People).filter_by(id=person_id).first()
        if person:
            person.sequence_num = new_sequence
            session.commit()
        session.close()
        return person

    def verify_pin(self, person_id, pin):
        person = self.get_person_by_id(person_id)
        if person and person.verify_pin(pin):
            return True
        return False
