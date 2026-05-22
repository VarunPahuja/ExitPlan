"""
Ingest orchestrator — runs all scrapers then embeds and stores the results.

NOTE: On Windows, Scrapy/Twisted requires SelectorEventLoop.
If called from an existing asyncio context (e.g. FastAPI), run the scraping
phase first via run_all_scrapers() before entering the event loop, or use
the Celery task wrapper which handles this automatically.

For CLI use, backend/ingest.py handles phase separation correctly.
"""

from services.embeddings import embed_and_store


async def ingest_docs(docs: list[dict]) -> dict:
    """Embed and store pre-scraped documents. Returns summary counts."""
    chunks_stored = await embed_and_store(docs)
    return {"docs_scraped": len(docs), "chunks_stored": chunks_stored}


async def ingest_all() -> dict:
    """Scrape, embed, and store all policy pages.

    IMPORTANT: Call this only when no asyncio event loop is running yet,
    because run_all_scrapers() starts the Twisted reactor synchronously.
    For scripts use backend/ingest.py which separates the two phases.
    """
    from scrapers.runner import run_all_scrapers

    print("Scraping policy pages...")
    docs = run_all_scrapers()
    print(f"  {len(docs)} document(s) scraped\n")

    print("Embedding and storing chunks...")
    return await ingest_docs(docs)
