from choreboss.models.chore import Chore
from choreboss.models import Base
from sqlalchemy.orm import sessionmaker, joinedload


class ChoreRepository:
    def __init__(self, engine):
        self.Session = sessionmaker(bind=engine)

    def add_chore(self, name, description):
        session = self.Session()  # Create a session instance
        chore = Chore(name=name, description=description)
        session.add(chore)
        session.commit()
        session.close()

    def get_all_chores(self):
        session = self.Session()
        chores = session.query(Chore).options(
            joinedload(Chore.person_id_relationship),
            joinedload(Chore.last_completed_id_person)
        ).all()
        session.close()
        return chores

    def get_chore_by_id(self, chore_id):
        session = self.Session()
        chore = session.query(Chore).options(
            joinedload(Chore.person_id_relationship),
            joinedload(Chore.last_completed_id_person)
        ).filter_by(id=chore_id).first()
        session.close()
        return chore
