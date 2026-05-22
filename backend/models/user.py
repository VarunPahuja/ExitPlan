"""
Pydantic models for the /profile endpoint.
"""

from datetime import datetime
from pydantic import BaseModel

from models.profile import UserWeights


class ProfileUpdate(BaseModel):
    """Request body for PUT /profile — all fields optional."""
    nationality: str | None = None
    current_status: str | None = None
    field: str | None = None
    degree_level: str | None = None
    savings_range: str | None = None
    career_goal: str | None = None
    weights: UserWeights | None = None
    saved_countries: list[str] | None = None


class ProfileResponse(BaseModel):
    """Matches the public.users table schema returned from Supabase."""
    id: str
    email: str
    nationality: str | None = None
    current_status: str | None = None
    field: str | None = None
    degree_level: str | None = None
    savings_range: str | None = None
    career_goal: str | None = None
    weights: dict | None = None
    saved_countries: list[str] | None = None
    created_at: datetime | None = None
