"""
Germany immigration policy scraper — Scrapy spider.

Sources:
- gesetze-im-internet.de: Federal Ministry of Justice, authoritative English
  translation of the German Residence Act. Covers EU Blue Card (§18b),
  Job Seeker Visa (§20), Skilled Immigration Act (§18a). Plain HTML, stable.
- iamexpat.de: Accessible expat guide with EU Blue Card specifics including
  salary thresholds and sector requirements. Used instead of make-it-in-germany.com
  which is blocked by Cloudflare.
- gtai.de: Germany Trade & Invest — official government-backed investment
  promotion agency, covers skilled worker immigration pathways.
"""

import re
from datetime import datetime

import scrapy
from bs4 import BeautifulSoup

_URL_VISA_MAP = {
    "englisch_aufenthg": "German Residence Act",
}

_DEFAULT_URLS = [
    # gesetze-im-internet.de is the authoritative English translation of the full
    # Residence Act. It covers EU Blue Card (§18b), Job Seeker Visa (§20), Skilled
    # Immigration Act (§18a, §18d), and work permit rules for all visa categories.
    # The relevance filter in embed_and_store() removes the dense administrative
    # boilerplate, keeping only sections with practical immigration information.
    "https://www.gesetze-im-internet.de/englisch_aufenthg/englisch_aufenthg.html",
]


class GermanySpider(scrapy.Spider):
    name = "germany_immigration"
    start_urls = _DEFAULT_URLS

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "USER_AGENT": "ExitPlan/1.0 (+https://exitplan.app)",
        "DOWNLOAD_DELAY": 1,
        "CONCURRENT_REQUESTS": 1,
        "LOG_LEVEL": "ERROR",
    }

    def __init__(self, start_urls=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if start_urls is not None:
            self.start_urls = (
                start_urls if isinstance(start_urls, list) else [start_urls]
            )

    def parse(self, response):
        # URLs like /englisch_aufenthg/englisch_aufenthg.html — take the directory name
        parts = response.url.rstrip("/").split("/")
        slug = parts[-2] if parts[-1].endswith(".html") else parts[-1]
        visa_type = _URL_VISA_MAP.get(slug, slug.replace("_", " ").title())

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup.find_all(["nav", "header", "footer", "script", "style"]):
            tag.decompose()
        for tag in soup.find_all(class_=re.compile(r"cookie|banner|breadcrumb", re.I)):
            tag.decompose()

        main = soup.find("main") or soup.find("div", id="content") or soup.body or soup
        text = main.get_text(separator=" ", strip=True)
        text = re.sub(r"\s{2,}", " ", text).strip()

        yield {
            "country_code": "DE",
            "visa_type": visa_type,
            "content": text,
            "source_url": response.url,
            "scraped_at": datetime.now().isoformat(),
        }
