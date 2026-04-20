import bcrypt
import datetime
from sqlalchemy import Boolean, Column, Date, Integer, String
from sqlalchemy.orm import relationship, validates
from choreboss.models import Base
from choreboss.models.chore import Chore


class People(Base):
    __tablename__ = 'people'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    birthday = Column(Date, nullable=False)
    pin = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    sequence_num = Column(Integer, nullable=False)

    chore_person_id_back_populate = relationship(
        'Chore',
        back_populates='person_id_foreign_key',
        foreign_keys=[Chore.person_id]
    )
    last_completed_id_back_populate = relationship(
        'Chore',
        back_populates='last_completed_id_foreign_key',
        foreign_keys=[Chore.last_completed_id]
    )

    @validates('first_name')
    def validate_first_name(self, key, value):
        """Validates the first name attribute."""
        if not isinstance(value, str):
            raise AttributeError(f'{key} must be a string')
        if not 2 <= len(value) <= 50:
            raise AttributeError(f'{key} must be between 2 and 50 characters')
        return value

    @validates('last_name')
    def validate_last_name(self, key, value):
        """Validates the last name attribute."""
        if not isinstance(value, str):
            raise AttributeError(f'{key} must be a string')
        if not 2 <= len(value) <= 50:
            raise AttributeError(f'{key} must be between 2 and 50 characters')
        return value

    @validates('birthday')
    def validate_birthday(self, key, value):
        """Validates the birthday attribute."""
        if not isinstance(value, datetime.date):
            raise AttributeError(f'{key} must be a datetime.date object')
        return value

    @validates('pin')
    def validate_pin(self, key, value):
        """Validates the pin attribute."""
        if not isinstance(value, str):
            raise AttributeError(f'{key} must be a string')
        if not 4 <= len(value) <= 255:
            raise AttributeError(f'{key} must be between 6 and 255 characters')
        return value

    @validates('is_admin')
    def validate_is_admin(self, key, value):
        """Validates the is_admin attribute."""
        if not isinstance(value, bool):
            raise AttributeError(f'{key} must be a boolean')
        return value

    @validates('sequence_num')
    def validate_sequence_num(self, key, value):
        """Validates the sequence_num attribute."""
        if not isinstance(value, int):
            raise AttributeError(f'{key} must be an integer')
        return value

    def set_pin(self, pin):
        """Sets the pin attribute after hashing it."""
        hashed = bcrypt.hashpw(pin.encode('utf-8'), bcrypt.gensalt())
        self.pin = hashed.decode('utf-8')

    def verify_pin(self, pin):
        """Verifies the pin attribute"""
        return bcrypt.checkpw(pin.encode('utf-8'), self.pin.encode('utf-8'))
