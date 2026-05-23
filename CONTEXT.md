# EXIT PLAN — CONTEXT.md
> The single source of truth for all agents (Claude Code, Antigravity, Lovable, Claude claude.ai).
> Read this before starting any session. Update this after every session.
> Last updated: 2026-05-23

---

## 1. PROJECT SNAPSHOT

**What Exit Plan is:** AI-powered immigration country ranking platform for Indian international students. Personalized country rankings based on field, finances, and career goal. AI chat answering real visa questions from scraped government sources. Proactive alerts when immigration policies change.

**Current phase:** Week 2 active build. Backend core is complete. Frontend exists in Lovable but the results page and knowledge graph are hardcoded/placeholder — connecting real API data is the immediate next task.

**Target user:** Indian international students deciding where to emigrate post-graduation. Not consultants, not Reddit — real data, personalized to them.

---

## 2. WHAT IS ACTUALLY BUILT

| Component | Status | Notes |
|-----------|--------|-------|
| Repo + folder structure | ✅ Done | backend/ with routers/, services/, models/, db/, workers/, scrapers/, data/ |
| Supabase schema | ✅ Done | users, countries, country_scores, policy_chunks, policy_changes, user_alerts, outcomes tables; pgvector enabled |
| FastAPI skeleton | ✅ Done | main.py, CORS, all routers registered; /health returns `{db: true}` |
| Auth (JWT) | ✅ Done | services/auth.py: verify_jwt + get_current_user; /profile and /alerts require Bearer token; /rank and /ask are public |
| /profile endpoint | ✅ Done | GET returns user row or 404; PUT upserts with email from JWT |
| /rank endpoint | ✅ Done | POST /rank/ accepts RankRequest, returns full RankResponse: 10 ranked countries + graph_data + profile_hash + shareable_url |
| GET /rank/preview | ✅ Done | Returns RankResponse with equal weights (public, no auth) |
| Scoring engine | ✅ Done | services/scoring.py: weighted dot-product, field-specific job_market scores, auto-tier, cosine similarity graph edges |
| Country data | ✅ Done | data/country_scores.py: research-backed scores with citations for all 10 countries, field-specific job_market scores for 8 fields; COUNTRY_META has visa_types and pr_timeline_years |
| Scrapers — all 10 countries | ✅ Done | UK (gov.uk 8 pages), CA (canada.ca 6 pages), DE (Residence Act full), AU/AE/PT (Wikipedia fallback), NL (ind.nl), IE (enterprise.gov.ie + irishimmigration.ie), NZ (immigration.govt.nz), SG (mom.gov.sg); runner.py has run_all_scrapers() |
| Relevance filter | ✅ Done | is_relevant_chunk() in embeddings.py; filters admin boilerplate before embedding |
| Embedding pipeline | ✅ Done | services/embeddings.py: all-MiniLM-L6-v2 local, chunk_text (512 words, 64 overlap), embed_and_store; ingest.py CLI |
| pgvector in Supabase | ✅ Done | vector(384) column + ivfflat index; match_policy_chunks RPC function deployed |
| Hybrid RAG | ✅ Done | services/rag.py: pgvector similarity search + keyword ilike merged; no FlashRank (not needed) |
| /ask endpoint | ✅ Done | POST /ask/ streams SSE via Gemini 2.5 Flash; citations in final chunk |
| Gemini integration | ✅ Done | services/llm.py: gemini-3.1-flash-lite (500 RPD free) primary; gemini-2.5-flash premium fallback; streaming SSE |
| Manual curated docs | ✅ Done | scrapers/md_ingest.py parses curated_immigration_data.md (SG, NL, CA, GB detailed briefs) into structured docs |
| Ingest pipeline | ✅ Done | ingest.py: Phase 1a (scrapers) + Phase 1b (manual docs) + Phase 2 (embed + store) |
| Policy chunks in DB | ✅ Done | DE=216, NZ=30, AU=28, PT=28, AE=24, IE=13, GB=12+manual, CA=8+manual, SG=2+manual, NL=1+manual |
| /alerts endpoint | 🟡 Stub | GET /alerts/ returns stub response; CRUD not implemented |
| Change detector | ❌ Not built | services/change_detector.py is a stub file |
| Resend email alerts | ❌ Not built | services/alert_engine.py is a stub file |
| Celery workers | ❌ Not built | workers/celery_app.py is a stub file |
| Upstash Redis | ❌ Not built | Not blocking anything currently |
| Lovable — landing page | 🟡 Built | Editorial design complete; needs hero image swap |
| Lovable — profile builder | ✅ Done | 5-step form, all steps working; drag priority UI on step 5; POSTs to /rank on submit |
| Lovable — results page | ❌ Hardcoded | Page exists but renders hardcoded data; must read from localStorage "exitplan_results" and render real API response |
| Lovable — knowledge graph | ❌ Placeholder | Div with id="knowledge-graph" exists; needs real D3.js force simulation using graph_data from /rank |
| Lovable — AI chat page | 🟡 Placeholder | Exists per country; not wired to /ask |
| Lovable — alert dashboard | 🟡 Placeholder | Exists; not wired to /alerts |
| Lovable — sign in page | ❌ Not built | Google OAuth via Supabase Auth; not started |

