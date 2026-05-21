"""Pydantic schemas for Auth responses."""

from __future__ import annotations

from pydantic import BaseModel


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    person_id: int
    is_admin: bool
