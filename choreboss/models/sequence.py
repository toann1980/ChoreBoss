from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from choreboss.models import Base


class Sequence(Base):
    __tablename__ = 'sequences'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('people.id'), nullable=False)
    sequence = Column(Integer, nullable=False)

    person_id_foreign_key = relationship(
        'People',
        back_populates='sequence_person_id_back_populate',
        foreign_keys=[person_id]
    )
