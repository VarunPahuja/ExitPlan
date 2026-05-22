"""
Personalization scoring engine.

Applies user-declared priority weights to research-backed country factor scores
(0-100 per dimension) and returns a fully ranked RankResponse with graph edges
derived from cosine similarity between country vectors.

Job market scores are field-specific (e.g. medicine vs. CS differ per country).
"""

import hashlib
import json
import math
from datetime import date

from data.country_scores import COUNTRY_DATA, COUNTRY_META
from models.profile import (
    CountryScore,
    GraphEdge,
    GraphNode,
    RankRequest,
    RankResponse,
)

FACTORS = ["job_market", "pr_timeline", "visa_ease", "salary_cost_ratio", "language"]

_VERDICT_PHRASES = {
    "job_market": "strong job market",
    "pr_timeline": "fast PR pathway",
    "visa_ease": "straightforward visa process",
    "salary_cost_ratio": "excellent salary-to-cost ratio",
    "language": "language advantage",
}

_FACTOR_LABELS = {
    "job_market": "job market",
    "pr_timeline": "PR timeline",
    "visa_ease": "visa ease",
    "salary_cost_ratio": "salary-cost ratio",
    "language": "language",
}


def _cosine_similarity(a: dict, b: dict) -> float:
    va = [a[f] for f in FACTORS]
    vb = [b[f] for f in FACTORS]
    dot = sum(x * y for x, y in zip(va, vb))
    mag_a = math.sqrt(sum(x ** 2 for x in va))
    mag_b = math.sqrt(sum(x ** 2 for x in vb))
    return dot / (mag_a * mag_b) if mag_a and mag_b else 0.0


def score_countries(request: RankRequest) -> RankResponse:
    field = request.field
    weights = {
        "job_market": request.weights.job_market,
        "pr_timeline": request.weights.pr_timeline,
        "visa_ease": request.weights.visa_ease,
        "salary_cost_ratio": request.weights.salary_cost_ratio,
        "language": request.weights.language,
    }
    today = date.today().isoformat()

    # Resolve field-specific job_market scores for each country upfront
    resolved: dict[str, dict] = {
        code: {
            "job_market": data["job_market"].get(field, 65),
            "pr_timeline": data["pr_timeline"],
            "visa_ease": data["visa_ease"],
            "salary_cost_ratio": data["salary_cost_ratio"],
            "language": data["language"],
        }
        for code, data in COUNTRY_DATA.items()
    }

    scored = []
    for code, factor_scores in resolved.items():
        data = COUNTRY_DATA[code]
        meta = COUNTRY_META[code]
        total = sum(factor_scores[f] * weights[f] for f in FACTORS)

        if total >= 80:
            tier = "great"
        elif total >= 60:
            tier = "good"
        elif total >= 40:
            tier = "moderate"
        else:
            tier = "low"

        top2 = sorted(FACTORS, key=lambda f: factor_scores[f] * weights[f], reverse=True)[:2]
        verdict = (
            f"{_VERDICT_PHRASES[top2[0]].capitalize()} and {_VERDICT_PHRASES[top2[1]]} "
            f"make {data['name']} your top match."
        )

        scored.append({
            "code": code,
            "data": data,
            "meta": meta,
            "factor_scores": factor_scores,
            "total": round(total, 2),
            "tier": tier,
            "verdict": verdict,
        })

    scored.sort(key=lambda x: x["total"], reverse=True)

    ranked = [
        CountryScore(
            rank=i + 1,
            country_code=item["code"],
            country_name=item["data"]["name"],
            total_score=item["total"],
            scores=item["factor_scores"],
            verdict=item["verdict"],
            tier=item["tier"],
            visa_types=item["meta"]["visa_types"],
            pr_timeline_years=item["meta"]["pr_timeline_years"],
            last_updated=today,
        )
        for i, item in enumerate(scored)
    ]

    nodes = [
        GraphNode(id=c.country_code, label=c.country_name, total_score=c.total_score, tier=c.tier)
        for c in ranked
    ]

    edges = []
    codes = list(COUNTRY_DATA.keys())
    for i in range(len(codes)):
        for j in range(i + 1, len(codes)):
            a, b = codes[i], codes[j]
            sim = _cosine_similarity(resolved[a], resolved[b])
            if sim > 0.85:
                shared = max(FACTORS, key=lambda f: (resolved[a][f] + resolved[b][f]) / 2)
                edges.append(GraphEdge(
                    source=a,
                    target=b,
                    similarity=round(sim, 3),
                    reason=f"Similar {_FACTOR_LABELS[shared]} profiles",
                ))

    profile_hash = hashlib.md5(
        json.dumps(request.model_dump(), sort_keys=True).encode()
    ).hexdigest()

    return RankResponse(
        ranked_countries=ranked,
        graph_data={
            "nodes": [n.model_dump() for n in nodes],
            "edges": [e.model_dump() for e in edges],
        },
        profile_hash=profile_hash,
        shareable_url=f"http://localhost:3000/results/{profile_hash}",
    )
