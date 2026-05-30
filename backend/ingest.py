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

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env FIRST before any other imports so GEMINI_API_KEY is available
load_dotenv()

import asyncio  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))

from scrapers.runner import run_all_scrapers  # noqa: E402
from services.embeddings import embed_and_store, chunk_text  # noqa: E402


async def _store(docs: list[dict]) -> int:
    return await embed_and_store(docs)


if __name__ == "__main__":
    # ── Phase 1: Scrapy / Twisted (sync, blocking, no asyncio loop running) ──
    print("Phase 1 — Scraping policy pages...")
    docs = run_all_scrapers()
    print(f"  {len(docs)} document(s) scraped")

    # ── Phase 1b: Manual curated markdown documents ──
    print("\nPhase 1b — Loading manual curated documents...")
    from scrapers.md_ingest import load_manual_md_docs
    manual_docs = load_manual_md_docs()
    print(f"  {len(manual_docs)} manual section(s) loaded")
    docs = docs + manual_docs

    if not docs:
        print("No documents found — check scraper output and manual_docs/.")
        sys.exit(1)

    # ── Progress estimate ──
    total_chunks = sum(len(chunk_text(doc["content"])) for doc in docs)
    print(f"\n  Documents total             : {len(docs)}")
    print(f"  Estimated chunks to embed   : ~{total_chunks}")
    print(f"  Estimated time at 0.6s/chunk: ~{total_chunks * 0.6 / 60:.0f} minutes")
    print(f"  Using: gemini-embedding-001 + gemini-embedding-2 fallback")
    print(f"  (Already-stored chunks are skipped — resume-safe)\n")

    # ── Phase 2: Embed + store (asyncio, Twisted is fully done by now) ──
    print("Phase 2 — Embedding and storing chunks...")
    total = asyncio.run(_store(docs))

    print(f"\nDone.")
    print(f"  Documents scraped : {len(docs)}")
    print(f"  Chunks stored     : {total}")
