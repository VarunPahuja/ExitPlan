"""
RAG (Retrieval-Augmented Generation) query engine.

retrieve() does a real pgvector cosine similarity search via a Postgres RPC
function (match_policy_chunks). MOCK_CHUNKS are kept as a fallback when the
country has no indexed chunks or the DB is unreachable.
"""

import json
from collections.abc import AsyncGenerator

from services import llm

# ── Fallback data (used when pgvector returns no results) ─────────────────────

MOCK_CHUNKS: dict[str, list[dict]] = {
    "DE": [
        {
            "content": (
                "International students in Germany on a student visa "
                "(Aufenthaltserlaubnis zum Studium) are permitted to work 120 full "
                "days or 240 half days per year. Part-time work during semester is "
                "allowed up to 20 hours per week."
            ),
            "source_url": "https://bamf.de/student-visa",
            "visa_type": "Student Visa",
        },
        {
            "content": (
                "After completing a degree in Germany, graduates can apply for a job "
                "seeker visa valid for 18 months. During this period, they may work "
                "in any job to support themselves."
            ),
            "source_url": "https://bamf.de/job-seeker",
            "visa_type": "Job Seeker Visa",
        },
        {
            "content": (
                "The EU Blue Card in Germany requires a job offer with minimum salary "
                "of EUR 45,300 per year (2024). STEM graduates have a reduced "
                "threshold of EUR 41,041."
            ),
            "source_url": "https://bamf.de/eu-blue-card",
            "visa_type": "EU Blue Card",
        },
    ],
    "GB": [
        {
            "content": (
                "International students in the UK on a Student visa can work up to "
                "20 hours per week during term time and full-time during vacations."
            ),
            "source_url": "https://gov.uk/student-visa/work",
            "visa_type": "Student Visa",
        },
        {
            "content": (
                "The Graduate Route visa allows international students who have "
                "completed a UK degree to stay and work for 2 years (3 years for PhD "
                "graduates) without needing a job offer."
            ),
            "source_url": "https://gov.uk/graduate-visa",
            "visa_type": "Graduate Route",
        },
        {
            "content": (
                "The Skilled Worker visa requires a job offer from a UK employer with "
                "a minimum salary of GBP 38,700 per year or the going rate for the "
                "occupation, whichever is higher."
            ),
            "source_url": "https://gov.uk/skilled-worker-visa",
            "visa_type": "Skilled Worker",
        },
    ],
    "CA": [
        {
            "content": (
                "International students in Canada with a valid study permit can work "
                "on campus without a work permit. Off-campus work is allowed up to "
                "24 hours per week during academic sessions."
            ),
            "source_url": "https://canada.ca/study-permit-work",
            "visa_type": "Study Permit",
        },
        {
            "content": (
                "The Post-Graduation Work Permit (PGWP) allows graduates of eligible "
                "Canadian programs to work in Canada for up to 3 years after graduation."
            ),
            "source_url": "https://canada.ca/pgwp",
            "visa_type": "PGWP",
        },
        {
            "content": (
                "Express Entry is Canada's main immigration system for skilled "
                "workers. Candidates are ranked by Comprehensive Ranking System (CRS) "
                "score. The Federal Skilled Worker stream requires at least 1 year of "
                "skilled work experience."
            ),
            "source_url": "https://canada.ca/express-entry",
            "visa_type": "Express Entry",
        },
    ],
}


# ── Real retrieval ─────────────────────────────────────────────────────────────

async def _vector_search(query: str, country_code: str, k: int = 5) -> list[dict]:
    """Return top-k policy chunks via pgvector cosine similarity.

    Falls back to MOCK_CHUNKS if the country has no indexed chunks or the
    RPC call fails (e.g. function not yet deployed, DB unreachable).
    """
    code = country_code.upper()
    try:
        from db.client import admin_client
        from services.embeddings import embed

        client = admin_client()

        country_result = (
            client.table("countries").select("id").eq("code", code).execute()
        )
        if not country_result.data:
            return _mock_fallback(code, k)

        country_id = country_result.data[0]["id"]

        vector = embed([query])[0]
        vector_str = "[" + ",".join(f"{v:.8f}" for v in vector) + "]"

        rpc_result = client.rpc(
            "match_policy_chunks",
            {
                "query_embedding": vector_str,
                "match_country_id": country_id,
                "match_count": k,
            },
        ).execute()

        if not rpc_result.data:
            return _mock_fallback(code, k)

        return [
            {
                "content": row["content"],
                "source_url": row["source_url"],
                "visa_type": row["visa_type"],
                "similarity": row.get("similarity"),
            }
            for row in rpc_result.data
        ]

    except Exception as exc:
        print(f"[rag._vector_search] error for {code}: {exc!r} — using mock fallback")
        return _mock_fallback(code, k)


