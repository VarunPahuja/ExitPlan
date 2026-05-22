"""
Pydantic models for country data snapshots and ranked results.

CountrySnapshot holds the raw dimension values stored in Supabase.
CountryScore adds the computed weighted score returned by the ranking engine.
"""

from pydantic import BaseModel


class CountrySnapshot(BaseModel):
    code: str
    name: str
    job_market_score: float
    cost_of_living_index: float
    safety_index: float
    climate_score: float
    english_proficiency: float
    last_scraped_at: str


class CountryScore(CountrySnapshot):
    composite_score: float
    rank: int
    score_breakdown: dict[str, float]


class CountryDetail(CountrySnapshot):
    """Extended model including policy document metadata for the detail view."""
    policy_doc_count: int
    last_policy_change: str | None = None
