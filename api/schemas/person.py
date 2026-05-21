"""Pydantic schemas for People operations."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class PersonBase(BaseModel):
    """Base person schema with common fields."""

    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    login_name: str = Field(..., min_length=3, max_length=50)
    birthday: date
    is_admin: bool = False
    assign_chores: bool = True


class PersonCreate(PersonBase):
    """Schema for creating a person."""

    pin: str = Field(..., min_length=4, max_length=4)


class PersonUpdate(BaseModel):
    """Schema for updating a person."""

    first_name: str | None = Field(None, min_length=1, max_length=50)
    last_name: str | None = Field(None, min_length=1, max_length=50)
    login_name: str | None = Field(None, min_length=3, max_length=50)
    birthday: date | None = None
    is_admin: bool | None = None
    assign_chores: bool | None = None


class PersonRead(PersonBase):
    """Schema for reading person data from API."""

    id: int
    sequence_num: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class PersonLogin(BaseModel):
    """Schema for login with login_name and PIN."""

    login_name: str = Field(..., min_length=3, max_length=50)
    pin: str = Field(..., min_length=4, max_length=4)
