"""
Policy change detector.

After each scrape run, diffs the newly scraped text against the previous
snapshot stored in Supabase.  If a meaningful change is detected (above a
configurable similarity threshold), it publishes a change event to the
Upstash Redis pub/sub channel so the alert_engine can fan out notifications.

Uses cosine similarity between document-level embeddings as the primary
change signal; falls back to text diff for flagging specific changed passages.
"""


CHANGE_THRESHOLD = 0.05


async def detect(country_code: str, doc_id: str, new_text: str):
    """Compare new_text against the stored snapshot and publish a change event if needed."""
    pass


async def fetch_previous_snapshot(doc_id: str) -> str | None:
    """Load the last-indexed text for a document from Supabase."""
    pass


def similarity_delta(old_embedding: list[float], new_embedding: list[float]) -> float:
    """Return 1 - cosine_similarity as a change magnitude score."""
    pass


async def publish_change_event(country_code: str, doc_id: str, summary: str):
    """Push a JSON change event onto the Upstash Redis pub/sub channel."""
    pass
