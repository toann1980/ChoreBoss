from choreboss.models.chore import Chore
from choreboss.models import Base
from sqlalchemy.orm import sessionmaker


class ChoreRepository:
    def __init__(self, engine):
        self.Session = sessionmaker(bind=engine)

    def add_chore(self, description):
        session = self.Session()
        chore = Chore(description=description)
        session.add(chore)
        session.commit()
        session.close()
        return chore

    def get_all_chores(self):
        session = self.Session()
        chores = session.query(Chore).all()
        session.close()
        return chores
