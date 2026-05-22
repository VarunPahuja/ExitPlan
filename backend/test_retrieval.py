"""
Debug script: inspect what pgvector actually retrieves for a test query.

Usage:
    cd backend/
    python test_retrieval.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from services.rag import retrieve


async def main() -> None:
    query = "EU Blue Card salary requirement Germany"
    country = "DE"
    k = 10

    print(f"Query      : {query}")
    print(f"Country    : {country}   k={k}")
    print("-" * 70)

    chunks = await retrieve(query, country, k=k)

    for i, c in enumerate(chunks, 1):
        sim = c.get("similarity")
        sim_str = f"{sim:.4f}" if sim is not None else "n/a (mock)"
        preview = c["content"][:200].replace("\n", " ")
        print(f"\n#{i}  similarity={sim_str}  [{c['visa_type']}]")
        print(f"    {preview}")

    print(f"\n{len(chunks)} chunk(s) returned.")


if __name__ == "__main__":
    asyncio.run(main())
