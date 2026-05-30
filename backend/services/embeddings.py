"""
Gemini embedding pipeline via REST API.

Uses gemini-embedding-001 (768 dimensions) through the Gemini REST API with
httpx — same approach as llm.py. No local model weights, zero RAM overhead.
"""

import hashlib
import os
import time
from datetime import date

import httpx

_API_KEY = os.getenv("GEMINI_API_KEY", "")
_EMBED_MODEL_PRIMARY = "gemini-embedding-001"
_EMBED_MODEL_FALLBACK = "gemini-embedding-2"


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


def _content_hash(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()[:16]


def _embed_one(text: str) -> list[float]:
    """Embed with primary model, fall back to secondary on rate limit."""
    for model in [_EMBED_MODEL_PRIMARY, _EMBED_MODEL_FALLBACK]:
        time.sleep(0.5)  # 2 req/sec max — safe for free tier
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models"
            f"/{model}:embedContent?key={_API_KEY}"
        )
        try:
            response = httpx.post(
                url,
                json={
                    "content": {"parts": [{"text": text}]},
                    "outputDimensionality": 768,
                },
                timeout=30,
            )
            if response.status_code == 429:
                print(f"  [rate limit] {model} exhausted, trying fallback...")
                continue
            response.raise_for_status()
            return response.json()["embedding"]["values"]
        except httpx.HTTPStatusError as e:
            print(f"  [error] {model}: {e}")
            continue

    # Both models exhausted — wait 60s and retry once
    print("  [rate limit] both models exhausted, waiting 60s...")
    time.sleep(60)
    return _embed_one(text)


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

    Resume-safe: chunks already in the DB are skipped by content hash so a
    crashed run can be restarted without duplicating work.

    Returns the total number of chunks successfully written to Supabase.
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

        if not filtered:
            continue

        # Build set of already-stored hashes for this country so we can resume
        existing_result = (
            client.table("policy_chunks")
            .select("content")
            .eq("country_id", country_id)
            .execute()
        )
        existing_hashes = {
            _content_hash(r["content"]) for r in (existing_result.data or [])
        }

        ok = 0
        for chunk in filtered:
            if _content_hash(chunk) in existing_hashes:
                ok += 1  # already stored from a previous run
                continue

            try:
                vector = _embed_one(chunk)
            except Exception as e:
                print(f"  [error] embedding failed: {e} | {chunk[:50]!r}")
                continue

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