async def keyword_search(
    query: str, country_code: str, k: int = 5
) -> list[dict]:
    """Return chunks that contain query keywords via Supabase ilike filter."""
    from db.client import admin_client

    client = admin_client()

    country = (
        client.table("countries")
        .select("id")
        .eq("code", country_code.upper())
        .execute()
    )
    if not country.data:
        return []
    country_id = country.data[0]["id"]

    terms = [w for w in query.lower().split() if len(w) > 3]

    results = []
    seen: set[str] = set()
    for term in terms[:4]:
        rows = (
            client.table("policy_chunks")
            .select("content,source_url,visa_type")
            .eq("country_id", country_id)
            .ilike("content", f"%{term}%")
            .limit(k)
            .execute()
        )
        for row in rows.data:
            key = row["content"][:100]
            if key not in seen:
                seen.add(key)
                results.append({
                    "content": row["content"],
                    "source_url": row["source_url"],
                    "visa_type": row["visa_type"],
                    "similarity": 0.85,
                })
    return results[:k]


async def retrieve(query: str, country_code: str, k: int = 5) -> list[dict]:
    """Hybrid retrieval: merge vector search and keyword search results.

    Both searches run concurrently. Results are deduplicated by the first 100
    chars of content and capped at k total chunks.
    """
    import asyncio as _asyncio

    vector_res, keyword_res = await _asyncio.gather(
        _vector_search(query, country_code, k),
        keyword_search(query, country_code, k),
    )

    seen: set[str] = set()
    merged: list[dict] = []
    for chunk in vector_res + keyword_res:
        key = chunk["content"][:100]
        if key not in seen:
            seen.add(key)
            merged.append(chunk)
    return merged[:k]


def _mock_fallback(country_code: str, k: int) -> list[dict]:
    return MOCK_CHUNKS.get(country_code, MOCK_CHUNKS["GB"])[:k]


# ── Streaming answer ───────────────────────────────────────────────────────────

async def ask(
    query: str, country_code: str, user_profile: dict
) -> AsyncGenerator[str, None]:
    """Keyword-only retrieval then Gemini answer. No embedding API call for queries."""
    code = country_code.upper()
    chunks: list[dict] = []

    try:
        from db.client import admin_client
        client = admin_client()

        country_result = (
            client.table("countries").select("id").eq("code", code).execute()
        )
        if country_result.data:
            country_id = country_result.data[0]["id"]

            # Try full query phrase first
            result = (
                client.table("policy_chunks")
                .select("content, source_url, visa_type")
                .eq("country_id", country_id)
                .ilike("content", f"%{query}%")
                .limit(8)
                .execute()
            )
            chunks = [
                {"content": r["content"], "source_url": r["source_url"], "visa_type": r["visa_type"]}
                for r in (result.data or [])
            ]

            # If nothing, try individual meaningful words
            if not chunks:
                words = [w for w in query.lower().split() if len(w) > 3]
                for word in words[:3]:
                    result = (
                        client.table("policy_chunks")
                        .select("content, source_url, visa_type")
                        .eq("country_id", country_id)
                        .ilike("content", f"%{word}%")
                        .limit(5)
                        .execute()
                    )
                    if result.data:
                        chunks = [
                            {"content": r["content"], "source_url": r["source_url"], "visa_type": r["visa_type"]}
                            for r in result.data
                        ]
                        break
    except Exception as exc:
        print(f"[rag.ask] keyword search error for {code}: {exc!r}")

    if not chunks:
        chunks = _mock_fallback(code, 5)

    context_parts = [
        f"{c['content']} (Source: {c['source_url']})" for c in chunks
    ]

    if not context_parts:
        yield json.dumps({
            "chunk": (
                f"I don't have specific policy documents for {country_code} in my "
                f"database yet. Please check the official immigration website for "
                f"the most accurate information."
            ),
            "done": True,
            "citations": [],
        })
        return

    context = "\n\n".join(context_parts)

    prompt = (
        f"Answer this immigration question concisely.\n\n"
        f"Country: {country_code}\n"
        f"User: {user_profile}\n\n"
        f"Policy context (from official sources):\n{context}\n\n"
        f"Question: {query}\n\n"
        f"Answer in 2-3 short paragraphs. Plain English only. "
        f"No headers or bullet points. Under 150 words total. "
        f"End with: Source: [most relevant URL from context]"
    )

    async for chunk in llm.generate(prompt, context):
        yield f"data: {json.dumps({'chunk': chunk, 'done': False})}\n\n"

    citations = [
        {"source_url": c["source_url"], "visa_type": c["visa_type"]} for c in chunks
    ]
    yield f"data: {json.dumps({'chunk': '', 'done': True, 'citations': citations})}\n\n"
