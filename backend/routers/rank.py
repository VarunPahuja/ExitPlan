"""
/rank router — returns a ranked list of immigration destination countries
tailored to the user's profile weights and priorities.

POST / accepts a RankRequest body, calls the scoring engine, and returns a
RankResponse with all 10 countries ranked, graph data, and a shareable URL.
GET /preview returns a demo ranking with default equal weights (no auth required).
"""

from fastapi import APIRouter

from models.profile import RankRequest, RankResponse, UserWeights
from services.scoring import score_countries

router = APIRouter()


@router.post("/", response_model=RankResponse)
async def rank_countries(request: RankRequest) -> RankResponse:
    """Return ranked countries scored against the user's declared weights."""
    return score_countries(request)


@router.get("/preview")
async def rank_preview():
    """Return a demo ranking with equal weights across all five factors."""
    demo = RankRequest(
        nationality="IN",
        current_status="student",
        field="computer_science",
        degree_level="masters",
        savings_range="5_15L",
        career_goal="long_term_pr",
        weights=UserWeights(
            job_market=0.2,
            pr_timeline=0.2,
            visa_ease=0.2,
            salary_cost_ratio=0.2,
            language=0.2,
        ),
    )
    return score_countries(demo)
