from choreboss.models.chore import Chore
from choreboss.models import Base
from sqlalchemy.orm import sessionmaker


class ChoreRepository:
    def __init__(self, engine):
        self.session = sessionmaker(bind=engine)

    def add_chore(self, description):
        chore = Chore(description=description)
        self.session.add(chore)
        self.session.commit()
        self.session.close()
        return chore

    def get_all_chores(self):
        session = self.session()
        chores = session.query(Chore).all()
        session.close()
        return chores
