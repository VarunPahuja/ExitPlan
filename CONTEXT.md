# EXIT PLAN — CONTEXT.md
> The single source of truth for all agents (Claude Code, Antigravity, Lovable, Claude claude.ai).
> Read this before starting any session. Update this after every session.
> Last updated: Week 0 (pre-build)

---

## 1. PROJECT SNAPSHOT

**What Exit Plan is:** Real-time, AI-powered platform that gives international students a personalized country ranking based on their profile — scored by their own declared priorities, visualized as a force-directed knowledge graph, with proactive alerts when immigration policies change.

**Current phase:** Current phase: Week 1-2 active build.

Backend core complete: folder structure, Supabase schema, 
FastAPI, auth, /rank scoring engine, /ask RAG streaming.
Frontend: landing page in Lovable (needs polish).

**Repo:** [ ADD YOUR GITHUB REPO URL HERE ]
**Supabase project:** [ ADD SUPABASE PROJECT URL HERE ]
**Lovable project:** [ ADD LOVABLE PROJECT URL HERE ]
**OpenRouter key:** [ ADD OPENROUTER API KEY HERE — never commit to git ]

---

## 2. WHAT IS ACTUALLY BUILT (update this every session)

| Layer | Status | Notes |
|-------|--------|-------|
| Repo + folder structure | ✅ Done | backend/ skeleton created — all routers, services, models, workers, scrapers |
| Supabase project + schema | ✅ Done | 001_initial_schema.sql created; run manually in Supabase SQL editor |
│ FastAPI      │ ✅ Done  │ /health returns db:true; all 5 routers wired skeleton with stubs; uvicorn running on port 8000     
| Auth (Google OAuth) | ✅ Done | services/auth.py: verify_jwt + get_current_user dependency; /profile and /alerts require Bearer token; /rank, /ask, /outcomes are public |
| /profile endpoint | ✅ Done | GET returns row or 404; PUT upserts with email from JWT; models in models/user.py |
| /rank endpoint | ✅ Done | POST /rank/ accepts RankRequest, returns RankResponse with 10 ranked countries + graph data + shareable URL |
| Scoring engine (user weights) | ✅ Done | services/scoring.py: weighted dot-product, auto-tier, rule-based verdict, cosine-similarity graph edges (>0.85) |
| Scraper (UK, Canada, Germany) | ✅ Done | UK (gov.uk), CA (canada.ca), DE (gesetze-im-internet.de — make-it-in-germany.com blocked by Cloudflare); runner.py has run_all_scrapers() |
| Embedding pipeline (sentence-transformers) | ✅ Done | services/embeddings.py: chunk_text+embed+embed_and_store; services/ingest.py; backend/ingest.py CLI — 245 chunks stored |
| pgvector setup in Supabase | ✅ Done | vector(384) column in policy_chunks; ivfflat index in 001_initial_schema.sql |
| /ask endpoint (RAG) | ✅ Done | POST /ask/ streams SSE; real pgvector search via match_policy_chunks RPC; mock fallback if no chunks |
| OpenRouter integration | ⏭ Skipped | Using Gemini directly via services/llm.py (httpx SSE); OpenRouter not needed |
| FlashRank reranker | ❌ Not started | |
| Change detector | ❌ Not started | |
| Upstash Redis + pub/sub | ❌ Not started | |
| Celery workers | ❌ Not started | |
| Resend email alerts | ❌ Not started | |
| Lovable landing page | ❌ Not started | |
| Lovable profile builder (steps 1-3) | ❌ Not started | |
| Lovable profile builder (steps 4-5, drag weights) | ❌ Not started | |
| Lovable results page (cards) | ❌ Not started | |
| Lovable knowledge graph (D3.js) | ❌ Not started | |
| Lovable AI chat panel | ❌ Not started | |
| Lovable alert dashboard | ❌ Not started | |
| Lovable outcome feed | ❌ Not started | |
| Outcome stories (manual seed) | ❌ Not started | |

---

## 3. ACTIVE TASK

**What is being worked on right now:**
Lovable frontend — profile builder + results page


**Who is working on it:**
Lovable (5 credits/day)

**Started:**
2026-05-21

**Expected output:**
`GET /health` returns 200. `POST /auth/login` and `GET /auth/callback` wired up via Supabase Auth.

> RULE: Only one active task at a time across all agents.
> Before starting a new task, mark the previous one complete in section 2.

---

## 4. CURRENT BLOCKERS

None yet. Add blockers here as they appear.

Format:
- [BLOCKER] Description — what needs to be decided or fixed before work can continue.

---

## 5. NEXT TASK QUEUE (in order)

