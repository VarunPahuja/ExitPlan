"""
Diagnose vector insertion format for Supabase policy_chunks.

Fetches the first chunk of the German Residence Act page directly (httpx, no
Scrapy) so this script runs cleanly inside asyncio.run() without any
Twisted-reactor conflict.

Tests both vector formats against a real Supabase insert and prints which one
succeeds.

Usage:
    cd backend/
    python test_insert.py
"""

import asyncio
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import httpx
from bs4 import BeautifulSoup

from db.client import admin_client
from services.embeddings import chunk_text, embed

SOURCE_URL = "https://www.gesetze-im-internet.de/englisch_aufenthg/englisch_aufenthg.html"


def fetch_first_chunk() -> str:
    """Fetch the German Residence Act and return its first text chunk."""
    print(f"Fetching {SOURCE_URL} ...")
    r = httpx.get(
        SOURCE_URL,
        headers={"User-Agent": "ExitPlan/1.0"},
        follow_redirects=True,
        timeout=20,
    )
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup.find_all(["nav", "header", "footer", "script", "style"]):
        tag.decompose()
    main = soup.find("main") or soup.find("div", id="content") or soup.body or soup
    text = re.sub(r"\s{2,}", " ", main.get_text(separator=" ", strip=True))

    chunks = chunk_text(text)
    print(f"  {len(chunks)} chunks available — using chunk #1")
    return chunks[0]


async def try_insert(row: dict, label: str) -> bool:
    """Attempt one insert and report the outcome. Returns True on success."""
    client = admin_client()
    print(f"\n--- {label} ---")
    emb = row["embedding"]
    preview = str(emb)[:80] if isinstance(emb, str) else f"[list of {len(emb)} floats]"
    print(f"  embedding type : {type(emb).__name__}")
    print(f"  embedding value: {preview}...")
    try:
        result = client.table("policy_chunks").insert(row).execute()
        if result.data:
            print(f"  SUCCESS  id={result.data[0].get('id')}")
            return True
        else:
            print(f"  FAIL     empty response (no data returned)")
            return False
    except Exception as e:
        print(f"  FAIL     exception: {e}")
        return False


async def main() -> None:
    client = admin_client()

    # Look up DE country_id
    countries = client.table("countries").select("id,code").execute()
    country_map = {r["code"]: r["id"] for r in countries.data}
    country_id = country_map.get("DE")
    if not country_id:
        print("ERROR: 'DE' not found in countries table — run the schema migration first.")
        sys.exit(1)
    print(f"DE country_id: {country_id}")

    chunk = fetch_first_chunk()
    vector: list[float] = embed([chunk])[0]
    today = date.today().isoformat()

    base_row = {
        "country_id": country_id,
        "visa_type": "German Residence Act",
        "content": chunk,
        "source_url": SOURCE_URL,
        "effective_date": today,
        "scraped_at": today + "T00:00:00",
    }

    # ── Test 1: string format '[v1,v2,...]' ──────────────────────────────────
    row_str = {**base_row, "embedding": "[" + ",".join(f"{v:.8f}" for v in vector) + "]"}
    ok_str = await try_insert(row_str, "Format A: string '[v1,v2,...]'")

    # ── Test 2: plain Python list ────────────────────────────────────────────
    row_list = {**base_row, "embedding": vector}
    ok_list = await try_insert(row_list, "Format B: list[float]")

    # ── Summary ──────────────────────────────────────────────────────────────
    print("\n" + "=" * 50)
    print(f"String format : {'OK' if ok_str  else 'FAIL'}")
    print(f"List format   : {'OK' if ok_list else 'FAIL'}")

    if not ok_str and not ok_list:
        print("\nBoth formats failed — check Supabase credentials and that")
        print("pgvector extension + policy_chunks table exist.")
    elif ok_str and not ok_list:
        print("\nUse string format in embed_and_store() (current default is correct).")
    elif ok_list and not ok_str:
        print("\nSwitch embed_and_store() to use_string_format=False.")
    else:
        print("\nBoth work — string format preferred (explicit, no type-coercion).")


if __name__ == "__main__":
    asyncio.run(main())
