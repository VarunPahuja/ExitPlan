"""
UK immigration policy scraper — Scrapy spider.

Scrapes gov.uk visa pages, extracts clean body text (headings, paragraphs,
salary figures, date references), and yields one document per page.
"""

import re
from datetime import datetime

import scrapy
from bs4 import BeautifulSoup

_URL_VISA_MAP = {
    "skilled-worker-visa": "Skilled Worker",
    "graduate-visa": "Graduate Route",
    "global-talent-visa": "Global Talent",
}

_DEFAULT_URLS = [
    "https://www.gov.uk/skilled-worker-visa",
    "https://www.gov.uk/graduate-visa",
    "https://www.gov.uk/global-talent-visa",
]


class UKSpider(scrapy.Spider):
    name = "uk_immigration"
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

        # Drop chrome — nav, header, footer, scripts, cookie banners
        for tag in soup.find_all(["nav", "header", "footer", "script", "style"]):
            tag.decompose()
        for tag in soup.find_all(class_=re.compile(r"cookie|banner|breadcrumb", re.I)):
            tag.decompose()

        # Prefer <main> content, fall back to full body
        main = soup.find("main") or soup.find("div", id="content") or soup.body or soup
        text = main.get_text(separator=" ", strip=True)
        text = re.sub(r"\s{2,}", " ", text).strip()

        yield {
            "country_code": "GB",
            "visa_type": visa_type,
            "content": text,
            "source_url": response.url,
            "scraped_at": datetime.now().isoformat(),
        }
