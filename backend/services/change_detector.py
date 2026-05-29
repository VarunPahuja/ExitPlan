"""
Policy change detector.

After each scrape run, diffs newly scraped text against existing policy_chunks.
Flags meaningful changes (>10% length diff or key term changes) and stores them
in policy_changes for the alert engine to fan out.
"""

import re
from datetime import datetime, timezone

from db.client import admin_client

# Regex for salary figures, years, percentages, thresholds
_KEY_TERMS = re.compile(r"\b(\d{1,3}(?:,\d{3})*|\d+%|\d{4})\b")


async def detect_changes(new_docs: list[dict]) -> list[dict]:
    """
    Compare new scraped docs against existing policy_chunks.
    Returns list of detected change dicts.
    """
    changes = []
    for doc in new_docs:
        country_code = doc.get("country_code", "")
        visa_type = doc.get("visa_type", "")
        source_url = doc.get("url", "")
        new_text = doc.get("text", "")

        if not country_code or not new_text:
            continue

        result = (
            admin_client()
            .table("policy_chunks")
            .select("content")
            .eq("country_code", country_code)
            .eq("source_url", source_url)
            .execute()
        )
        if not result.data:
            continue  # first scrape of this URL — not a change

        old_text = " ".join(row["content"] for row in result.data)

        if _is_meaningful_change(old_text, new_text):
            changes.append({
                "country_code": country_code,
                "visa_type": visa_type,
                "source_url": source_url,
                "change_summary": _summarize_change(old_text, new_text),
                "old_snippet": old_text[:500],
                "new_snippet": new_text[:500],
            })

    return changes


def _is_meaningful_change(old_text: str, new_text: str) -> bool:
    old_clean = " ".join(old_text.split())
    new_clean = " ".join(new_text.split())

    if old_clean == new_clean:
        return False

    if len(old_clean) > 0:
        ratio = abs(len(new_clean) - len(old_clean)) / len(old_clean)
        if ratio > 0.10:
            return True

    # Flag if numeric values (salaries, dates, thresholds) changed
    old_numbers = set(_KEY_TERMS.findall(old_clean))
    new_numbers = set(_KEY_TERMS.findall(new_clean))
    return old_numbers != new_numbers


def _summarize_change(old_text: str, new_text: str) -> str:
    old_words = len(old_text.split())
    new_words = len(new_text.split())
    if new_words > old_words * 1.1:
        return "Policy page was expanded with new information."
    if new_words < old_words * 0.9:
        return "Policy page content was reduced — some requirements may have been removed."
    return "Policy page was updated — key figures or dates may have changed."


async def store_change(change: dict) -> str:
    """Insert into policy_changes. Returns the new row's id."""
    country_result = (
        admin_client()
        .table("countries")
        .select("id")
        .eq("code", change["country_code"])
        .execute()
    )
    country_id = country_result.data[0]["id"] if country_result.data else None

    result = (
        admin_client()
        .table("policy_changes")
        .insert({
            "country_id": country_id,
            "visa_type": change.get("visa_type", ""),
            "change_summary": change.get("change_summary", ""),
            "detected_at": datetime.now(timezone.utc).isoformat(),
            "old_value": change.get("old_snippet", "")[:500],
            "new_value": change.get("new_snippet", "")[:500],
        })
        .execute()
    )
    return result.data[0]["id"] if result.data else ""


async def get_affected_users(country_code: str) -> list[dict]:
    """Return [{user_id, email}] for users who watch this country."""
    result = (
        admin_client()
        .table("users")
        .select("id, email")
        .contains("saved_countries", [country_code])
        .execute()
    )
    return result.data or []
