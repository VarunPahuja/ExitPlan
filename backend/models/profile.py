"""
Pydantic models for rank requests and responses.
"""

from pydantic import BaseModel, model_validator


class UserWeights(BaseModel):
    job_market: float
    pr_timeline: float
    visa_ease: float
    salary_cost_ratio: float
    language: float

    @model_validator(mode="after")
    def normalise(self) -> "UserWeights":
        total = (
            self.job_market + self.pr_timeline + self.visa_ease
            + self.salary_cost_ratio + self.language
        )
        if total == 0:
            raise ValueError("Weights cannot all be zero")
        if abs(total - 1.0) > 1e-6:
            self.job_market /= total
            self.pr_timeline /= total
            self.visa_ease /= total
            self.salary_cost_ratio /= total
            self.language /= total
        return self


class RankRequest(BaseModel):
    nationality: str
    current_status: str  # student | post_study | employed
    field: str
    degree_level: str    # bachelors | masters | phd | diploma
    savings_range: str   # 0_5L | 5_15L | 15L_plus
    career_goal: str     # long_term_pr | work_experience | return_home
    weights: UserWeights


class CountryScore(BaseModel):
    rank: int
    country_code: str
    country_name: str
    total_score: float
    scores: dict           # job_market, pr_timeline, visa_ease, salary_cost_ratio, language — all 0-100
    verdict: str
    tier: str              # great | good | moderate | low
    visa_types: list[str]
    pr_timeline_years: int
    last_updated: str


class GraphNode(BaseModel):
    id: str
    label: str
    total_score: float
    tier: str


class GraphEdge(BaseModel):
    source: str
    target: str
    similarity: float
    reason: str


class RankResponse(BaseModel):
    ranked_countries: list[CountryScore]
    graph_data: dict       # {nodes: list[GraphNode], edges: list[GraphEdge]}
    profile_hash: str
    shareable_url: str
