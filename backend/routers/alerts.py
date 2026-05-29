"""
/alerts router — manage and retrieve policy-change alerts for the authenticated user.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from db.client import admin_client
from models.alert import AlertPreferences, AlertResponse
from services.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=list[AlertResponse])
async def list_alerts(user_id: str = Depends(get_current_user)):
    """Return the 50 most recent policy-change alerts for the current user."""
    result = (
        admin_client()
        .table("user_alerts")
        .select("*")
        .eq("user_id", user_id)
        .order("sent_at", desc=True)
        .limit(50)
        .execute()
    )
    return result.data or []


@router.get("/preferences")
async def get_preferences(user_id: str = Depends(get_current_user)):
    """Return the current user's alert preferences and watched countries."""
    result = (
        admin_client()
        .table("users")
        .select("saved_countries, alert_preferences")
        .eq("id", user_id)
        .execute()
    )
    if not result.data:
        return {"watched_countries": [], "email_alerts": True, "alert_types": []}
    row = result.data[0]
    prefs = row.get("alert_preferences") or {}
    return {
        "watched_countries": row.get("saved_countries") or [],
        "email_alerts": prefs.get("email_alerts", True),
        "alert_types": prefs.get("alert_types", []),
    }


@router.put("/preferences")
async def update_preferences(
    body: AlertPreferences,
    user_id: str = Depends(get_current_user),
):
    """Upsert the current user's alert preferences and watched countries."""
    result = (
        admin_client()
        .table("users")
        .update({
            "saved_countries": body.watched_countries,
            "alert_preferences": {
                "email_alerts": body.email_alerts,
                "alert_types": body.alert_types,
            },
        })
        .eq("id", user_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to update preferences")
    row = result.data[0]
    prefs = row.get("alert_preferences") or {}
    return {
        "watched_countries": row.get("saved_countries") or [],
        "email_alerts": prefs.get("email_alerts", True),
        "alert_types": prefs.get("alert_types", []),
    }


@router.post("/mark-read/{alert_id}")
async def mark_alert_read(alert_id: str, user_id: str = Depends(get_current_user)):
    """Set read_at on an alert that belongs to the current user."""
    result = (
        admin_client()
        .table("user_alerts")
        .update({"read_at": datetime.now(timezone.utc).isoformat()})
        .eq("id", alert_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"success": True}
