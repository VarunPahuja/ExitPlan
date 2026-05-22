"""
RAG (Retrieval-Augmented Generation) query engine.

Week 3: mock chunk retrieval backed by hardcoded policy snippets.
Week 4: replace retrieve() with pgvector similarity search + FlashRank reranking.
"""

import json
from collections.abc import AsyncGenerator

from services import llm

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


async def retrieve(query: str, country_code: str, k: int = 3) -> list[dict]:
    """Return top-k mock policy chunks for the given country.

    Falls back to GB chunks when the country isn't in the mock set.
    Real pgvector retrieval replaces this in Week 4.
    """
    return MOCK_CHUNKS.get(country_code.upper(), MOCK_CHUNKS["GB"])[:k]


async def ask(
    query: str, country_code: str, user_profile: dict
) -> AsyncGenerator[str, None]:
    """Retrieve context chunks, stream Gemini answer as SSE, then emit citations."""
    chunks = await retrieve(query, country_code)

    context_parts = [
        f"{c['content']} (Source: {c['source_url']})" for c in chunks
    ]
    context = "\n\n".join(context_parts)

    prompt = (
        f"User profile: {user_profile}\n\n"
        f"Policy context:\n{context}\n\n"
        f"Question: {query}\n\n"
        "Answer based only on the context above."
    )

    async for chunk in llm.generate(prompt, context):
        yield f"data: {json.dumps({'chunk': chunk, 'done': False})}\n\n"

    citations = [
        {"source_url": c["source_url"], "visa_type": c["visa_type"]} for c in chunks
    ]
    yield f"data: {json.dumps({'chunk': '', 'done': True, 'citations': citations})}\n\n"
