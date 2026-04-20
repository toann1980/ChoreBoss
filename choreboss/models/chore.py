"""Chore model."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, validates

from choreboss.models import Base


class Chore(Base):
    """Chore model for household tasks."""

    __tablename__ = "chores"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(500), nullable=False)
    person_id = Column(Integer, ForeignKey("people.id"), nullable=True)
    last_completed_date = Column(DateTime, nullable=True, default=None)
    last_completed_id = Column(Integer, ForeignKey("people.id"), nullable=True)
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

    person = relationship(
        "People",
        back_populates="chores",
        foreign_keys=[person_id],
        primaryjoin="Chore.person_id==People.id",
    )
    last_completed_person = relationship(
        "People",
        foreign_keys=[last_completed_id],
        primaryjoin="Chore.last_completed_id==People.id",
    )

    @validates("id")
    def validate_id(self, key, value):
        """Validate ID field."""
        if not isinstance(value, int):
            raise AttributeError(f"{key} must be an integer")
        return value

    @validates("name")
    def validate_name(self, key, value):
        """Validate name field."""
        if not isinstance(value, str):
            raise AttributeError(f"{key} must be a string")
        if not 8 <= len(value) <= 50:
            raise AttributeError(
                f"{key} must be between 8 and 50 characters"
            )
        return value

    @validates("description")
    def validate_description(self, key, value):
        """Validate description field."""
        if not isinstance(value, str):
            raise AttributeError(f"{key} must be a string")
        if not 10 <= len(value) <= 500:
            raise AttributeError(
                f"{key} must be between 10 and 500 characters"
            )
        return value

    @validates("person_id")
    def validate_person_id(self, key, value):
        """Validate person_id field."""
        if value is not None and not isinstance(value, int):
            raise AttributeError(f"{key} must be an integer")
        return value

    @validates("last_completed_date")
    def validate_last_completed_date(self, key, value):
        """Validate last_completed_date field."""
        if value is not None and not isinstance(value, datetime):
            raise AttributeError(f"{key} must be a datetime object")
        return value

    @validates("last_completed_id")
    def validate_last_completed_id(self, key, value):
        """Validate last_completed_id field."""
        if value is not None and not isinstance(value, int):
            raise AttributeError(f"{key} must be an integer")
        return value
