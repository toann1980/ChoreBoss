"""People model."""

from __future__ import annotations

import bcrypt
from datetime import date, datetime

from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String
from sqlalchemy.orm import relationship, validates

from choreboss.models import Base


class People(Base):
    """People model for household members."""

    __tablename__ = "people"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    birthday = Column(Date, nullable=False)
    pin = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    sequence_num = Column(Integer, nullable=False)
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    chores = relationship(
        "Chore",
        back_populates="person",
        foreign_keys="Chore.person_id",
        viewonly=False,
    )

    @validates("first_name")
    def validate_first_name(self, key, value):
        """Validate first_name field."""
        if not isinstance(value, str):
            raise AttributeError(f"{key} must be a string")
        if not 2 <= len(value) <= 50:
            raise AttributeError(
                f"{key} must be between 2 and 50 characters"
            )
        return value

    @validates("last_name")
    def validate_last_name(self, key, value):
        """Validate last_name field."""
        if not isinstance(value, str):
            raise AttributeError(f"{key} must be a string")
        if not 2 <= len(value) <= 50:
            raise AttributeError(
                f"{key} must be between 2 and 50 characters"
            )
        return value

    @validates("birthday")
    def validate_birthday(self, key, value):
        """Validate birthday field."""
        if not isinstance(value, date):
            raise AttributeError(f"{key} must be a datetime.date object")
        return value

    @validates("pin")
    def validate_pin(self, key, value):
        """Validate pin field."""
        if not isinstance(value, str):
            raise AttributeError(f"{key} must be a string")
        if not 4 <= len(value) <= 255:
            raise AttributeError(
                f"{key} must be between 4 and 255 characters"
            )
        return value

    @validates("is_admin")
    def validate_is_admin(self, key, value):
        """Validate is_admin field."""
        if not isinstance(value, bool):
            raise AttributeError(f"{key} must be a boolean")
        return value

    @validates("sequence_num")
    def validate_sequence_num(self, key, value):
        """Validate sequence_num field."""
        if not isinstance(value, int):
            raise AttributeError(f"{key} must be an integer")
        return value

    def set_pin(self, pin: str) -> None:
        """Hash and set PIN.

        Args:
            pin: Plain text PIN to hash.
        """
        hashed = bcrypt.hashpw(pin.encode("utf-8"), bcrypt.gensalt())
        self.pin = hashed.decode("utf-8")

    def verify_pin(self, pin: str) -> bool:
        """Verify PIN against hash.

        Args:
            pin: Plain text PIN to verify.

        Returns:
            bool: True if PIN matches.
        """
        return bcrypt.checkpw(pin.encode("utf-8"), self.pin.encode("utf-8"))
