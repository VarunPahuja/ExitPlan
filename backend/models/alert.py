"""
Pydantic models for the /alerts endpoints.
"""

from datetime import datetime
from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: str
    country_id: str | None = None
    alert_type: str
    message: str
    plain_english: str | None = None
    sent_at: datetime | None = None
    read_at: datetime | None = None
    source_url: str | None = None


class AlertPreferences(BaseModel):
    watched_countries: list[str] = []
    email_alerts: bool = True
    alert_types: list[str] = []
