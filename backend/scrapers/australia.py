"""
Australia immigration policy scraper — Scrapy spider.

Sources: en.wikipedia.org — Wikipedia articles covering Australian skilled migration.
immi.homeaffairs.gov.au is SharePoint/JS-rendered (returns empty to Scrapy).
visaguide.world URLs also returned no content. Wikipedia provides comprehensive
coverage of skilled migration categories, points system, employer sponsorship,
graduate visas, and PR pathways including subclass-specific detail.
"""

import re
from datetime import datetime

import scrapy
from bs4 import BeautifulSoup

_URL_VISA_MAP = {
    "Immigration_to_Australia": "Australian Immigration System",
    "Points-based_immigration_system": "Points-Based Skilled Migration",
}

_DEFAULT_URLS = [
    "https://en.wikipedia.org/wiki/Immigration_to_Australia",
    "https://en.wikipedia.org/wiki/Points-based_immigration_system",
]


class AustraliaSpider(scrapy.Spider):
    name = "australia_immigration"
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

        main = soup.find("main") or soup.find("div", id="content") or soup.body or soup
        text = main.get_text(separator=" ", strip=True)
        text = re.sub(r"\s{2,}", " ", text).strip()

        yield {
            "country_code": "AU",
            "visa_type": visa_type,
            "content": text,
            "source_url": response.url,
            "scraped_at": datetime.now().isoformat(),
        }
