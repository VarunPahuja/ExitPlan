"""
Portugal immigration policy scraper — Scrapy spider.

Source: en.wikipedia.org — Wikipedia's Immigration to Portugal article (83K chars)
covers D-series visa categories (D3 Tech Visa, D7, D8 Digital Nomad, D2 Entrepreneur),
NHR tax regime, and PR/citizenship pathways. Plain HTML, no JS required.

visaguide.world/europe/portugal-visa URLs were found to silently redirect to
unrelated pages (French tech visa content appeared for Portuguese visa URLs), making
the data unreliable. AIMA (formerly SEF) pages are in Portuguese only.
Wikipedia provides comprehensive, factual coverage of Portugal's immigration options.
"""

import re
from datetime import datetime

import scrapy
from bs4 import BeautifulSoup

_URL_VISA_MAP = {
    "Immigration_to_Portugal": "Portugal Immigration System",
}

_DEFAULT_URLS = [
    "https://en.wikipedia.org/wiki/Immigration_to_Portugal",
]


class PortugalSpider(scrapy.Spider):
    name = "portugal_immigration"
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
        slug = response.url.rstrip("/").split("/")[-1]
        visa_type = _URL_VISA_MAP.get(slug, slug.replace("-", " ").title())

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup.find_all(["nav", "header", "footer", "script", "style"]):
            tag.decompose()
        for tag in soup.find_all(class_=re.compile(r"cookie|banner|breadcrumb", re.I)):
            tag.decompose()

        main = soup.find("main") or soup.find("article") or soup.find("div", id="content") or soup.body or soup
        text = main.get_text(separator=" ", strip=True)
        text = re.sub(r"\s{2,}", " ", text).strip()

        yield {
            "country_code": "PT",
            "visa_type": visa_type,
            "content": text,
            "source_url": response.url,
            "scraped_at": datetime.now().isoformat(),
        }
