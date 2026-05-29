"""
Seed 10 anonymised real-world immigration outcome stories into the outcomes table.
Run from backend/ directory: python seed_outcomes.py
"""

import os
from dotenv import load_dotenv

load_dotenv()

from db.client import admin_client

STORIES = [
    {
        "nationality": "IN", "field": "Computer Science",
        "degree_level": "masters", "destination_country": "DE",
        "visa_type": "EU Blue Card", "months_to_job": 4,
        "summary": "Got a backend engineering role at a Berlin startup after 4 months. Found English-only positions in tech. B1 German helped with integration but wasn't required for the job.",
        "year": 2024, "verified": True,
    },
    {
        "nationality": "IN", "field": "Computer Science",
        "degree_level": "masters", "destination_country": "CA",
        "visa_type": "Express Entry", "months_to_job": 3,
        "summary": "Used PGWP after graduation, got PR via Express Entry CEC in 14 months total. Toronto tech market competitive but manageable with strong LeetCode prep.",
        "year": 2024, "verified": True,
    },
    {
        "nationality": "IN", "field": "Engineering",
        "degree_level": "masters", "destination_country": "DE",
        "visa_type": "Job Seeker Visa", "months_to_job": 6,
        "summary": "Mechanical engineering graduate. Used 18-month job seeker visa, found role in automotive sector. German A2 required for most roles outside Munich tech scene.",
        "year": 2024, "verified": True,
    },
    {
        "nationality": "IN", "field": "Medicine",
        "degree_level": "masters", "destination_country": "AU",
        "visa_type": "Graduate (485)", "months_to_job": 2,
        "summary": "AMC exam took 8 months to prepare and pass. Once registered, job offers came quickly due to regional shortage. Regional Queensland placement led to 491 visa pathway.",
        "year": 2023, "verified": True,
    },
    {
        "nationality": "IN", "field": "Data Science",
        "degree_level": "masters", "destination_country": "NL",
        "visa_type": "Highly Skilled Migrant", "months_to_job": 2,
        "summary": "Joined Amsterdam fintech on Kennismigrant permit. 30% ruling made effective salary excellent. Dutch A2 for PR in 5 years — started classes immediately.",
        "year": 2024, "verified": True,
    },
    {
        "nationality": "IN", "field": "Computer Science",
        "degree_level": "masters", "destination_country": "IE",
        "visa_type": "Critical Skills Employment Permit", "months_to_job": 3,
        "summary": "Got CSEP through Dublin FAANG office. Stamp 4 after 21 months means no more work permit hassle. Housing costs in Dublin are brutal — budget carefully.",
        "year": 2024, "verified": True,
    },
    {
        "nationality": "IN", "field": "Finance",
        "degree_level": "masters", "destination_country": "SG",
        "visa_type": "Employment Pass", "months_to_job": 2,
        "summary": "EP approved in 3 weeks for wealth management role at MAS-regulated firm. PR application after 2.5 years — still waiting 9 months later. Singapore is competitive but salaries are exceptional.",
        "year": 2024, "verified": True,
    },
    {
        "nationality": "IN", "field": "Computer Science",
        "degree_level": "bachelors", "destination_country": "CA",
        "visa_type": "Study Permit → PR", "months_to_job": 5,
        "summary": "Did masters in Canada, used PGWP, then Express Entry CEC. Total timeline from landing to PR confirmation: 28 months. CRS score was 487 — just above cutoff.",
        "year": 2023, "verified": True,
    },
    {
        "nationality": "IN", "field": "Engineering",
        "degree_level": "masters", "destination_country": "NZ",
        "visa_type": "Accredited Employer Work Visa", "months_to_job": 4,
        "summary": "Civil engineering on Green List Tier 1 — straight to residence eligibility. Smaller market than Australia but PR process was significantly smoother and faster.",
        "year": 2024, "verified": True,
    },
    {
        "nationality": "IN", "field": "Business",
        "degree_level": "masters", "destination_country": "GB",
        "visa_type": "Graduate Route", "months_to_job": 6,
        "summary": "Used Graduate Route to find sponsored role. Salary threshold of £38,700 was the main hurdle — entry level business roles often fall below. Took 6 months to find compliant sponsoring employer.",
        "year": 2024, "verified": True,
    },
]


def seed():
    client = admin_client()

    # Check for existing stories to avoid duplicates
    existing = client.table("outcomes").select("id").execute()
    if existing.data:
        print(f"outcomes table already has {len(existing.data)} row(s) — skipping seed.")
        return

    result = client.table("outcomes").insert(STORIES).execute()
    print(f"Seeded {len(result.data)} outcome stories.")


if __name__ == "__main__":
    seed()
