from choreboss.models.people import People
from choreboss.models import Base
from sqlalchemy.orm import sessionmaker


class PeopleRepository:
    def __init__(self, engine):
        self.Session = sessionmaker(bind=engine)

    def add_person(self, first_name, last_name, age):
        session = self.Session()
        person = People(first_name=first_name, last_name=last_name, age=age)
        session.add(person)
        session.commit()
        session.close()
        return person

    def get_all_people(self):
        session = self.Session()
        people = session.query(People).all()
        session.close()
        return people
