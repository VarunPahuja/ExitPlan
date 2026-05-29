"""
/outcomes router — community immigration outcome stories.

Stories are seeded via backend/seed_outcomes.py.  Public GET with optional
filtering; authenticated POST for user submissions.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from db.client import admin_client
from services.auth import get_current_user

router = APIRouter()


class OutcomeSubmission(BaseModel):
    nationality: str = "IN"
    field: str
    degree_level: str
    destination_country: str
    visa_type: str
    months_to_job: int | None = None
    summary: str
    year: int | None = None


@router.get("/")
async def list_outcomes(
    country: str | None = None,
    field: str | None = None,
    limit: int = 20,
    offset: int = 0,
):
    """Return paginated outcome stories, optionally filtered by country code or field."""
    query = (
        admin_client()
        .table("outcomes")
        .select("*")
        .order("year", desc=True)
        .range(offset, offset + limit - 1)
    )

    if country:
        query = query.eq("destination_country", country.upper())
    if field:
        query = query.ilike("field", f"%{field}%")

    result = query.execute()
    return result.data or []


@router.get("/{outcome_id}")
async def get_outcome(outcome_id: str):
    """Return a single outcome story by id."""
    result = (
        admin_client()
        .table("outcomes")
        .select("*")
        .eq("id", outcome_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Outcome not found")
    return result.data[0]


@router.post("/", status_code=201)
async def submit_outcome(
    body: OutcomeSubmission,
    user_id: str = Depends(get_current_user),
):
    """Submit a new immigration outcome story. Auth required."""
    result = (
        admin_client()
        .table("outcomes")
        .insert({
            "nationality": body.nationality,
            "field": body.field,
            "degree_level": body.degree_level,
            "destination_country": body.destination_country.upper(),
            "visa_type": body.visa_type,
            "months_to_job": body.months_to_job,
            "summary": body.summary,
            "year": body.year,
            "verified": False,
            "submitted_by": user_id,
        })
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to submit outcome")
    return result.data[0]
