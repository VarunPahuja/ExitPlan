"""
Immigration scoring data for Indian international students.
Compiled May 2026. Sources cited inline in CITATIONS dict.

SCORING METHODOLOGY:
- All scores 0-100, higher = better for an Indian student/skilled worker.
- pr_timeline: 100 = under 2 years to PR, 80 = 2-3 years, 60 = ~5 years,
               40 = ~7 years, 20 = no real PR pathway (renewable visa only)
- visa_ease: 100 = fast (<1 month) + high approval, 60 = moderate, 30 = slow/uncertain
- salary_cost_ratio: 100 = best take-home vs local costs (after tax), 50 = average
- language: 100 = English-only suffices indefinitely, 50 = English works for job but local
            language needed for PR/integration, 20 = local language required from day 1
- job_market (per field): demand for that skill set in that country in 2026

Job market scoring rubric (since no public 0-100 source exists per-field per-country):
  90+ = on official shortage/critical skills list + strong hiring signal
  75-89 = strong demand, well-represented in immigration-friendly job postings
  60-74 = moderate demand, employable but competitive
  40-59 = limited demand or significant local-credential barriers
  <40 = very restricted (licensing barriers, nationality preference, small market)
"""

COUNTRY_DATA = {
    "GB": {
        "name": "United Kingdom",
        # 5-year ILR currently, but earned settlement reform proposes 10 years from 2026/27.
        # Scoring reflects current 5-year reality with downward pressure from uncertainty.
        "pr_timeline": 50,
        # Skilled Worker visa relatively straightforward but salary thresholds raised 2024-25,
        # social care recruitment ended July 2025, eligible job list shrunk.
        "visa_ease": 65,
        # London salaries decent but cost of living high; outside London ratio worsens for low/mid tier.
        "salary_cost_ratio": 60,
        "language": 100,  # English-native
        "job_market": {
            "computer_science": 82,   # London + Manchester tech hubs, on Skilled Worker list
            "data_science": 82,       # high demand, finance + AI sector
            "engineering": 70,        # solid but not on critical shortage like Germany
            "business": 68,           # competitive, MBA-heavy market
            "medicine": 88,           # NHS chronic shortages, doctors/nurses on shortage list
            "law": 55,                # qualification recognition barrier (SQE), UK-trained preferred
            "design": 65,             # London creative sector strong but visa-restricted
            "finance": 85,            # London = global finance hub
        },
    },

    "CA": {
        "name": "Canada",
        # Express Entry: ~7 months processing, total 9-18 months ITA-to-PR. Direct PR via EE.
        "pr_timeline": 88,
        # Points-based, high CRS cutoffs in 2024-25 but category-based draws help STEM/health/French.
        # Open work permit via PGWP for students.
        "visa_ease": 82,
        # Salaries moderate, Toronto/Vancouver housing crisis hurts ratio significantly.
        "salary_cost_ratio": 58,
        "language": 95,  # English (or French) is the official language; IELTS required.
        "job_market": {
            "computer_science": 85,   # Tech category draws, AI hub growth in Toronto/Montreal
            "data_science": 85,       # STEM category Express Entry draws
            "engineering": 82,        # consistent shortage, on most provincial NOC lists
            "business": 65,
            "medicine": 92,           # acute shortage, healthcare category draws prioritized
            "law": 50,                # NCA accreditation required, hard for foreign-trained
            "design": 62,
            "finance": 72,
        },
    },

    "DE": {
        "name": "Germany",
        # EU Blue Card: 21 months with B1 German, 27 months with A1. Skilled worker: 4 years.
        # German graduates: 2 years post-degree.
        "pr_timeline": 90,
        # Opportunity Card + Blue Card reforms 2024 made it among easiest in EU.
        # 163+ shortage occupations get reduced thresholds + waived priority check.
        "visa_ease": 88,
        # Strong salaries, lower cost of living than UK/NL, but high tax burden.
        "salary_cost_ratio": 72,
        # English works in many tech jobs, but B1 German needed for PR. Major barrier outside tech.
        "language": 55,
        "job_market": {
            "computer_science": 92,   # IT on bottleneck list, no degree required if 3+ yrs exp
            "data_science": 88,       # bottleneck profession, Blue Card threshold lowered
            "engineering": 95,        # Germany's #1 strength; massive shortage in mech/elec/auto
            "business": 60,           # German-language preferred
            "medicine": 90,           # acute shortage, but Approbation + B2/C1 German required
            "law": 30,                # German law degree (Staatsexamen) required
            "design": 58,
            "finance": 68,            # Frankfurt finance hub, but smaller than London
        },
    },

    "AU": {
        "name": "Australia",
        # Subclass 189: PR on grant, ~7-12 months processing. 491 → 191 = 3 years regional.
        "pr_timeline": 85,
        # Points-based, 65+ minimum but realistically 85-95 needed. Competitive but transparent.
        "visa_ease": 75,
        # High salaries, but Sydney/Melbourne housing very expensive.
        "salary_cost_ratio": 70,
        "language": 100,  # English-native
        "job_market": {
            "computer_science": 85,   # on MLTSSL skilled occupation list
            "data_science": 82,
            "engineering": 88,        # consistent shortage, multiple engineering occs on MLTSSL
            "business": 60,
            "medicine": 92,           # severe regional + urban shortages, fast-track pathways
            "law": 50,                # state-specific bar admission required
            "design": 60,
            "finance": 72,
        },
    },

    "NL": {
        "name": "Netherlands",
        # 5 years to PR. Time on Highly Skilled Migrant (Kennismigrant) permit counts directly.
        "pr_timeline": 60,
        # Fastest skilled-migrant processing in Europe (2-4 weeks). Employer-sponsored.
        # 30% tax ruling is huge financial advantage.
        "visa_ease": 92,
        # 30% ruling makes effective salaries excellent; Amsterdam housing tight but not catastrophic.
        "salary_cost_ratio": 78,
        # 90%+ adults speak English; #1 ranked English proficiency for non-native country.
        "language": 90,
        "job_market": {
            "computer_science": 88,   # Amsterdam tech hub, ASML/Booking/Adyen ecosystem
            "data_science": 85,
            "engineering": 82,        # ASML, semiconductor cluster in Eindhoven
            "business": 70,
            "medicine": 78,           # BIG registration + Dutch language required
            "law": 35,                # Dutch civil law tradition, qualification recognition difficult
            "design": 72,             # Eindhoven design heritage, English-friendly creative agencies
            "finance": 75,            # Amsterdam post-Brexit finance migration
        },
    },

    "PT": {
        "name": "Portugal",
        # PR still 5 years (unchanged by 2026 nationality reform); citizenship now 10 yrs.
        "pr_timeline": 55,
        # D7/D8/Tech visa accessible; AIMA backlogs have caused delays in 2024-25.
        "visa_ease": 60,
        # Salaries are by far the lowest of EU here; cost of living also low but ratio mediocre.
        # NHR 2.0 (IFICI) tax regime helps for qualifying scientific/innovation roles.
        "salary_cost_ratio": 45,
        # English widely spoken in Lisbon/Porto tech; A2 Portuguese needed for PR/citizenship.
        "language": 65,
        "job_market": {
            "computer_science": 72,   # Lisbon tech hub growing, but salary ceiling low
            "data_science": 65,
            "engineering": 55,
            "business": 50,
            "medicine": 68,           # SNS shortages but credential recognition + language
            "law": 30,                # Portuguese law degree required
            "design": 58,
            "finance": 50,
        },
    },

    "IE": {
        "name": "Ireland",
        # Critical Skills Employment Permit → Stamp 4 after 21 months. Fastest in EU for skilled tech.
        "pr_timeline": 90,
        # CSEP waives Labour Market Needs Test, 6-12 week processing. €40,904 salary threshold (Mar 2026).
        "visa_ease": 85,
        # Dublin tech salaries strong (FAANG presence), but Dublin housing among Europe's worst.
        "salary_cost_ratio": 58,
        "language": 100,  # English-native (and Irish, but English suffices)
        "job_market": {
            "computer_science": 92,   # Google/Meta/Apple/Microsoft Dublin HQs, CSEP-eligible
            "data_science": 88,
            "engineering": 78,
            "business": 65,
            "medicine": 88,           # severe HSE staffing shortages
            "law": 45,                # Law Society of Ireland qualification needed
            "design": 62,
            "finance": 78,            # IFSC Dublin, post-Brexit financial services growth
        },
    },

    "AE": {
        "name": "United Arab Emirates",
        # No traditional PR. Golden Visa = 10-year renewable residency (not citizenship/permanent).
        # Requires AED 30,000/month basic salary for skilled professional category.
        # Scoring here reflects "long-term stay" not "permanent residence" in the western sense.
        "pr_timeline": 35,
        # Employer-sponsored work visas are quick (weeks), but tied to employer.
        # Golden Visa easier if salary qualifies. No path to citizenship realistically.
        "visa_ease": 75,
        # Tax-free salaries, but Dubai/Abu Dhabi housing+schooling costs eat heavily.
        "salary_cost_ratio": 75,
        # English is the business lingua franca in Dubai/Abu Dhabi private sector.
        "language": 90,
        "job_market": {
            "computer_science": 80,   # AI Strategy 2031, strong demand
            "data_science": 82,       # fintech/regtech surge
            "engineering": 75,        # construction + oil/gas + renewables
            "business": 72,
            "medicine": 85,           # massive healthcare buildout, expat-friendly
            "law": 35,                # UAE/Sharia legal system, locals preferred
            "design": 60,
            "finance": 88,            # DIFC/ADGM growth, wealth management boom
        },
    },

    "NZ": {
        "name": "New Zealand",
        # Skilled Migrant Category: 6 points, ~40-124 days processing for residence visa.
        # AEWV work-to-residence pathway, plus Green List "Straight to Residence" for top occupations.
        "pr_timeline": 80,
        # Simplified points system since Oct 2023. Major reform Aug 2026 expected to widen access.
        "visa_ease": 78,
        # Salaries lower than Australia, cost of living high (Auckland especially).
        "salary_cost_ratio": 55,
        "language": 100,  # English-native
        "job_market": {
            "computer_science": 78,   # on Green List Tier 2, smaller market than AU
            "data_science": 75,
            "engineering": 82,        # multiple engineering roles on Green List Tier 1 (Straight to Residence)
            "business": 55,
            "medicine": 95,           # almost every healthcare role on Green List Tier 1, severe shortage
            "law": 45,                # NZ-specific admission required
            "design": 55,
            "finance": 60,
        },
    },

    "SG": {
        "name": "Singapore",
        # PR is discretionary, no fixed timeline. Typically 2+ years on EP before applying.
        # ICA approval rates not published; PR intake ~35-40k/year.
        "pr_timeline": 50,
        # EP salary floor S$5,600 (S$6,200 finance) from 2026, rising to S$6,000/6,600 in 2027.
        # COMPASS points system can reject even above-threshold candidates.
        # EP approval ~80%+ for strong candidates; processing ~3 weeks.
        "visa_ease": 70,
        # Tax-low, high salaries in finance/tech, but Singapore is one of world's most expensive cities.
        "salary_cost_ratio": 68,
        "language": 100,  # English is official language of business
        "job_market": {
            "computer_science": 88,   # regional tech HQs, sovereign cloud push
            "data_science": 85,
            "engineering": 70,
            "business": 70,
            "medicine": 72,           # MOH licensing complex, locals prioritized
            "law": 40,                # Singapore Bar required, foreign-qualified routes limited
            "design": 62,
            "finance": 92,            # APAC finance hub, wealth management booming
        },
    },
}


