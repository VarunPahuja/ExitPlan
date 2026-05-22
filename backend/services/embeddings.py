"""
Sentence-transformers embedding pipeline.

Model is loaded once at module level and kept in memory for the process
lifetime — avoids a ~1s reload penalty on every call.
"""

from datetime import date

from sentence_transformers import SentenceTransformer

_model = SentenceTransformer("all-MiniLM-L6-v2")


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


def embed(texts: list[str]) -> list[list[float]]:
    """Return 384-dim embedding vectors for a list of texts."""
    return _model.encode(texts).tolist()


async def embed_and_store(docs: list[dict]) -> int:
    """Chunk, embed, and insert documents into the policy_chunks table.

    Returns the total number of chunks written to Supabase.
    Vectors are passed as pgvector-format strings: '[v1,v2,...]'.
    """
    from db.client import admin_client

    client = admin_client()
    today = date.today().isoformat()

    # Build country_code → country_id lookup (one round-trip)
    countries = client.table("countries").select("id,code").execute()
    country_map: dict[str, str] = {r["code"]: r["id"] for r in countries.data}

    total = 0
    BATCH = 50

    for doc in docs:
        code = doc["country_code"]
        country_id = country_map.get(code)
        if not country_id:
            print(f"  [skip] country code '{code}' not found in DB")
            continue

        chunks = chunk_text(doc["content"])
        if not chunks:
            continue

        vectors = embed(chunks)

        rows = [
            {
                "country_id": country_id,
                "visa_type": doc["visa_type"],
                "content": chunk,
                "source_url": doc["source_url"],
                "effective_date": today,
                # pgvector expects the string form '[v1,v2,...]' via PostgREST
                "embedding": "[" + ",".join(f"{v:.8f}" for v in vector) + "]",
                "scraped_at": doc["scraped_at"],
            }
            for chunk, vector in zip(chunks, vectors)
        ]

        for i in range(0, len(rows), BATCH):
            client.table("policy_chunks").insert(rows[i : i + BATCH]).execute()

        total += len(rows)
        print(f"  [{code}] {doc['visa_type']:<35} {len(rows):>4} chunks")

    return total