1. Create GitHub repo + folder structure (Claude Code)
2. Create Supabase project, run schema migrations (Claude Code)
3. FastAPI skeleton — main.py, router files, health check endpoint (Claude Code)
4. Google OAuth via Supabase Auth — /auth/login, /auth/callback endpoints (Claude Code)
5. Lovable: landing page (Claude.ai to write prompt first, then spend credit) 
6. User profile model + /profile GET/PUT endpoint (Claude Code)
7. /rank endpoint with user-weight scoring engine (Claude Code + Antigravity)
8. Lovable: profile builder steps 1-3 (Claude.ai to write prompt first)
9. Lovable: profile builder steps 4-5 drag-weight UI (Claude.ai to write prompt first)
10. Lovable: results page with placeholder cards connected to /rank (Claude.ai to write prompt first)

---

## 6. FOLDER STRUCTURE

```
exit-plan/
├── CONTEXT.md              ← this file
├── API_CONTRACT.md         ← endpoint contracts (read before any frontend work)
├── DECISIONS.md            ← architectural decisions and reasons
├── .env.example            ← all env vars listed (no values)
├── .gitignore
│
├── backend/
│   ├── main.py             ← FastAPI app entry point
│   ├── requirements.txt
│   ├── .env                ← real env vars (gitignored)
│   ├── routers/
│   │   ├── rank.py         ← /rank endpoint
│   │   ├── ask.py          ← /ask endpoint (RAG + streaming)
│   │   ├── profile.py      ← /profile endpoint
│   │   ├── alerts.py       ← /alerts endpoint
│   │   └── outcomes.py     ← /outcomes endpoint
│   ├── services/
│   │   ├── scoring.py      ← personalization scoring engine
│   │   ├── rag.py          ← RAG query engine
│   │   ├── embeddings.py   ← sentence-transformers pipeline
│   │   ├── scraper.py      ← Scrapy + Playwright orchestrator
│   │   ├── change_detector.py
│   │   └── alert_engine.py
│   ├── models/
│   │   ├── user.py         ← Pydantic models
│   │   ├── country.py
│   │   └── profile.py
│   ├── db/
│   │   ├── supabase.py     ← Supabase client
│   │   └── migrations/     ← SQL migration files
│   ├── workers/
│   │   └── celery_app.py   ← Celery + task definitions
│   └── scrapers/
│       ├── uk.py
│       ├── canada.py
│       └── germany.py
│
└── frontend/               ← Lovable manages this entirely
    └── (do not manually edit — Lovable owns this folder)
```

---

## 7. ENVIRONMENT VARIABLES

All agents must know these exist. Never hardcode values.

```
# Supabase
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_KEY=

# OpenRouter (LLM rotation)
OPENROUTER_API_KEY=
OPENROUTER_MODEL=google/gemini-flash-1.5   ← change this one line to rotate models

# Upstash Redis
UPSTASH_REDIS_URL=
UPSTASH_REDIS_TOKEN=

# Resend (email)
RESEND_API_KEY=

# App
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

**OpenRouter free models available (rotate when rate-limited):**
- `google/gemini-flash-1.5` — fast, 1M context, best default
- `deepseek/deepseek-chat` — strong reasoning, very fast
- `meta-llama/llama-3.1-8b-instruct` — lightweight fallback
- `mistralai/mistral-7b-instruct` — reliable fallback

---

## 8. HOW TO USE THIS FILE WITH EACH AGENT

### Claude Code (terminal)
Paste this at the start of every session:
```
Read CONTEXT.md in the project root before doing anything.
Current task: [PASTE ACTIVE TASK FROM SECTION 3]
Do not modify any files outside the scope of this task.
After completing, tell me what to update in CONTEXT.md.
```

### Antigravity
Paste this at the start of every session:
```
Project: Exit Plan (immigration country ranking platform)
Stack: FastAPI backend, Next.js frontend (Lovable), Supabase, pgvector, OpenRouter
Current task: [PASTE SPECIFIC SCOPED TASK]
Do not touch: [LIST FILES CLAUDE CODE IS WORKING ON]
Relevant context: [PASTE ONLY THE SECTION OF CONTEXT.MD RELEVANT TO THIS TASK]
```

### Lovable (before spending a credit)
1. Come to Claude (claude.ai) first
2. Paste API_CONTRACT.md + the screen you want to build
3. Claude writes the Lovable prompt
4. You copy it into Lovable and spend the credit
5. After Lovable responds, update section 2 of this file

### Claude (claude.ai) — this conversation
Use for: architecture decisions, writing Lovable prompts, debugging strategy, updating this file.