"""
Personalization scoring engine.

Applies user-declared priority weights to hardcoded country factor scores
(0-100 per dimension) and returns a fully ranked RankResponse with graph edges
derived from cosine similarity between country vectors.
"""

import hashlib
import json
import math
from datetime import date

from models.profile import (
    CountryScore,
    GraphEdge,
    GraphNode,
    RankRequest,
    RankResponse,
)

FACTORS = ["job_market", "pr_timeline", "visa_ease", "salary_cost_ratio", "language"]

COUNTRY_DATA: dict[str, dict] = {
    "GB": {
        "name": "United Kingdom",
        "job_market": 82, "pr_timeline": 65, "visa_ease": 85, "salary_cost_ratio": 68, "language": 98,
        "visa_types": ["Skilled Worker", "Graduate Route", "Global Talent"],
        "pr_timeline_years": 5,
    },
    "CA": {
        "name": "Canada",
        "job_market": 85, "pr_timeline": 70, "visa_ease": 88, "salary_cost_ratio": 72, "language": 95,
        "visa_types": ["Express Entry", "PNP", "Study Permit → PR"],
        "pr_timeline_years": 3,
    },
    "DE": {
        "name": "Germany",
        "job_market": 88, "pr_timeline": 75, "visa_ease": 80, "salary_cost_ratio": 85, "language": 55,
        "visa_types": ["EU Blue Card", "Job Seeker Visa", "Skilled Immigration Act"],
        "pr_timeline_years": 5,
    },
    "AU": {
        "name": "Australia",
        "job_market": 80, "pr_timeline": 72, "visa_ease": 82, "salary_cost_ratio": 70, "language": 96,
        "visa_types": ["Skilled Independent (189)", "Employer Sponsored (482)", "Graduate (485)"],
        "pr_timeline_years": 4,
    },
    "NL": {
        "name": "Netherlands",
        "job_market": 83, "pr_timeline": 78, "visa_ease": 79, "salary_cost_ratio": 80, "language": 88,
        "visa_types": ["Highly Skilled Migrant", "Orientation Year", "EU Blue Card"],
        "pr_timeline_years": 5,
    },
    "PT": {
        "name": "Portugal",
        "job_market": 65, "pr_timeline": 80, "visa_ease": 75, "salary_cost_ratio": 82, "language": 72,
        "visa_types": ["D3 Tech Visa", "Job Seeker Visa", "Digital Nomad Visa"],
        "pr_timeline_years": 5,
    },
    "IE": {
        "name": "Ireland",
        "job_market": 78, "pr_timeline": 68, "visa_ease": 83, "salary_cost_ratio": 65, "language": 97,
        "visa_types": ["Critical Skills Employment Permit", "General Employment Permit", "Stamp 4"],
        "pr_timeline_years": 5,
    },
    "AE": {
        "name": "UAE",
        "job_market": 76, "pr_timeline": 45, "visa_ease": 70, "salary_cost_ratio": 88, "language": 90,
        "visa_types": ["Golden Visa", "Employment Visa", "Green Visa"],
        "pr_timeline_years": 10,
    },
    "NZ": {
        "name": "New Zealand",
        "job_market": 72, "pr_timeline": 74, "visa_ease": 80, "salary_cost_ratio": 74, "language": 97,
        "visa_types": ["Skilled Migrant", "Accredited Employer Work Visa", "Post-Study Work"],
        "pr_timeline_years": 4,
    },
    "SG": {
        "name": "Singapore",
        "job_market": 79, "pr_timeline": 55, "visa_ease": 72, "salary_cost_ratio": 78, "language": 95,
        "visa_types": ["Employment Pass", "S Pass", "Personalised Employment Pass"],
        "pr_timeline_years": 7,
    },
}

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
    weights = {
        "job_market": request.weights.job_market,
        "pr_timeline": request.weights.pr_timeline,
        "visa_ease": request.weights.visa_ease,
        "salary_cost_ratio": request.weights.salary_cost_ratio,
        "language": request.weights.language,
    }
    today = date.today().isoformat()

    scored = []
    for code, data in COUNTRY_DATA.items():
        factor_scores = {f: data[f] for f in FACTORS}
        total = sum(factor_scores[f] * weights[f] for f in FACTORS)

        if total >= 80:
            tier = "great"
        elif total >= 60:
            tier = "good"
        elif total >= 40:
            tier = "moderate"
        else:
            tier = "low"

        # Top 2 factors by weighted contribution
        top2 = sorted(FACTORS, key=lambda f: factor_scores[f] * weights[f], reverse=True)[:2]
        verdict = (
            f"{_VERDICT_PHRASES[top2[0]].capitalize()} and {_VERDICT_PHRASES[top2[1]]} "
            f"make {data['name']} your top match."
        )

        scored.append({
            "code": code,
            "data": data,
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
            visa_types=item["data"]["visa_types"],
            pr_timeline_years=item["data"]["pr_timeline_years"],
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
            sim = _cosine_similarity(COUNTRY_DATA[a], COUNTRY_DATA[b])
            if sim > 0.85:
                shared = max(FACTORS, key=lambda f: (COUNTRY_DATA[a][f] + COUNTRY_DATA[b][f]) / 2)
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
