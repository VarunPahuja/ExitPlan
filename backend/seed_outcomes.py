"""
Seed anonymised real-world immigration outcome stories into the outcomes table.
Run from backend/ directory: python seed_outcomes.py
Re-running truncates and re-seeds all 25 stories.
"""

import os
from dotenv import load_dotenv

load_dotenv()

from db.client import admin_client

STORIES = [
    # ——— Original 10 ———
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
    # ——— 15 new stories ———
    {
        "nationality": "IN", "field": "Computer Science",
        "degree_level": "masters", "destination_country": "PT",
        "visa_type": "Tech Visa (D3)", "months_to_job": 3,
        "summary": "Secured a backend role at a Lisbon-based SaaS company before arrival and applied for the D3 Tech Visa. AIMA appointment took 3 months to schedule — book early. Cost of living is much lower than Dublin or Amsterdam but salaries reflect that.",
        "year": 2025, "verified": True,
    },
    {
        "nationality": "IN", "field": "Finance",
        "degree_level": "masters", "destination_country": "AE",
        "visa_type": "Employment Visa", "months_to_job": 2,
        "summary": "Joined a Dubai private equity fund on an employer-sponsored visa. Tax-free salary is genuinely transformative for savings. Golden Visa eligibility kicked in at the AED 30k basic salary mark — applied at year 2.",
        "year": 2024, "verified": True,
    },
    {
        "nationality": "IN", "field": "Engineering",
        "degree_level": "masters", "destination_country": "AU",
        "visa_type": "Skilled Independent (189)", "months_to_job": 3,
        "summary": "Electrical engineering role in Melbourne. Skills assessed by Engineers Australia during the 485 period. Got an invitation from SkillSelect with 90 points — age and Australian work experience were the deciding factors.",
        "year": 2024, "verified": True,
    },
    {
        "nationality": "IN", "field": "Computer Science",
        "degree_level": "masters", "destination_country": "SG",
        "visa_type": "Employment Pass", "months_to_job": 1,
        "summary": "Got EP for a product engineering role at a Series B fintech. COMPASS scoring was straightforward with a graduate degree and salary above the median. Singapore's infrastructure and proximity to India makes it feel manageable for first-time expats.",
        "year": 2025, "verified": True,
    },
    {
        "nationality": "IN", "field": "Design",
        "degree_level": "masters", "destination_country": "NL",
        "visa_type": "Highly Skilled Migrant", "months_to_job": 5,
        "summary": "UX design roles are harder to get than software engineering in Amsterdam — fewer companies sponsor and salary thresholds can be tight for junior designers. Landed a role at a Dutch design agency after 5 months. 30% ruling makes the net pay competitive.",
        "year": 2024, "verified": True,
    },
    {
        "nationality": "IN", "field": "Finance",
        "degree_level": "masters", "destination_country": "PT",
        "visa_type": "Digital Nomad Visa (D8)", "months_to_job": 2,
        "summary": "Used D8 Digital Nomad visa while continuing remote contract work for a UK fintech. Porto is genuinely affordable compared to Lisbon. NHR 2.0 tax regime gave a flat 20% tax rate on Portuguese-sourced income for 10 years.",
        "year": 2025, "verified": True,
    },
    {
        "nationality": "IN", "field": "Computer Science",
        "degree_level": "masters", "destination_country": "NZ",
        "visa_type": "Accredited Employer Work Visa", "months_to_job": 4,
        "summary": "Software engineering role in Auckland on AEWV. Market is smaller than Sydney but competition is noticeably lower. Applied for Skilled Migrant resident visa after 2 years — approved in 68 days after the ballot draw.",
        "year": 2024, "verified": True,
    },
    {
        "nationality": "IN", "field": "Engineering",
        "degree_level": "masters", "destination_country": "AE",
        "visa_type": "Employment Visa", "months_to_job": 3,
        "summary": "Structural engineering position with a major Abu Dhabi construction group. Visa processing was fast — under 2 weeks with employer support. No path to traditional citizenship or PR, but Golden Visa at 10 years gives long-term stability.",
        "year": 2023, "verified": True,
    },
    {
        "nationality": "IN", "field": "Data Science",
        "degree_level": "masters", "destination_country": "GB",
        "visa_type": "Skilled Worker", "months_to_job": 4,
        "summary": "Data science role at a London insurtech. Graduate Route gave 2 years runway to find a sponsor. The salary floor of £41,700 for Skilled Worker ruled out several offers — negotiated hard on the offer that cleared it.",
        "year": 2024, "verified": True,
    },
    {
        "nationality": "IN", "field": "Engineering",
        "degree_level": "masters", "destination_country": "CA",
        "visa_type": "Express Entry", "months_to_job": 2,
        "summary": "Chemical engineering role in Calgary via PGWP + Express Entry. Alberta PNP nomination boosted CRS score by 600 points — bypassed the federal pool entirely. PR confirmed 18 months after landing.",
        "year": 2024, "verified": True,
    },
    {
        "nationality": "IN", "field": "Computer Science",
        "degree_level": "bachelors", "destination_country": "DE",
        "visa_type": "EU Blue Card", "months_to_job": 5,
        "summary": "Non-EU degree required recognition through anabin database — IND equivalent. Process took 3 months but was smooth for an Indian IIT degree. Got Blue Card for a Hamburg logistics tech company. German PR in 21 months with B1 is absolutely achievable.",
        "year": 2025, "verified": True,
    },
    {
        "nationality": "IN", "field": "Engineering",
        "degree_level": "masters", "destination_country": "IE",
        "visa_type": "Critical Skills Employment Permit", "months_to_job": 3,
        "summary": "Hardware engineering role at a semiconductor firm in Cork. CSEP was straightforward — employer handled most of the paperwork. Stamp 4 after 2 years is the real prize: changed employers freely within 6 months of getting it.",
        "year": 2024, "verified": True,
    },
    {
        "nationality": "IN", "field": "Finance",
        "degree_level": "masters", "destination_country": "SG",
        "visa_type": "Employment Pass", "months_to_job": 2,
        "summary": "Quantitative analyst role at a Singapore hedge fund. EP approved with COMPASS score of 60+. No PR after 3 years of applications — ICA is opaque about rejections. Still renewing EP annually. Savings rate is extraordinary despite high rents.",
        "year": 2023, "verified": True,
    },
    {
        "nationality": "IN", "field": "Medicine",
        "degree_level": "masters", "destination_country": "AU",
        "visa_type": "Employer Sponsored (482)", "months_to_job": 1,
        "summary": "GP role in regional South Australia — direct employer sponsorship on 482 visa, bypassed the 485 queue entirely. Regional placement was mandatory for 2 years but led to 491 → 191 PR pathway. Rural loading made the salary higher than metro GP roles.",
        "year": 2025, "verified": True,
    },
    {
        "nationality": "IN", "field": "Engineering",
        "degree_level": "masters", "destination_country": "NL",
        "visa_type": "Highly Skilled Migrant", "months_to_job": 2,
        "summary": "Mechanical engineering role at an ASML supplier in Eindhoven. Kennismigrant permit processed in 10 days — one of the fastest in Europe. 30% ruling approved for 5 years. Started Dutch A2 evening classes immediately; the PR requirement is real and takes time.",
        "year": 2025, "verified": True,
    },
]


def seed():
    client = admin_client()

    existing = client.table("outcomes").select("id").execute()
    if existing.data:
        client.table("outcomes").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        print(f"Cleared {len(existing.data)} existing row(s).")

    result = client.table("outcomes").insert(STORIES).execute()
    print(f"Seeded {len(result.data)} outcome stories.")


if __name__ == "__main__":
    seed()
