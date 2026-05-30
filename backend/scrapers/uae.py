"""
UAE immigration policy scraper — Scrapy spider.

Sources: en.wikipedia.org — Wikipedia articles covering UAE immigration programs.
Golden visa (47K chars) covers the 10-year renewable visa, investor and skilled
professional requirements. Immigration to UAE covers general work permit categories.
DIFC article provides finance/free-zone employment context.

u.ae and government.ae TCP-timeout from non-UAE IPs (geo-blocked). mohre.gov.ae
requires session auth. globalcitizensolutions.com and expatica.com tested but
returned no content to Scrapy.
"""

import re
from datetime import datetime

import scrapy
from bs4 import BeautifulSoup

_URL_VISA_MAP = {
    "Golden_visa": "Golden Visa",
    "Immigration_to_the_United_Arab_Emirates": "UAE Work & Residency",
    "Dubai_International_Financial_Centre": "DIFC Free Zone Employment",
    "golden-visa-uae": "UAE Golden Visa (Practical Guide)",
}

_DEFAULT_URLS = [
    "https://en.wikipedia.org/wiki/Immigration_to_the_United_Arab_Emirates",
    "https://en.wikipedia.org/wiki/Golden_visa",
    "https://en.wikipedia.org/wiki/Dubai_International_Financial_Centre",
    "https://www.globalcitizensolutions.com/golden-visa-uae/",
]


class UAESpider(scrapy.Spider):
    name = "uae_immigration"
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
        # Strip .aspx extension from mohre.gov.ae URLs
        slug = slug.replace(".aspx", "")
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
            "country_code": "AE",
            "visa_type": visa_type,
            "content": text,
            "source_url": response.url,
            "scraped_at": datetime.now().isoformat(),
        }
