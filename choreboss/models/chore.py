from sqlalchemy import Column, DateTime, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from choreboss.models import Base


class Chore(Base):
    __tablename__ = 'chores'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(200), nullable=False)
    person_id = Column(Integer, ForeignKey('people.id'), nullable=True)
    last_completed_date = Column(DateTime, nullable=True, default=None)
    last_completed_id = Column(Integer, ForeignKey('people.id'), nullable=True)

    person_id_foreign_key = relationship(
        'People',
        back_populates='chore_person_id_back_populate',
        foreign_keys=[person_id]
    )
    last_completed_id_foreign_key = relationship(
        'People',
        back_populates='last_completed_id_back_populate',
        foreign_keys=[last_completed_id]
    )