# Display metadata — visa programme names and estimated years to PR/long-term residence
COUNTRY_META: dict[str, dict] = {
    "GB": {"visa_types": ["Skilled Worker", "Graduate Route", "Global Talent"],          "pr_timeline_years": 5},
    "CA": {"visa_types": ["Express Entry", "PNP", "PGWP → PR"],                          "pr_timeline_years": 3},
    "DE": {"visa_types": ["EU Blue Card", "Job Seeker Visa", "Skilled Immigration Act"],  "pr_timeline_years": 2},
    "AU": {"visa_types": ["Skilled Independent (189)", "Employer Sponsored (482)", "Graduate (485)"], "pr_timeline_years": 3},
    "NL": {"visa_types": ["Highly Skilled Migrant", "Orientation Year", "EU Blue Card"],  "pr_timeline_years": 5},
    "PT": {"visa_types": ["D3 Tech Visa", "D8 Digital Nomad Visa", "Job Seeker Visa"],    "pr_timeline_years": 5},
    "IE": {"visa_types": ["Critical Skills Employment Permit", "General Employment Permit", "Stamp 4"], "pr_timeline_years": 2},
    "AE": {"visa_types": ["Golden Visa", "Employment Visa", "Green Visa"],                "pr_timeline_years": 10},
    "NZ": {"visa_types": ["Skilled Migrant", "Accredited Employer Work Visa", "Green List Straight to Residence"], "pr_timeline_years": 3},
    "SG": {"visa_types": ["Employment Pass", "S Pass", "Personalised Employment Pass"],   "pr_timeline_years": 7},
}


