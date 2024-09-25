from sqlalchemy import Column, Integer, String
from choreboss.models import Base
from sqlalchemy.orm import relationship


class Person(Base):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

    chores = relationship('Chore', back_populates='person')
