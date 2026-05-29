"""
/country router — static scoring data + live DB policy changes for a single country.
"""

from fastapi import APIRouter, HTTPException

from data.country_scores import COUNTRY_DATA, COUNTRY_META
from db.client import admin_client

router = APIRouter()


@router.get("/{code}")
async def get_country(code: str):
    """
    Returns full country info:
      1. Static scores and metadata from country_scores.py
      2. Recent policy changes from policy_changes table
      3. Key policy chunks from policy_chunks table
    """
    code = code.upper()
    if code not in COUNTRY_DATA:
        raise HTTPException(status_code=404, detail=f"Country {code} not found")

    data = COUNTRY_DATA[code]
    meta = COUNTRY_META[code]

    country_id_result = (
        admin_client()
        .table("countries")
        .select("id")
        .eq("code", code)
        .execute()
    )

    recent_changes: list = []
    key_facts: list = []

    if country_id_result.data:
        country_id = country_id_result.data[0]["id"]

        changes_result = (
            admin_client()
            .table("policy_changes")
            .select("*")
            .eq("country_id", country_id)
            .order("detected_at", desc=True)
            .limit(5)
            .execute()
        )
        recent_changes = changes_result.data or []

        chunks_result = (
            admin_client()
            .table("policy_chunks")
            .select("content, visa_type, source_url")
            .eq("country_id", country_id)
            .limit(3)
            .execute()
        )
        key_facts = chunks_result.data or []

    return {
        "code": code,
        "name": data["name"],
        "scores": {
            "pr_timeline": data["pr_timeline"],
            "visa_ease": data["visa_ease"],
            "salary_cost_ratio": data["salary_cost_ratio"],
            "language": data["language"],
        },
        "visa_types": meta["visa_types"],
        "pr_timeline_years": meta["pr_timeline_years"],
        "recent_changes": recent_changes,
        "key_facts": key_facts,
    }
