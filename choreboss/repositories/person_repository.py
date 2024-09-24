from choreboss.models.person import Person
from choreboss.models import Base
from sqlalchemy.orm import sessionmaker


class PersonRepository:
    def __init__(self, engine):
        self.Session = sessionmaker(bind=engine)

    def add_person(self, name):
        session = self.Session()
        person = Person(name=name)
        session.add(person)
        session.commit()
        session.close()
        return person

    def get_all_people(self):
        session = self.Session()
        people = session.query(Person).all()
        session.close()
        return people
