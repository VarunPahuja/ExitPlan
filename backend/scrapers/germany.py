"""
Germany immigration policy scraper — Scrapy spider.

Source: gesetze-im-internet.de (Federal Ministry of Justice) — the authoritative
English translation of the German Residence Act (Aufenthaltsgesetz).

make-it-in-germany.com is blocked by Cloudflare and requires Playwright;
BAMF.de changed its URL structure. gesetze-im-internet.de is stable government
source with plain HTML that includes all visa rules: EU Blue Card (§18b),
Job Seeker Visa (§20), Skilled Immigration Act (§18a), etc.
"""

import re
from datetime import datetime

import scrapy
from bs4 import BeautifulSoup

_URL_VISA_MAP = {
    "englisch_aufenthg": "German Residence Act",
    "englisch_beschv": "Employment Regulation",
}

_DEFAULT_URLS = [
    "https://www.gesetze-im-internet.de/englisch_aufenthg/englisch_aufenthg.html",
    "https://www.gesetze-im-internet.de/englisch_beschv/englisch_beschv.html",
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
