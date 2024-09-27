from choreboss.models.people import People
from choreboss.models import Base
from sqlalchemy.orm import sessionmaker, joinedload


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
            is_admin=is_admin
        )
        session.add(person)
        session.commit()
        session.close()
        return person

    def get_all_people(self):
        session = self.Session()
        people = session.query(People).options(
            joinedload(People.chores),
            joinedload(People.completed_chores)
        ).all()
        session.close()
        return people

    def get_person_by_id(self, person_id):
        session = self.Session()
        person = session.query(People).options(
            joinedload(People.chores),
            joinedload(People.completed_chores)
        ).filter(People.id == person_id).first()
        session.close()
        return person

    def admins_exist(self):
        session = self.Session()
        admin_exists = session.query(People).filter_by(
            is_admin=True).first() is not None
        session.close()
        return admin_exists
