"""
Scraper runner — executes Scrapy spiders in-process and persists output.

IMPORTANT — Twisted reactor limitation:
  CrawlerProcess starts Twisted's reactor. Once started and stopped it cannot
  be restarted in the same process. This means:
    - Individual run_*_scraper() functions are safe to call individually (one per run).
    - run_all_scrapers() crawls all 10 spiders in a single CrawlerProcess to
      avoid this limitation. Do NOT call individual runners then run_all_scrapers
      in the same Python process.

Usage examples:
    python scrapers/runner.py uk
    python scrapers/runner.py canada
    python scrapers/runner.py germany
    python scrapers/runner.py australia
    python scrapers/runner.py netherlands
    python scrapers/runner.py ireland
    python scrapers/runner.py uae
    python scrapers/runner.py nz
    python scrapers/runner.py singapore
    python scrapers/runner.py portugal
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

from scrapers.australia import AustraliaSpider  # noqa: E402
from scrapers.canada import CanadaSpider  # noqa: E402
from scrapers.germany import GermanySpider  # noqa: E402
from scrapers.ireland import IrelandSpider  # noqa: E402
from scrapers.netherlands import NetherlandsSpider  # noqa: E402
from scrapers.newzealand import NewZealandSpider  # noqa: E402
from scrapers.portugal import PortugalSpider  # noqa: E402
from scrapers.singapore import SingaporeSpider  # noqa: E402
from scrapers.uae import UAESpider  # noqa: E402
from scrapers.uk import UKSpider  # noqa: E402

OUTPUT_DIR = Path(__file__).parent / "output"

_BASE_SETTINGS = {
    "LOG_LEVEL": "ERROR",
}

_COUNTRY_FILES = [
    ("GB", "uk_raw.json"),
    ("CA", "canada_raw.json"),
    ("DE", "germany_raw.json"),
    ("AU", "au_raw.json"),
    ("NL", "nl_raw.json"),
    ("IE", "ie_raw.json"),
    ("AE", "ae_raw.json"),
    ("NZ", "nz_raw.json"),
    ("SG", "sg_raw.json"),
    ("PT", "pt_raw.json"),
]


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


def run_australia_scraper(urls: list[str] | None = None) -> list[dict]:
    """Run AustraliaSpider. Saves to output/au_raw.json."""
    out_file = OUTPUT_DIR / "au_raw.json"
    process = _make_process(out_file)
    process.crawl(AustraliaSpider, **({"start_urls": urls} if urls else {}))
    process.start()
    with open(out_file) as f:
        return json.load(f)


def run_netherlands_scraper(urls: list[str] | None = None) -> list[dict]:
    """Run NetherlandsSpider. Saves to output/nl_raw.json."""
    out_file = OUTPUT_DIR / "nl_raw.json"
    process = _make_process(out_file)
    process.crawl(NetherlandsSpider, **({"start_urls": urls} if urls else {}))
    process.start()
    with open(out_file) as f:
        return json.load(f)


def run_ireland_scraper(urls: list[str] | None = None) -> list[dict]:
    """Run IrelandSpider. Saves to output/ie_raw.json."""
    out_file = OUTPUT_DIR / "ie_raw.json"
    process = _make_process(out_file)
    process.crawl(IrelandSpider, **({"start_urls": urls} if urls else {}))
    process.start()
    with open(out_file) as f:
        return json.load(f)


def run_uae_scraper(urls: list[str] | None = None) -> list[dict]:
    """Run UAESpider. Saves to output/ae_raw.json."""
    out_file = OUTPUT_DIR / "ae_raw.json"
    process = _make_process(out_file)
    process.crawl(UAESpider, **({"start_urls": urls} if urls else {}))
    process.start()
    with open(out_file) as f:
        return json.load(f)


def run_newzealand_scraper(urls: list[str] | None = None) -> list[dict]:
    """Run NewZealandSpider. Saves to output/nz_raw.json."""
    out_file = OUTPUT_DIR / "nz_raw.json"
    process = _make_process(out_file)
    process.crawl(NewZealandSpider, **({"start_urls": urls} if urls else {}))
    process.start()
    with open(out_file) as f:
        return json.load(f)


def run_singapore_scraper(urls: list[str] | None = None) -> list[dict]:
    """Run SingaporeSpider. Saves to output/sg_raw.json."""
    out_file = OUTPUT_DIR / "sg_raw.json"
    process = _make_process(out_file)
    process.crawl(SingaporeSpider, **({"start_urls": urls} if urls else {}))
    process.start()
    with open(out_file) as f:
        return json.load(f)


def run_portugal_scraper(urls: list[str] | None = None) -> list[dict]:
    """Run PortugalSpider. Saves to output/pt_raw.json."""
    out_file = OUTPUT_DIR / "pt_raw.json"
    process = _make_process(out_file)
    process.crawl(PortugalSpider, **({"start_urls": urls} if urls else {}))
    process.start()
    with open(out_file) as f:
        return json.load(f)


def run_all_scrapers() -> list[dict]:
    """Run all 10 spiders in one CrawlerProcess (avoids reactor restart).

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
    process.crawl(AustraliaSpider)
    process.crawl(NetherlandsSpider)
    process.crawl(IrelandSpider)
    process.crawl(UAESpider)
    process.crawl(NewZealandSpider)
    process.crawl(SingaporeSpider)
    process.crawl(PortugalSpider)
    process.start()

    for code, filename in _COUNTRY_FILES:
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
        print("Testing Canada scraper (express-entry)...\n")
        _print_preview(run_canada_scraper(
            urls=["https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry.html"]
        ))

    elif target == "germany":
        print("Testing Germany scraper (German Residence Act — gesetze-im-internet.de)...\n")
        _print_preview(run_germany_scraper(
            urls=["https://www.gesetze-im-internet.de/englisch_aufenthg/englisch_aufenthg.html"]
        ))

    elif target == "australia":
        print("Testing Australia scraper (all 4 Wikipedia sources)...\n")
        docs = run_australia_scraper()
        print(f"  Pages scraped: {len(docs)}")
        for d in docs:
            print(f"  [{d['visa_type']}] {len(d['content'])} chars — {d['source_url']}")
        if docs:
            print(f"\n  Preview ({docs[0]['visa_type']}):\n  {docs[0]['content'][:300]}\n")

    elif target == "netherlands":
        print("Testing Netherlands scraper (highly-skilled-migrant)...\n")
        _print_preview(run_netherlands_scraper(
            urls=["https://ind.nl/en/residence-permits/work/highly-skilled-migrant"]
        ))

    elif target == "ireland":
        print("Testing Ireland scraper (critical-skills-employment-permit)...\n")
        _print_preview(run_ireland_scraper(
            urls=["https://enterprise.gov.ie/en/what-we-do/workplace-and-skills/employment-permits/permit-types/critical-skills-employment-permit/"]
        ))

    elif target == "uae":
        print("Testing UAE scraper (all 4 sources)...\n")
        docs = run_uae_scraper()
        print(f"  Pages scraped: {len(docs)}")
        for d in docs:
            print(f"  [{d['visa_type']}] {len(d['content'])} chars — {d['source_url']}")
        if docs:
            print(f"\n  Preview ({docs[0]['visa_type']}):\n  {docs[0]['content'][:300]}\n")

    elif target == "nz":
        print("Testing New Zealand scraper (accredited-employer-work-visa)...\n")
        _print_preview(run_newzealand_scraper(
            urls=["https://www.immigration.govt.nz/new-zealand-visas/visas/visa/accredited-employer-work-visa"]
        ))

    elif target == "singapore":
        print("Testing Singapore scraper (employment-pass)...\n")
        _print_preview(run_singapore_scraper(
            urls=["https://www.mom.gov.sg/passes-and-permits/employment-pass"]
        ))

    elif target == "portugal":
        print("Testing Portugal scraper (Wikipedia: Immigration + Digital Nomad)...\n")
        docs = run_portugal_scraper()
        print(f"  Pages scraped: {len(docs)}")
        for d in docs:
            print(f"  [{d['visa_type']}] {len(d['content'])} chars — {d['source_url']}")
        if docs:
            print(f"\n  Preview ({docs[0]['visa_type']}):\n  {docs[0]['content'][:300]}\n")

    elif target == "all":
        print("Running all 10 scrapers (full crawl)...\n")
        docs = run_all_scrapers()
        print(f"Total documents scraped: {len(docs)}")
        for code, _ in _COUNTRY_FILES:
            country_docs = [d for d in docs if d["country_code"] == code]
            print(f"  {code}: {len(country_docs)} page(s)")

    else:
        print(f"Unknown target '{target}'. Use: uk | canada | germany | australia | netherlands | ireland | uae | nz | singapore | portugal | all")
        sys.exit(1)
