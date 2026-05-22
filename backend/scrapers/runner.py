"""
Scraper runner — executes Scrapy spiders in-process and persists output.

IMPORTANT — Twisted reactor limitation:
  CrawlerProcess starts Twisted's reactor. Once started and stopped it cannot
  be restarted in the same process. This means:
    - run_uk/canada/germany_scraper() are safe to call individually (one per run).
    - run_all_scrapers() crawls all three spiders in a single CrawlerProcess to
      avoid this limitation. Do NOT call individual runners then run_all_scrapers
      in the same Python process.

Usage examples:
    python scrapers/runner.py uk
    python scrapers/runner.py canada
    python scrapers/runner.py germany
    python scrapers/runner.py all
"""

import json
import sys
from pathlib import Path

_backend = Path(__file__).resolve().parent.parent
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

from scrapy import signals  # noqa: E402
from scrapy.crawler import CrawlerProcess  # noqa: E402
from scrapy.signalmanager import dispatcher  # noqa: E402

from scrapers.canada import CanadaSpider  # noqa: E402
from scrapers.germany import GermanySpider  # noqa: E402
from scrapers.uk import UKSpider  # noqa: E402

OUTPUT_DIR = Path(__file__).parent / "output"

_BASE_SETTINGS = {
    "LOG_LEVEL": "ERROR",
}


def _make_process(out_file: Path) -> CrawlerProcess:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return CrawlerProcess(
        settings={
            **_BASE_SETTINGS,
            "FEEDS": {str(out_file): {"format": "json", "overwrite": True}},
        }
    )


def run_uk_scraper(urls: list[str] | None = None) -> list[dict]:
    """Run UKSpider. Saves to output/uk_raw.json."""
    out_file = OUTPUT_DIR / "uk_raw.json"
    process = _make_process(out_file)
    process.crawl(UKSpider, **({"start_urls": urls} if urls else {}))
    process.start()
    with open(out_file) as f:
        return json.load(f)


def run_canada_scraper(urls: list[str] | None = None) -> list[dict]:
    """Run CanadaSpider. Saves to output/canada_raw.json."""
    out_file = OUTPUT_DIR / "canada_raw.json"
    process = _make_process(out_file)
    process.crawl(CanadaSpider, **({"start_urls": urls} if urls else {}))
    process.start()
    with open(out_file) as f:
        return json.load(f)


def run_germany_scraper(urls: list[str] | None = None) -> list[dict]:
    """Run GermanySpider. Saves to output/germany_raw.json."""
    out_file = OUTPUT_DIR / "germany_raw.json"
    process = _make_process(out_file)
    process.crawl(GermanySpider, **({"start_urls": urls} if urls else {}))
    process.start()
    with open(out_file) as f:
        return json.load(f)


def run_all_scrapers() -> list[dict]:
    """Run all three spiders in one CrawlerProcess (avoids reactor restart).

    Saves per-country JSON files and returns a combined list of all documents.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []

    def _collect(item, response, spider):
        results.append(dict(item))

    dispatcher.connect(_collect, signal=signals.item_scraped)

    process = CrawlerProcess(settings=_BASE_SETTINGS)
    process.crawl(UKSpider)
    process.crawl(CanadaSpider)
    process.crawl(GermanySpider)
    process.start()

    # Persist per-country output files
    for code, filename in [("GB", "uk_raw.json"), ("CA", "canada_raw.json"), ("DE", "germany_raw.json")]:
        docs = [d for d in results if d["country_code"] == code]
        with open(OUTPUT_DIR / filename, "w") as f:
            json.dump(docs, f, indent=2)

    return results


def _print_preview(docs: list[dict], chars: int = 300) -> None:
    if not docs:
        print("  No results — check connection or target URL.")
        return
    d = docs[0]
    print(f"  URL       : {d['source_url']}")
    print(f"  Visa type : {d['visa_type']}")
    print(f"  Chars     : {len(d['content'])}")
    print(f"  Preview   : {d['content'][:chars]}\n")


if __name__ == "__main__":
    target = sys.argv[1].lower() if len(sys.argv) > 1 else "uk"

    if target == "uk":
        print("Testing UK scraper (graduate-visa)...\n")
        _print_preview(run_uk_scraper(urls=["https://www.gov.uk/graduate-visa"]))

    elif target == "canada":
        print("Testing Canada scraper (after-graduation)...\n")
        _print_preview(run_canada_scraper(
            urls=["https://www.canada.ca/en/immigration-refugees-citizenship/services/study-canada/work/after-graduation.html"]
        ))

    elif target == "germany":
        print("Testing Germany scraper (German Residence Act — gesetze-im-internet.de)...\n")
        _print_preview(run_germany_scraper(
            urls=["https://www.gesetze-im-internet.de/englisch_aufenthg/englisch_aufenthg.html"]
        ))

    elif target == "all":
        print("Running all scrapers (full crawl)...\n")
        docs = run_all_scrapers()
        print(f"Total documents scraped: {len(docs)}")
        for code in ("GB", "CA", "DE"):
            country_docs = [d for d in docs if d["country_code"] == code]
            print(f"  {code}: {len(country_docs)} page(s)")

    else:
        print(f"Unknown target '{target}'. Use: uk | canada | germany | all")
        sys.exit(1)
