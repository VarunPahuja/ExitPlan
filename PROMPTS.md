# EXIT PLAN — PROMPTS.md
> Pre-written prompts for each agent, for each major task.
> Copy, fill in the [BRACKETS], paste into the agent. Never go in blind.

---

## CLAUDE CODE PROMPTS

### Session starter (paste this EVERY time)
```
I'm building Exit Plan — an AI-powered immigration country ranking platform.
Read the project context:

CURRENT STATE: [PASTE SECTION 2 OF CONTEXT.MD]
ACTIVE TASK: [PASTE THE SPECIFIC TASK]
FOLDER STRUCTURE: backend/ contains FastAPI app. frontend/ is owned by Lovable — do not touch it.
STACK: FastAPI, Supabase (Postgres + pgvector + Auth), Upstash Redis, Celery, sentence-transformers, OpenRouter, LangChain, Resend.
RULE: Only modify files relevant to this task. Tell me what to update in CONTEXT.md when done.
```

### Week 1 — Task 1: Repo + folder structure
```
Create the complete folder structure for Exit Plan backend.
Structure:
backend/
  main.py
  requirements.txt
  .env.example
  routers/ (rank.py, ask.py, profile.py, alerts.py, outcomes.py)
  services/ (scoring.py, rag.py, embeddings.py, scraper.py, change_detector.py, alert_engine.py)
  models/ (user.py, country.py, profile.py)
  db/ (supabase.py, migrations/)
  workers/ (celery_app.py)
  scrapers/ (uk.py, canada.py, germany.py)

Create each file with a docstring describing its purpose and empty placeholder functions.
Create requirements.txt with: fastapi, uvicorn, supabase, python-dotenv, celery, redis, langchain, sentence-transformers, flashrank, httpx, scrapy, playwright, beautifulsoup4, spacy, pytesseract, resend
Create .env.example with all variable names from CONTEXT.md section 7, no values.
```

### Week 1 — Task 2: Database schema
```
Create the Supabase database schema for Exit Plan.
Create backend/db/migrations/001_initial_schema.sql with these tables:

users: id (uuid pk), email (text unique), nationality (text), current_status (text), field (text), degree_level (text), savings_range (text), career_goal (text), weights (jsonb), saved_countries (text[]), created_at (timestamptz default now())

countries: id (uuid pk), name (text), code (text unique), region (text), active (boolean default true)

country_scores: id (uuid pk), country_id (uuid fk countries), profile_hash (text), job_score (int), pr_score (int), visa_score (int), salary_score (int), language_score (int), total_score (int), calculated_at (timestamptz default now())

policy_chunks: id (uuid pk), country_id (uuid fk countries), visa_type (text), content (text), source_url (text), effective_date (date), embedding vector(384), scraped_at (timestamptz default now())

policy_changes: id (uuid pk), country_id (uuid fk countries), visa_type (text), change_summary (text), detected_at (timestamptz default now()), old_value (text), new_value (text)

user_alerts: id (uuid pk), user_id (uuid fk users), country_id (uuid fk countries), alert_type (text), message (text), plain_english (text), sent_at (timestamptz), read_at (timestamptz), source_url (text)

outcomes: id (uuid pk), nationality (text), field (text), degree_level (text), destination_country (text), visa_type (text), months_to_job (int), summary (text), year (int), anonymous (boolean default true), verified (boolean default false), created_at (timestamptz default now())

Also seed the countries table with the 10 MVP countries: GB, CA, DE, AU, NL, PT, IE, AE, NZ, SG with their full names.
Enable pgvector extension: CREATE EXTENSION IF NOT EXISTS vector;
Create an ivfflat index on policy_chunks.embedding for fast similarity search.
```

