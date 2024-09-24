from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from choreboss.models import Base


class Chore(Base):
    __tablename__ = 'chore'
    id = Column(Integer, primary_key=True)
    description = Column(String(200), nullable=False)
    person_id = Column(Integer, ForeignKey('person.id'), nullable=True)

    person = relationship('Person', back_populates='chores')
