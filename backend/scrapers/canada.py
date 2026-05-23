"""
Canada immigration policy scraper — Scrapy spider.

Scrapes canada.ca IRCC pages, extracts clean body text, and yields one
document per page.
"""

import re
from datetime import datetime

import scrapy
from bs4 import BeautifulSoup

_URL_VISA_MAP = {
    "express-entry": "Express Entry",
    "works": "Express Entry How It Works",
    "after-graduation": "Post-Graduation Work Permit",
    "provincial-nominees": "Provincial Nominee Program",
    "work-permit": "Temporary Work Permit",
    "understand-pr-status": "Permanent Residence",
}

_DEFAULT_URLS = [
    "https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry.html",
    "https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/works.html",
    "https://www.canada.ca/en/immigration-refugees-citizenship/services/study-canada/work/after-graduation.html",
    "https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/provincial-nominees.html",
    "https://www.canada.ca/en/immigration-refugees-citizenship/services/work-canada/permit/temporary/work-permit.html",
    "https://www.canada.ca/en/immigration-refugees-citizenship/services/new-immigrants/pr-card/understand-pr-status.html",
]


class CanadaSpider(scrapy.Spider):
    name = "canada_immigration"
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
        # canada.ca URLs end in .html — strip extension before slug lookup
        slug = response.url.rstrip("/").split("/")[-1].replace(".html", "")
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
            "country_code": "CA",
            "visa_type": visa_type,
            "content": text,
            "source_url": response.url,
            "scraped_at": datetime.now().isoformat(),
        }
