"""
Scraper orchestrator — coordinates the per-country scrapers (uk.py, canada.py,
germany.py) and writes scraped content into Supabase.

After each scrape run, calls the embedding pipeline to index new or updated
chunks, then calls change_detector to diff against the previous snapshot.
"""


async def run_all():
    """Trigger scrape + embed + diff for every configured country."""
    pass


async def run_country(country_code: str):
    """Scrape, embed, and diff a single country."""
    pass


async def store_raw_document(country_code: str, url: str, html: str, text: str):
    """Persist a raw scraped document to Supabase before chunking."""
    pass


async def index_document(country_code: str, doc_id: str, text: str):
    """Chunk the document, embed each chunk, and upsert into pgvector table."""
    pass
