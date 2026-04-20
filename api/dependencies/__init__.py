"""Dependencies package initialization."""

from __future__ import annotations

from api.dependencies.auth import (
    create_access_token,
    get_admin_person,
    get_current_person,
)
from api.dependencies.db import get_session

__all__ = [
    "get_session",
    "get_current_person",
    "get_admin_person",
    "create_access_token",
]