---

## 3. ACTIVE TASK

**What is being worked on right now:** None.

> RULE: Only one active task at a time across all agents. Before starting, update this section. After completing, mark it done in section 2.

---

## 4. CURRENT BLOCKERS

None.

---

## 5. NEXT TASK QUEUE (priority order)

### Backend must-haves (before launch)
1. `/alerts` endpoint — full CRUD: GET list, POST subscribe to country, DELETE unsubscribe, PUT preferences (Claude Code)
2. Change detector — diff new scrape against stored chunks, write to policy_changes table when delta detected (Claude Code)
3. Resend email — trigger email via Resend API when change_detector writes a new policy_change (Claude Code)

### Frontend must-haves (before launch)
4. Results page — read from localStorage `"exitplan_results"`, render real ranked cards with animated score count-up and factor bars (Lovable — use prompt from PROMPTS.md Section 3)
5. Knowledge graph — D3.js force simulation using graph_data from /rank response; click node highlights corresponding country card (Lovable — use prompt from PROMPTS.md Section 3)
6. Sign in page — Google OAuth via Supabase Auth; redirect to /profile after sign-in (Lovable — use prompt from PROMPTS.md Section 3)

### Nice-to-have (post-launch)
7. Wire AI chat page to /ask endpoint
8. Wire alert dashboard to /alerts endpoint
9. Celery scheduled scraping (replace manual run)
10. Upstash Redis caching for /rank responses
11. Outcome stories — manual seed from Reddit/forums

---

## 6. FOLDER STRUCTURE

