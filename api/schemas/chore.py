"""Pydantic schemas for Chore operations."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class RecurrenceType(str, Enum):
    """Chore recurrence patterns."""

    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class ChoreBase(BaseModel):
    """Base chore schema with common fields."""

    name: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=10, max_length=500)
    person_id: int | None = None
    recurrence: RecurrenceType = RecurrenceType.NONE
    recurrence_day: int | None = None  # Day of week (0-6) or month (1-31)


class ChoreCreate(ChoreBase):
    """Schema for creating a chore."""

    pass


class ChoreUpdate(BaseModel):
    """Schema for updating a chore."""

    name: str | None = Field(None, min_length=1, max_length=50)
    description: str | None = Field(None, min_length=10, max_length=500)
    person_id: int | None = None
    recurrence: RecurrenceType | None = None
    recurrence_day: int | None = None


class ChoreRead(ChoreBase):
    """Schema for reading chore data from API."""

    id: int
    last_completed_date: datetime | None = None
    last_completed_id: int | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True