### Week 1 — Task 3: FastAPI skeleton + /rank stub
```
Build the FastAPI skeleton for Exit Plan.

In backend/main.py: Create FastAPI app, include all routers, add CORS middleware (allow frontend URL from env), add a GET /health endpoint that returns {"status": "ok"}.

In backend/models/profile.py: Create Pydantic models for:
- UserWeights: job_market, pr_timeline, visa_ease, salary_cost_ratio, language (all floats, validator ensures they sum to 1.0, normalises if not)
- RankRequest: nationality, current_status, field, degree_level, savings_range, career_goal, weights (UserWeights)
- CountryScore: rank, country_code, country_name, total_score, scores (dict), verdict, visa_types, pr_timeline_years, last_updated
- GraphNode: id, label, total_score, tier
- GraphEdge: source, target, similarity, reason
- RankResponse: ranked_countries (list[CountryScore]), graph_data (nodes + edges), profile_hash, shareable_url

In backend/routers/rank.py: Create POST /rank endpoint. For now, return HARDCODED mock data for 3 countries (DE, CA, GB) using the RankResponse model. The scoring engine will replace this in Week 2.

In backend/services/scoring.py: Create a placeholder score() function with this signature:
def score(profile: RankRequest, country_data: dict) -> CountryScore
Add a docstring: "Applies user-declared weights from profile.weights to country factor scores. No hardcoded defaults."

Run the app with uvicorn and confirm /health and /rank return correct responses.
```

### Week 2 — Scoring engine
```
Build the scoring engine in backend/services/scoring.py.

The engine must:
1. Accept a RankRequest (with user-declared weights) and raw country data from the database
2. For each country, calculate factor scores (0-100) for: job_market, pr_timeline, visa_ease, salary_cost_ratio, language
3. Apply user weights: total_score = sum(factor_score * user_weight for each factor)
4. NEVER apply hardcoded defaults — use only what is in profile.weights
5. Calculate graph edges: similarity between country pairs = cosine similarity of their factor score vectors
6. Return a complete RankResponse

Country data (hardcode for now, will come from DB in Week 3):
DE: job_market=88, pr_timeline=75, visa_ease=80, salary_cost_ratio=85, language=55
CA: job_market=85, pr_timeline=70, visa_ease=88, salary_cost_ratio=72, language=95
GB: job_market=82, pr_timeline=65, visa_ease=85, salary_cost_ratio=68, language=98
AU: job_market=80, pr_timeline=72, visa_ease=82, salary_cost_ratio=70, language=96
NL: job_market=83, pr_timeline=78, visa_ease=79, salary_cost_ratio=80, language=88
PT: job_market=65, pr_timeline=80, visa_ease=75, salary_cost_ratio=82, language=72
IE: job_market=78, pr_timeline=68, visa_ease=83, salary_cost_ratio=65, language=97
AE: job_market=76, pr_timeline=45, visa_ease=70, salary_cost_ratio=88, language=90
NZ: job_market=72, pr_timeline=74, visa_ease=80, salary_cost_ratio=74, language=97
SG: job_market=79, pr_timeline=55, visa_ease=72, salary_cost_ratio=78, language=95

Verdict generation: call OpenRouter API (OPENROUTER_MODEL from env) with a prompt that takes the top 3 factor scores and generates a 1-sentence plain-English verdict. Keep prompt under 100 tokens.
```

---

## ANTIGRAVITY PROMPTS

### Utility functions
```
Project: Exit Plan (FastAPI backend, immigration ranking platform)
File to work on: backend/services/[FILENAME].py
Do NOT touch any other files.

Task: Write [SPECIFIC FUNCTION NAME] with this exact signature:
[PASTE FUNCTION SIGNATURE]

It should: [DESCRIBE WHAT IT DOES IN 2-3 SENTENCES]
Input: [DESCRIBE INPUT]
Output: [DESCRIBE OUTPUT]
Edge cases to handle: [LIST EDGE CASES]
```

---

## LOVABLE PROMPTS
> Always write these here in Claude first. Then copy into Lovable.

