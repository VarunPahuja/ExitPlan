"""
Full ingest + alert pipeline.

NOTE: run_all_scrapers() starts the Twisted reactor synchronously — call this
only from a context where no asyncio event loop is running, or via the CLI
(backend/ingest.py) which handles phase separation.
"""

from services.alert_engine import process_changes
from services.change_detector import detect_changes, store_change
from services.ingest import ingest_docs


async def run_ingest_and_alert() -> dict:
    """
    Full pipeline:
    1. Run scrapers
    2. Detect changes against stored policy_chunks
    3. Store each change in policy_changes
    4. Send alerts to affected users
    5. Re-embed and store new chunks
    6. Return summary dict
    """
    from scrapers.runner import run_all_scrapers  # late import — starts Twisted

    print("Scraping policy pages...")
    docs = run_all_scrapers()
    print(f"  {len(docs)} document(s) scraped")

    print("Detecting changes...")
    changes = await detect_changes(docs)
    print(f"  {len(changes)} change(s) detected")

    for change in changes:
        await store_change(change)

    print("Sending alerts...")
    alerts_sent = await process_changes(changes)
    print(f"  {alerts_sent} alert(s) sent")

    print("Embedding and storing chunks...")
    ingest_result = await ingest_docs(docs)

    return {
        "docs_scraped": len(docs),
        "changes_detected": len(changes),
        "alerts_sent": alerts_sent,
        "chunks_stored": ingest_result.get("chunks_stored", 0),
    }
