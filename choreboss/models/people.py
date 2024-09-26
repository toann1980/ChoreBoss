from sqlalchemy import Boolean, Column, Date, Integer, String
from choreboss.models import Base
from choreboss.models.chore import Chore
from sqlalchemy.orm import relationship


class People(Base):
    __tablename__ = 'people'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    birthday = Column(Date, nullable=False)
    pin = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)

    chores = relationship(
        'Chore',
        back_populates='person_id_relationship',
        foreign_keys=[Chore.person_id]
    )
    completed_chores = relationship(
        'Chore',
        foreign_keys=[Chore.last_completed_id],
        back_populates='last_completed_id_person'
    )
