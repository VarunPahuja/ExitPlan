"""
JWT verification via Supabase Auth admin client.
"""

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from db.client import admin_client

_bearer = HTTPBearer(auto_error=False)


def verify_jwt(token: str) -> dict:
    """Call Supabase auth.get_user(token). Returns user data or raises HTTP 401."""
    try:
        response = admin_client().auth.get_user(token)
        if response.user is None:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return {"id": response.user.id, "email": response.user.email}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def get_user_id(token: str) -> str:
    """Return just the user ID from a valid JWT."""
    return verify_jwt(token)["id"]


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> str:
    """FastAPI dependency — extracts Bearer token and returns the user's UUID."""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    return get_user_id(credentials.credentials)


async def get_current_user_info(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict:
    """FastAPI dependency — returns {"id": str, "email": str} for the authed user."""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    return verify_jwt(credentials.credentials)
