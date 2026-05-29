"""
Alert fan-out engine.

For each detected policy change, looks up users who watch the affected country
and sends them an email via Resend, then records the alert in user_alerts.
"""

import os
from datetime import datetime, timezone

import resend

from db.client import admin_client
from services.change_detector import get_affected_users

resend.api_key = os.environ.get("RESEND_API_KEY", "")
_FROM = os.environ.get("RESEND_FROM_EMAIL", "onboarding@resend.dev")
_APP_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")


def _get_country_id(country_code: str) -> str | None:
    result = (
        admin_client()
        .table("countries")
        .select("id")
        .eq("code", country_code)
        .execute()
    )
    return result.data[0]["id"] if result.data else None


def _get_country_name(country_code: str) -> str:
    result = (
        admin_client()
        .table("countries")
        .select("name")
        .eq("code", country_code)
        .execute()
    )
    return result.data[0]["name"] if result.data else country_code


async def send_alert(
    user_id: str,
    email: str,
    country_code: str,
    country_name: str,
    change_summary: str,
    visa_type: str,
    source_url: str,
) -> bool:
    """Insert a user_alerts row and send an email via Resend. Returns True on success."""
    admin_client().table("user_alerts").insert({
        "user_id": user_id,
        "country_id": _get_country_id(country_code),
        "alert_type": "policy_change",
        "message": f"Policy change detected for {country_name} ({visa_type})",
        "plain_english": change_summary,
        "source_url": source_url,
        "sent_at": datetime.now(timezone.utc).isoformat(),
    }).execute()

    if not resend.api_key:
        return True  # no key configured — row written, email skipped

    body = (
        f"Hi,\n\n"
        f"A policy change was detected for {country_name} that may affect your Exit Plan.\n\n"
        f"Visa type: {visa_type}\n"
        f"Change: {change_summary}\n"
        f"Source: {source_url}\n\n"
        f"Log in to Exit Plan to see how this affects your ranking.\n"
        f"{_APP_URL}/results\n\n"
        f"— The Exit Plan Team"
    )

    try:
        resend.Emails.send({
            "from": _FROM,
            "to": email,
            "subject": f"Policy change: {country_name} {visa_type}",
            "text": body,
        })
        return True
    except Exception:
        return False


async def process_changes(changes: list[dict]) -> int:
    """Fan out alerts for every detected change. Returns total alerts sent."""
    total = 0
    for change in changes:
        country_name = _get_country_name(change["country_code"])
        users = await get_affected_users(change["country_code"])
        for user in users:
            ok = await send_alert(
                user_id=user["id"],
                email=user["email"],
                country_code=change["country_code"],
                country_name=country_name,
                change_summary=change.get("change_summary", "Policy content updated."),
                visa_type=change.get("visa_type", "General"),
                source_url=change.get("source_url", ""),
            )
            if ok:
                total += 1
    return total