```
exit-plan/
├── CONTEXT.md                          ← this file — read before every session
├── API_CONTRACT.md                     ← endpoint contracts — read before any frontend work
├── DECISIONS.md                        ← all architectural decisions with reasons
├── PROMPTS.md                          ← ready-to-paste prompts for every agent
├── curated_immigration_data.md         ← manual immigration briefs (SG, NL, CA, GB)
│
├── backend/
│   ├── main.py                         ← FastAPI app entry, CORS, router registration
│   ├── requirements.txt
│   ├── ingest.py                       ← CLI: runs scrapers + embeddings pipeline
│   ├── .env                            ← real env vars (gitignored)
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   └── country_scores.py           ← research-backed scores + field-specific job_market + COUNTRY_META
│   │
│   ├── db/
│   │   ├── client.py
│   │   ├── supabase.py                 ← Supabase client init
│   │   └── migrations/
│   │       ├── 001_initial_schema.sql  ← all tables + pgvector index
│   │       └── 002_match_chunks.sql    ← match_policy_chunks RPC function
│   │
│   ├── models/
│   │   ├── profile.py                  ← RankRequest, RankResponse, UserWeights, CountryScore, GraphNode, GraphEdge
│   │   └── user.py                     ← ProfileResponse, UserProfile
│   │
│   ├── routers/
│   │   ├── rank.py                     ← POST /rank/, GET /rank/preview
│   │   ├── ask.py                      ← POST /ask/ (SSE stream)
│   │   ├── profile.py                  ← GET /profile/, PUT /profile/
│   │   ├── alerts.py                   ← GET /alerts/ (stub)
│   │   └── outcomes.py                 ← GET /outcomes/ (stub)
│   │
│   ├── scrapers/
│   │   ├── uk.py                       ← gov.uk, 8 pages
│   │   ├── canada.py                   ← canada.ca, 6 pages
│   │   ├── germany.py                  ← gesetze-im-internet.de, full Residence Act
│   │   ├── australia.py                ← Wikipedia fallback
│   │   ├── netherlands.py              ← ind.nl
│   │   ├── ireland.py                  ← enterprise.gov.ie + irishimmigration.ie
│   │   ├── uae.py                      ← Wikipedia fallback
│   │   ├── newzealand.py               ← immigration.govt.nz
│   │   ├── singapore.py                ← mom.gov.sg
│   │   ├── portugal.py                 ← Wikipedia fallback
│   │   ├── runner.py                   ← run_all_scrapers() for all 10
│   │   ├── md_ingest.py                ← parses curated_immigration_data.md into structured docs
│   │   └── manual_docs/
│   │       └── curated_immigration_data.md
│   │
│   ├── services/
│   │   ├── auth.py                     ← verify_jwt, get_current_user FastAPI dependency
│   │   ├── scoring.py                  ← weighted dot-product, field-specific scores, cosine similarity graph edges
│   │   ├── rag.py                      ← hybrid retrieval: pgvector + keyword ilike
│   │   ├── llm.py                      ← Gemini 2.5 Flash via Google AI Studio, streaming SSE
│   │   ├── embeddings.py               ← all-MiniLM-L6-v2, chunk_text, embed_and_store, is_relevant_chunk
│   │   ├── ingest.py                   ← orchestrates Phase 1a + 1b + Phase 2
│   │   ├── scraper.py                  ← shared scraper utilities
│   │   ├── change_detector.py          ← STUB: diffs scrapes vs stored chunks
│   │   └── alert_engine.py             ← STUB: sends Resend email on policy change
│   │
│   └── workers/
│       └── celery_app.py               ← STUB: Celery app + scheduled tasks
│
└── frontend/                           ← Lovable manages this entirely
    └── (do not manually edit — Lovable owns this folder)
```

---

## 7. ENVIRONMENT VARIABLES

All in `backend/.env`. Never hardcode values. Never commit `.env` to git.

```bash
# Supabase
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_KEY=

# Gemini (Google AI Studio)
GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.1-flash-lite          # primary — 500 RPD free
GEMINI_MODEL_PREMIUM=gemini-2.5-flash       # premium — 20 RPD free

# OpenRouter (kept as fallback, not currently used)
OPENROUTER_API_KEY=
OPENROUTER_MODEL=google/gemma-4-31b:free

# Upstash Redis (not yet set up)
UPSTASH_REDIS_URL=
UPSTASH_REDIS_TOKEN=

# Resend (not yet set up)
RESEND_API_KEY=

# App URLs
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

---

## 8. HOW TO USE EACH AGENT

### Claude Code (terminal — for backend architecture and complex changes)
Paste at the start of every session:
```
Read CONTEXT.md before doing anything.
Current task: [PASTE ACTIVE TASK FROM SECTION 3]
Do not modify files outside the scope of this task.
After completing, tell me what to update in CONTEXT.md sections 2 and 3.
```
Use Claude Code for: new endpoints, service logic, schema changes, debugging, anything that touches multiple files.

### Antigravity (for scoped single-function boilerplate)
Paste at the start of every session:
```
Project: Exit Plan (FastAPI backend, immigration ranking platform)
Stack: FastAPI, Python, Supabase (Postgres + pgvector), sentence-transformers, Gemini API
File to work on: backend/services/[FILENAME].py
Do NOT touch any other files.
Task: [SPECIFIC SCOPED TASK]
```
Use Antigravity for: utility functions, helper methods, one-file additions that don't need full codebase context. Preserves Claude Code's context budget for hard problems.

**Hard rule:** Never run both Claude Code and Antigravity on the same file simultaneously. Note which files are owned by which agent.

### Lovable (for frontend — always write prompt here first)
1. Come to Claude (claude.ai) first
2. Pick the prompt from PROMPTS.md Section 3 for the screen you want to build
3. Paste it into Lovable
4. After Lovable responds, update section 2 of this file

Never spend a Lovable credit on a vague prompt. Every prompt must reference exact field names and enum values from API_CONTRACT.md.

### Claude (claude.ai — this conversation)
Use for: architecture decisions, writing and refining Lovable prompts, debugging strategy, updating context files. Not for running code — that's Claude Code's job.