### Week 1 — Landing page
```
Build the Exit Plan landing page. Exit Plan is an AI-powered platform that gives international students a personalized country ranking based on their profile.

Design: Bright and optimistic. Electric indigo (#5B4FE8) primary, sunrise orange (#FF6B35) for CTAs, warm off-white (#FAFAF8) background. Font: Plus Jakarta Sans for headings, Inter for body. Feels alive and hopeful — not like a government website.

Sections:
1. Hero: Large headline "Your best country is out there." Subheadline: "Real-time country rankings, personalized to you. Not Reddit. Not a consultant." Orange CTA button: "Find my country →" (links to /profile). No login required copy below button.
2. How it works: 3 steps in a row with icons. Step 1: "Tell us about yourself" Step 2: "Set your priorities" Step 3: "Get your ranking + knowledge map"
3. Trust signals: Row of source logos/text: "Data from UKVI • IRCC • BAMF • DHA • LinkedIn" 
4. Footer: Exit Plan logo + tagline

No dark mode needed. Mobile responsive. Clean, generous whitespace. Score numbers should feel data-forward.
```

### Week 2 — Profile builder steps 1-3
```
Build a multi-step profile form for Exit Plan. This is /profile page, steps 1-3 of 5.

Design: Same as landing — electric indigo, sunrise orange CTAs, warm off-white, Plus Jakarta Sans headings.

Step 1 — Your background:
- Nationality dropdown (searchable, starts with India at top, then alphabetical)
- Current status: 3 large cards to select — "Currently studying", "Post-study visa", "Employed abroad"
- Progress bar at top showing Step 1 of 5

Step 2 — Your education:
- Field of study: searchable dropdown (Computer Science, Data Science, Engineering, Business, Medicine, Law, Design, Other)
- Degree level: 4 cards — Bachelors, Masters, PhD, Diploma
- Progress bar showing Step 2 of 5

Step 3 — Your finances:
- Savings range: 3 large cards with icons showing approximate amounts — "Under ₹5 Lakhs", "₹5–15 Lakhs", "₹15 Lakhs+"
- Progress bar showing Step 3 of 5

Navigation: Back and Next buttons. Next is orange. State persists across steps (use React state). On step 3 Next click, navigate to /profile/priorities (step 4).
```

### Week 2 — Profile builder steps 4-5
```
Build steps 4 and 5 of the Exit Plan profile builder.

Step 4 — Career goal:
3 large cards to select one:
- "Stay long-term & get PR" (icon: home)
- "Work experience then decide" (icon: briefcase)  
- "Return home eventually" (icon: arrow-left)
Progress bar showing Step 4 of 5.

Step 5 — Your priorities (THIS IS THE KEY SCREEN):
Headline: "What matters most to you?" Subheadline: "Drag to rank your priorities. Your ranking directly changes the results."

5 draggable cards in a vertical list. Each card has an icon, a label, and a short description:
1. Job Market — "How easy is it to find work in your field?"
2. PR Timeline — "How fast can you get permanent residency?"
3. Visa Ease — "How straightforward is the visa process?"
4. Salary vs Cost — "Will you actually save money there?"
5. Language — "How much does not knowing the local language hurt?"

As user drags to reorder, the weight percentages update in real time. Top card = highest weight. Weights are distributed as: 1st=35%, 2nd=25%, 3rd=20%, 4th=12%, 5th=8% based on position.

CTA button: "Find my countries →" (orange, full width). On click: POST to /rank with the full profile + computed weights, navigate to /results.

The drag interaction should feel smooth and satisfying. This is the most important screen in the product.
```

### Week 3 — Results page
```
Build the Exit Plan results page at /results.

Layout: Two-column. Left 40%: ranked country cards. Right 60%: knowledge graph (placeholder for now — just a div with id="knowledge-graph" and a loading state that says "Building your map...").

Left column — ranked cards:
Each country card shows:
- Country flag emoji + country name (large)
- Total score as a big number (animate count-up from 0 to final score on page load, 1 second duration)
- 5 factor score bars (labeled, colored by score: green >75, amber 50-75, red <50)
- One-line verdict text in italic
- Two small buttons: "Explore country" and "Ask AI"
Top card is elevated with an indigo border and a "Best match" badge in orange.

Above the cards: "Results for [nationality] • [field] • [degree]" and a "Adjust priorities" link that goes back to step 5.

Share button at top right: copies shareable URL to clipboard, shows "Copied!" toast.

Data: Fetch from POST /rank on page load using the profile stored in React state from the profile builder. Show a loading skeleton while fetching.

Mobile: Stack columns vertically. Graph goes below cards on mobile.
```