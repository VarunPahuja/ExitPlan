"""
New Zealand immigration policy scraper — Scrapy spider.

Source: immigration.govt.nz (Immigration New Zealand) — the official NZ government
immigration portal. Covers Skilled Migrant, AEWV, and Straight to Residence pathways.
Plain HTML, no Cloudflare blocking.
"""

import re
from datetime import datetime

import scrapy
from bs4 import BeautifulSoup

_URL_VISA_MAP = {
    "skilled-migrant-category-resident-visa": "Skilled Migrant",
    "accredited-employer-work-visa": "Accredited Employer Work Visa",
    "straight-to-residence-visa": "Straight to Residence",
}

_DEFAULT_URLS = [
    "https://www.immigration.govt.nz/new-zealand-visas/visas/visa/skilled-migrant-category-resident-visa",
    "https://www.immigration.govt.nz/new-zealand-visas/visas/visa/accredited-employer-work-visa",
    "https://www.immigration.govt.nz/new-zealand-visas/visas/visa/straight-to-residence-visa",
]


class NewZealandSpider(scrapy.Spider):
    name = "newzealand_immigration"
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
            "country_code": "NZ",
            "visa_type": visa_type,
            "content": text,
            "source_url": response.url,
            "scraped_at": datetime.now().isoformat(),
        }
