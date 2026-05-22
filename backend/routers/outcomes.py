"""
/outcomes router — read-only feed of real immigration outcome stories.

Stories are seeded manually and displayed in the Lovable outcome feed.  They
provide social proof and ground the AI-generated advice in lived experience.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_outcomes(country: str | None = None, limit: int = 20, offset: int = 0):
    """Return paginated outcome stories, optionally filtered by country."""
    return {"message": "outcomes endpoint — coming soon"}


@router.get("/{outcome_id}")
async def get_outcome(outcome_id: str):
    """Return a single outcome story by id."""
    return {"message": f"outcome {outcome_id} — coming soon"}
