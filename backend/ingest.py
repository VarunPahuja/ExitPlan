"""
Run the full ingest pipeline: scrape → embed → store.

Two-phase approach keeps Scrapy/Twisted completely separate from asyncio:
  Phase 1  run_all_scrapers() — Twisted reactor runs and stops synchronously
  Phase 2  asyncio.run(embed_and_store()) — asyncio starts fresh after Twisted exits

This avoids the Windows ProactorEventLoop / AsyncioSelectorReactor conflict.

Usage:
    cd backend/
    python ingest.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from scrapers.runner import run_all_scrapers  # noqa: E402  (import before asyncio starts)
from services.embeddings import embed_and_store  # noqa: E402


async def _store(docs: list[dict]) -> int:
    return await embed_and_store(docs)


if __name__ == "__main__":
    # ── Phase 1: Scrapy / Twisted (sync, blocking, no asyncio loop running) ──
    print("Phase 1 — Scraping policy pages...")
    docs = run_all_scrapers()
    print(f"  {len(docs)} document(s) scraped\n")

    if not docs:
        print("No documents scraped — check scraper output and network.")
        sys.exit(1)

    # ── Phase 2: Embed + store (asyncio, Twisted is fully done by now) ──
    print("Phase 2 — Embedding and storing chunks...")
    total = asyncio.run(_store(docs))

    print(f"\nDone.")
    print(f"  Documents scraped : {len(docs)}")
    print(f"  Chunks stored     : {total}")