CITATIONS = {
    "GB": {
        "pr_timeline": {
            "source": "gov.uk + Migration Observatory (Oxford)",
            "note": "Currently 5-year ILR via Skilled Worker. White paper May 2025 proposes 10-year route under 'earned settlement' system, implementation expected 2026/27. Score reflects current rules with downward pressure from policy uncertainty.",
            "url": "https://migrationobservatory.ox.ac.uk/resources/commentaries/changes-to-settlement-what-do-they-mean/",
            "cited": True,
        },
        "visa_ease": {
            "source": "House of Commons Library briefing CBP-10267 (May 2026)",
            "note": "Skilled Worker eligibility list reduced 22 July 2025, social care closed to overseas recruitment. Higher salary thresholds. English requirement raised to B2 from 8 Jan 2026.",
            "cited": True,
        },
        "salary_cost_ratio": {
            "source": "Numbeo Quality of Life Index 2026 (UK ranked 22nd)",
            "note": "London salaries strong but housing/COL high; ratio below NL/DE.",
            "cited": True,
        },
        "language": {"source": "Official language: English", "cited": True},
        "job_market": {
            "computer_science": {"source": "UK Shortage Occupation List + Tech Nation reports", "note": "inferred from sector hiring data", "cited": False},
            "data_science": {"source": "Same as CS", "note": "inferred", "cited": False},
            "engineering": {"source": "MAC shortage occupation reviews", "note": "inferred", "cited": False},
            "business": {"source": "general market knowledge", "note": "inferred", "cited": False},
            "medicine": {"source": "NHS Long Term Workforce Plan + Skilled Worker list", "note": "cited: doctors and many nurse specialties are on shortage list", "cited": True},
            "law": {"source": "SQE/QLTS requirements", "note": "inferred from credential recognition barriers", "cited": False},
            "design": {"source": "general market knowledge", "note": "inferred", "cited": False},
            "finance": {"source": "City of London Corp + general knowledge of London as global finance hub", "note": "inferred from market position", "cited": False},
        },
    },

    "CA": {
        "pr_timeline": {
            "source": "IRCC processing times (March 2026)",
            "note": "Express Entry CEC/FSW: ~7 months processing, total ITA-to-PR ~9-18 months. Among fastest direct-PR pathways globally.",
            "url": "https://immigration.ca/canada-immigration-applications-processing-times/",
            "cited": True,
        },
        "visa_ease": {
            "source": "IRCC Express Entry + category-based draws",
            "note": "CRS cutoffs elevated in 2024-25 but STEM/healthcare/French category draws lowered thresholds. PGWP open work permit for students is significant advantage.",
            "cited": True,
        },
        "salary_cost_ratio": {
            "source": "Numbeo + Statistics Canada wage data",
            "note": "Toronto/Vancouver housing crisis significantly degrades ratio.",
            "cited": True,
        },
        "language": {"source": "IRCC IELTS/CELPIP requirements", "note": "CLB 7+ typical", "cited": True},
        "job_market": {
            "computer_science": {"source": "IRCC STEM category-based Express Entry draws", "note": "cited: STEM is explicit Express Entry priority", "cited": True},
            "data_science": {"source": "IRCC STEM category", "note": "cited", "cited": True},
            "engineering": {"source": "Provincial NOC in-demand lists (ON, BC, AB)", "note": "cited", "cited": True},
            "business": {"source": "general market", "note": "inferred", "cited": False},
            "medicine": {"source": "IRCC healthcare category-based draws", "note": "cited: explicit category", "cited": True},
            "law": {"source": "NCA (National Committee on Accreditation) requirements", "note": "inferred from credentialing barriers", "cited": False},
            "design": {"source": "general market", "note": "inferred", "cited": False},
            "finance": {"source": "Toronto financial sector size", "note": "inferred", "cited": False},
        },
    },

    "DE": {
        "pr_timeline": {
            "source": "§9 AufenthG + BAMF / EU Blue Card Germany 2026 (Aldag Legal)",
            "note": "EU Blue Card: 27 months → Niederlassungserlaubnis, 21 months with B1 German. German graduates: 2 years. Skilled worker: 4 years.",
            "url": "https://aldaglegal.com/en/eu-blue-card-germany-2026/",
            "cited": True,
        },
        "visa_ease": {
            "source": "Skilled Immigration Act + Opportunity Card",
            "note": "163+ bottleneck occupations get reduced Blue Card threshold (€45,934 in 2026) and waived priority check. Among most accessible EU systems for skilled non-EU workers.",
            "cited": True,
        },
        "salary_cost_ratio": {
            "source": "Numbeo 2026 + OECD wage data",
            "note": "Germany ranked top 10 quality of life; lower COL than UK/NL with comparable tech salaries (though pre-tax). Tax burden high but net ratio favorable.",
            "cited": True,
        },
        "language": {
            "source": "BAMF Niederlassungserlaubnis requirements",
            "note": "B1 German required for accelerated PR; A1 minimum for standard. Major barrier outside tech jobs.",
            "cited": True,
        },
        "job_market": {
            "computer_science": {"source": "Bottleneck occupation list 2026 (163 occupations)", "note": "cited: IT specialists explicitly listed, degree-optional with 3+ yrs experience", "cited": True},
            "data_science": {"source": "Bottleneck occupation list", "note": "cited as IT/data category", "cited": True},
            "engineering": {"source": "DIHK Skilled Labour Report 2025/2026; mech/elec/auto engineering on bottleneck list", "note": "cited", "cited": True},
            "business": {"source": "general market", "note": "inferred; German-language preference reduces score for non-native", "cited": False},
            "medicine": {"source": "DIHK report: ~46k healthcare vacancies, top shortage category", "note": "cited; but Approbation + B2/C1 German required", "cited": True},
            "law": {"source": "Staatsexamen requirement", "note": "inferred from structural barrier to foreign-trained lawyers", "cited": False},
            "design": {"source": "general market", "note": "inferred", "cited": False},
            "finance": {"source": "Frankfurt finance sector + general knowledge", "note": "inferred", "cited": False},
        },
    },

    "AU": {
        "pr_timeline": {
            "source": "Department of Home Affairs processing times (Feb 2026)",
            "note": "Subclass 189: 3-12 months, PR granted on visa approval. 190: 6-9 months. 491→191: 3 yrs regional then convert.",
            "cited": True,
        },
        "visa_ease": {
            "source": "SkillSelect points system",
            "note": "Min 65 points, realistic threshold 85-95. Transparent but competitive. State nomination (190) adds 5 pts, regional (491) adds 15.",
            "cited": True,
        },
        "salary_cost_ratio": {"source": "Numbeo + ABS wage data", "note": "High salaries, high housing costs in Sydney/Melbourne.", "cited": True},
        "language": {"source": "Official language: English", "cited": True},
        "job_market": {
            "computer_science": {"source": "MLTSSL skilled occupation list", "note": "cited: ICT roles on list", "cited": True},
            "data_science": {"source": "MLTSSL", "note": "cited as ICT/analytics roles", "cited": True},
            "engineering": {"source": "MLTSSL: multiple engineering occupations", "note": "cited", "cited": True},
            "business": {"source": "general market", "note": "inferred", "cited": False},
            "medicine": {"source": "MLTSSL + Health Workforce Australia shortage data", "note": "cited", "cited": True},
            "law": {"source": "State-by-state bar admission", "note": "inferred from credentialing barriers", "cited": False},
            "design": {"source": "general market", "note": "inferred", "cited": False},
            "finance": {"source": "Sydney finance hub", "note": "inferred", "cited": False},
        },
    },

    "NL": {
        "pr_timeline": {
            "source": "IND onbepaalde tijd verblijfsvergunning rules",
            "note": "5 years legal residence; Kennismigrant time counts directly toward this. Citizenship also 5 years (with A2 Dutch).",
            "cited": True,
        },
        "visa_ease": {
            "source": "IND + move2europe.eu 2026 guide",
            "note": "Highly Skilled Migrant (Kennismigrant) permit: 2-4 week processing, fastest in EU. Employer-sponsored. 30% ruling for 5 years adds major financial advantage.",
            "cited": True,
        },
        "salary_cost_ratio": {
            "source": "Numbeo Quality of Life 2026 - Netherlands ranked #1",
            "note": "30% ruling makes effective take-home excellent for qualifying migrants.",
            "url": "https://investinholland.com/news/netherlands-lands-top-spot-in-numbeo-quality-of-life-index-2026/",
            "cited": True,
        },
        "language": {
            "source": "EF English Proficiency Index + IND citizenship requirements",
            "note": "90%+ adults speak English; #1 EPI ranking for non-native country. A2 Dutch needed for citizenship but not for PR work.",
            "cited": True,
        },
        "job_market": {
            "computer_science": {"source": "Eurotoptech 2026 sponsorship list + Amsterdam tech ecosystem", "note": "cited: Booking, Adyen, ASML, Uber engineering all sponsor", "cited": True},
            "data_science": {"source": "Same as CS", "note": "inferred from same ecosystem", "cited": False},
            "engineering": {"source": "ASML/Philips Eindhoven cluster", "note": "inferred from sector concentration", "cited": False},
            "business": {"source": "general market", "note": "inferred", "cited": False},
            "medicine": {"source": "BIG registration requirements", "note": "inferred from licensing barrier + language requirement", "cited": False},
            "law": {"source": "Dutch civil law system", "note": "inferred from credentialing barrier", "cited": False},
            "design": {"source": "Dutch Design Week Eindhoven heritage", "note": "inferred", "cited": False},
            "finance": {"source": "Amsterdam post-Brexit financial services growth", "note": "inferred", "cited": False},
        },
    },

    "PT": {
        "pr_timeline": {
            "source": "Lei Orgânica n.º 1/2026 + Lei 23/2007",
            "note": "PR (autorização de residência permanente) still 5 years - UNCHANGED by 2026 reform. Citizenship extended from 5 to 10 years (7 for CPLP/EU). D7/D8/Tech visa all viable.",
            "url": "https://www.theportugalnews.com/news/2026-05-08/portugals-new-nationality-law-why-permanent-residency-is-the-goal-worth-focusing-on/1019162",
            "cited": True,
        },
        "visa_ease": {
            "source": "AIMA + immigrant-invest 2026",
            "note": "D7/D8 accessible; AIMA backlogs reported 2024-25. Online renewal portal launched Feb 2026.",
            "cited": True,
        },
        "salary_cost_ratio": {
            "source": "OECD + Numbeo",
            "note": "Lowest salaries in this list; COL also low but ratio mediocre. NHR 2.0 (IFICI) helps qualifying scientific/innovation roles.",
            "cited": True,
        },
        "language": {
            "source": "Article 6 Lei 1/2026 + Portugalist citizenship guide",
            "note": "A2 Portuguese required for PR and citizenship; English widely spoken in Lisbon/Porto tech.",
            "cited": True,
        },
        "job_market": {
            "computer_science": {"source": "Lisbon/Porto tech hub reports", "note": "inferred; growing but salary ceiling significantly lower than IE/NL", "cited": False},
            "data_science": {"source": "general market", "note": "inferred", "cited": False},
            "engineering": {"source": "general market", "note": "inferred", "cited": False},
            "business": {"source": "general market", "note": "inferred", "cited": False},
            "medicine": {"source": "SNS staffing reports", "note": "inferred from public health workforce gaps; credential recognition + language are barriers", "cited": False},
            "law": {"source": "Portuguese legal system", "note": "inferred from credentialing barrier", "cited": False},
            "design": {"source": "general market", "note": "inferred", "cited": False},
            "finance": {"source": "general market", "note": "inferred; Portugal finance sector small relative to peers", "cited": False},
        },
    },

    "IE": {
        "pr_timeline": {
            "source": "Citizens Information Ireland + Settle.ie 2026 guide",
            "note": "Critical Skills Employment Permit → Stamp 4 after 21-24 months. One of fastest paths to long-term residence in EU for skilled workers.",
            "url": "https://settle.ie/guides/critical-skills-permit/",
            "cited": True,
        },
        "visa_ease": {
            "source": "Department of Enterprise CSEP guide",
            "note": "CSEP waives Labour Market Needs Test, immediate family reunification, 6-12 week processing. Salary threshold €40,904 (Mar 2026) on Critical Skills List.",
            "cited": True,
        },
        "salary_cost_ratio": {
            "source": "Daft.ie + Eurostat wage data",
            "note": "Dublin tech salaries high (FAANG presence) but Dublin housing among Europe's worst.",
            "cited": True,
        },
        "language": {"source": "Official language: English (and Irish)", "cited": True},
        "job_market": {
            "computer_science": {"source": "Critical Skills Occupation List (Ireland)", "note": "cited: ICT professionals explicitly listed", "cited": True},
            "data_science": {"source": "Critical Skills Occupation List", "note": "cited as ICT", "cited": True},
            "engineering": {"source": "Critical Skills Occupation List", "note": "cited: multiple engineering occupations listed", "cited": True},
            "business": {"source": "general market", "note": "inferred", "cited": False},
            "medicine": {"source": "HSE workforce reports + Critical Skills List", "note": "cited: healthcare on critical list", "cited": True},
            "law": {"source": "Law Society of Ireland", "note": "inferred from credentialing barrier", "cited": False},
            "design": {"source": "general market", "note": "inferred", "cited": False},
            "finance": {"source": "IFSC Dublin + post-Brexit migration", "note": "inferred from sector growth", "cited": False},
        },
    },

    "AE": {
        "pr_timeline": {
            "source": "UAE Golden Visa rules (ICP/GDRFA)",
            "note": "No traditional PR/citizenship for typical workers. Golden Visa = 10-year renewable residency for AED 30,000+/month basic salary skilled professionals. Score reflects this is renewable residency, NOT permanent residence in legal sense.",
            "url": "https://www.globalcitizensolutions.com/golden-visa-uae/",
            "cited": True,
        },
        "visa_ease": {
            "source": "MoHRE + Hudson McKenzie 2026 guide",
            "note": "Employer work visa: days-to-weeks. Golden Visa straightforward if salary qualifies. Tied to employer for standard visa.",
            "cited": True,
        },
        "salary_cost_ratio": {
            "source": "Numbeo Dubai + GoDubai 2026 salary guide",
            "note": "Tax-free salaries, but Dubai housing + international schooling are expensive.",
            "cited": True,
        },
        "language": {
            "source": "MoHRE + basecareer.co 2026",
            "note": "English is private-sector business language; Arabic not required for most tech/finance/healthcare roles.",
            "cited": True,
        },
        "job_market": {
            "computer_science": {"source": "UAE AI Strategy 2031 + Dubai AI Roadmap", "note": "cited: explicit government priority", "cited": True},
            "data_science": {"source": "Qureos UAE Labor Market Analysis April 2026", "note": "cited: fintech/regtech surge", "cited": True},
            "engineering": {"source": "general market - construction/oil/renewables", "note": "inferred", "cited": False},
            "business": {"source": "general market", "note": "inferred", "cited": False},
            "medicine": {"source": "GoDubai 2026 - 4 of top 10 highest-paying careers", "note": "cited", "cited": True},
            "law": {"source": "UAE/Sharia legal system + Emiratisation", "note": "inferred from structural barriers - nationality preference + legal system", "cited": False},
            "design": {"source": "general market", "note": "inferred", "cited": False},
            "finance": {"source": "DIFC/ADGM + Michael Page UAE Salary Guide", "note": "cited: senior IB AED 50-90k/month, wealth management boom", "cited": True},
        },
    },

    "NZ": {
        "pr_timeline": {
            "source": "Immigration NZ + KPMG GMS Flash Alert 2025-181",
            "note": "Skilled Migrant Category: 40-124 days processing. Straight to Residence: 35-129 days. Green List Tier 1 = direct PR.",
            "url": "https://www.immigration.govt.nz/about-us/news-centre/changes-to-the-skilled-migrant-category-resident-visa-announced/",
            "cited": True,
        },
        "visa_ease": {
            "source": "INZ simplified points system (Oct 2023)",
            "note": "Only 6 points needed. Major Aug 2026 reform expected to widen access further. AEWV provides employer-sponsored interim path.",
            "cited": True,
        },
        "salary_cost_ratio": {
            "source": "Numbeo + Stats NZ",
            "note": "Salaries lower than AU; Auckland COL high.",
            "cited": True,
        },
        "language": {"source": "Official language: English", "cited": True},
        "job_market": {
            "computer_science": {"source": "NZ Green List Tier 2", "note": "cited: software roles on work-to-residence pathway", "cited": True},
            "data_science": {"source": "Green List Tier 2", "note": "cited", "cited": True},
            "engineering": {"source": "Green List Tier 1 - Straight to Residence", "note": "cited: multiple engineering occupations on top tier", "cited": True},
            "business": {"source": "general market", "note": "inferred from small NZ business sector", "cited": False},
            "medicine": {"source": "Green List Tier 1 - severe healthcare shortage", "note": "cited: nearly all healthcare specialties on top tier", "cited": True},
            "law": {"source": "NZLS admission requirements", "note": "inferred from credentialing barrier", "cited": False},
            "design": {"source": "general market", "note": "inferred", "cited": False},
            "finance": {"source": "general market", "note": "inferred - small NZ finance sector vs SG/UK", "cited": False},
        },
    },

    "SG": {
        "pr_timeline": {
            "source": "ICA PTS scheme + one-visa.com 2026 guide",
            "note": "PR discretionary, no published timeline. Typically 2+ years on EP before applying. ICA approval rates not published. PR intake ~35-40k/year. No guarantees.",
            "url": "https://www.one-visa.com/singapore-visa-resources/singapore-permanent-resident-pr-application/",
            "cited": True,
        },
        "visa_ease": {
            "source": "MOM Employment Pass + COMPASS",
            "note": "EP salary floor S$5,600 (S$6,200 finance) Jan 2026, rising to S$6,000/6,600 Jan 2027. COMPASS points can reject above-threshold candidates. ~80%+ EP approval, ~3 week processing for qualified candidates.",
            "cited": True,
        },
        "salary_cost_ratio": {
            "source": "Numbeo Singapore + MOM wage reports",
            "note": "High salaries especially in finance/tech, low income tax. But Singapore is among most expensive cities globally.",
            "cited": True,
        },
        "language": {"source": "English is official language of administration and business", "cited": True},
        "job_market": {
            "computer_science": {"source": "MOM Strategic Economic Plan + regional tech HQ concentration", "note": "inferred from sector concentration; sovereign cloud push", "cited": False},
            "data_science": {"source": "MAS + MOM tech talent priorities", "note": "inferred", "cited": False},
            "engineering": {"source": "general market", "note": "inferred", "cited": False},
            "business": {"source": "general market", "note": "inferred", "cited": False},
            "medicine": {"source": "MOH licensing rules", "note": "inferred from local-preference licensing", "cited": False},
            "law": {"source": "Singapore Bar admission rules", "note": "inferred from structural barriers", "cited": False},
            "design": {"source": "general market", "note": "inferred", "cited": False},
            "finance": {"source": "MAS + Singapore as APAC finance hub; EP floor higher for finance reflects sector concentration", "note": "cited via higher EP threshold for financial services indicating sector demand", "cited": True},
        },
    },
}
