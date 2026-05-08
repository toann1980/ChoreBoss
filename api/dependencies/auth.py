"""JWT authentication configuration."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from choreboss.config import get_config

config = get_config()
security = HTTPBearer(auto_error=False)


def create_access_token(
    person_id: int,
    is_admin: bool,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT access token.

    Args:
        person_id: Person ID to encode in token.
        is_admin: Whether person is admin.
        expires_delta: Token expiration delta (default 7 days).

    Returns:
        str: Encoded JWT token.
    """
    if expires_delta is None:
        expires_delta = timedelta(days=7)

    to_encode = {
        "sub": str(person_id),
        "is_admin": is_admin,
        "exp": datetime.now(timezone.utc) + expires_delta,
    }

    encoded_jwt = jwt.encode(
        to_encode,
        config.secret_key,
        algorithm="HS256",
    )

    return encoded_jwt


async def get_current_person(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict[str, Any]:
    """Validate JWT token and return person data.

    Args:
        credentials: HTTP bearer credentials from request.

    Returns:
        dict: Decoded token payload.

    Raises:
        HTTPException: If token is invalid or expired.
    """
    token = request.session.get("token") if hasattr(request, "session") else None
    if not token and credentials is not None:
        token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        payload = jwt.decode(
            token,
            config.secret_key,
            algorithms=["HS256"],
        )
        person_id: str | None = payload.get("sub")
        is_admin: bool = payload.get("is_admin", False)

        if person_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        return {
            "person_id": int(person_id),
            "is_admin": is_admin,
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


async def get_admin_person(
    current_person: dict[str, Any] = Depends(get_current_person),
) -> dict[str, Any]:
    """Ensure current person is admin.

    Args:
        current_person: Current authenticated person.

    Returns:
        dict: Authenticated person data if admin.

    Raises:
        HTTPException: If person is not admin.
    """
    if not current_person["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_person
