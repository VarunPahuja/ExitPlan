"""
Gemini embedding pipeline via REST API.

Uses text-embedding-004 (768 dimensions) through the Gemini REST API with
httpx — same approach as llm.py. No local model weights, zero RAM overhead.
"""

import os
from datetime import date

import httpx

_API_KEY = os.getenv("GEMINI_API_KEY", "")
_EMBED_MODEL = "gemini-embedding-001"


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> list[str]:
    """Split text into overlapping word-based chunks.

    Each chunk is roughly chunk_size words; consecutive chunks share overlap
    words so context isn't lost at chunk boundaries.
    """
    words = text.split()
    if not words:
        return []
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        if end >= len(words):
            break
        start = end - overlap
    return chunks


def _embed_one(text: str) -> list[float]:
    """Call the Gemini embedContent REST endpoint for a single text."""
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models"
        f"/{_EMBED_MODEL}:embedContent?key={_API_KEY}"
    )
    response = httpx.post(
        url,
        json={
            "content": {"parts": [{"text": text}]},
            "outputDimensionality": 768,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["embedding"]["values"]


def embed(texts: list[str]) -> list[list[float]]:
    """Return 768-dim embedding vectors for a list of texts."""
    return [_embed_one(t) for t in texts]


def embed_single(text: str) -> list[float]:
    """Embed a single text string."""
    return _embed_one(text)


def is_relevant_chunk(text: str) -> bool:
    """
    Return True only if this chunk contains information useful
    to an international student making immigration decisions.
    Filter out purely administrative/legal boilerplate.
    """
    text_lower = text.lower()

    relevant_terms = [
        "visa", "permit", "salary", "wage", "pr ", "permanent",
        "residency", "work", "employ", "skill", "qualify",
        "application", "eligible", "require", "threshold",
        "language", "english", "sponsor", "job", "graduate",
        "student", "degree", "qualification", "pathway",
        "timeline", "months", "years", "citizenship", "settle",
        "blue card", "express entry", "points", "score",
    ]

    has_relevant = any(term in text_lower for term in relevant_terms)

    admin_indicators = [
        "table of contents", "footnote", "bundesgesetzblatt",
        "official journal", "whereas the council",
        "having regard to the treaty",
        "annex to this ordinance",
        "impressum", "datenschutz",
    ]
    is_admin = sum(1 for ind in admin_indicators if ind in text_lower) >= 2

    return has_relevant and not is_admin


async def embed_and_store(
    docs: list[dict],
    use_string_format: bool = True,
) -> int:
    """Chunk, embed, and insert documents into the policy_chunks table.

    Returns the total number of chunks successfully written to Supabase.

    use_string_format=True  → embedding sent as '[v1,v2,...]' string
    use_string_format=False → embedding sent as plain Python list[float]
    """
    from db.client import admin_client

    client = admin_client()
    today = date.today().isoformat()

    countries = client.table("countries").select("id,code").execute()
    country_map: dict[str, str] = {r["code"]: r["id"] for r in countries.data}

    total = 0

    for doc in docs:
        code = doc["country_code"]
        country_id = country_map.get(code)
        if not country_id:
            print(f"  [skip] country code '{code}' not found in DB")
            continue

        chunks = chunk_text(doc["content"])
        if not chunks:
            continue

        filtered: list[str] = []
        for c in chunks:
            if is_relevant_chunk(c):
                filtered.append(c)
            else:
                print("  [SKIP] irrelevant chunk")

        if not filtered:
            continue

        vectors = embed(filtered)
        ok = 0

        for chunk, vector in zip(filtered, vectors):
            embedding_value = (
                "[" + ",".join(f"{v:.8f}" for v in vector) + "]"
                if use_string_format
                else vector
            )
            row = {
                "country_id": country_id,
                "visa_type": doc["visa_type"],
                "content": chunk,
                "source_url": doc["source_url"],
                "effective_date": today,
                "embedding": embedding_value,
                "scraped_at": doc["scraped_at"],
            }
            try:
                result = client.table("policy_chunks").insert(row).execute()
                if not result.data:
                    print(f"  [warn] empty response | {chunk[:50]!r}")
                else:
                    ok += 1
            except Exception as e:
                print(f"  [error] {e} | {chunk[:50]!r}")

        total += ok
        print(f"  [{code}] {doc['visa_type']:<35} {ok:>4}/{len(filtered)} chunks stored")

    return total
