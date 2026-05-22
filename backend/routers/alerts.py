"""
/alerts router — manage and retrieve policy-change alerts for the authenticated
user.

The change_detector service publishes events to Upstash Redis; the alert_engine
workers fan them out to users who have matching country subscriptions.  This
router exposes the read side: list alerts and mark them as read.
"""

from fastapi import APIRouter, Depends
from services.auth import get_current_user

router = APIRouter()


@router.get("/")
async def list_alerts(user_id: str = Depends(get_current_user)):
    """Return all unread policy-change alerts for the current user."""
    return {"message": "alerts endpoint — coming soon"}


@router.post("/{alert_id}/read")
async def mark_alert_read(alert_id: str, user_id: str = Depends(get_current_user)):
    """Mark a single alert as read."""
    return {"message": f"alert {alert_id} marked read — coming soon"}


@router.post("/subscribe")
async def subscribe_country(user_id: str = Depends(get_current_user)):
    """Subscribe the current user to policy-change alerts for a country."""
    return {"message": "subscribe — coming soon"}


@router.delete("/subscribe/{country_code}")
async def unsubscribe_country(country_code: str, user_id: str = Depends(get_current_user)):
    """Remove a country subscription for the current user."""
    return {"message": f"unsubscribe {country_code} — coming soon"}
