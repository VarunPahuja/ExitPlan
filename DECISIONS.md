# EXIT PLAN — DECISIONS.md
> Every non-obvious architectural or product decision lives here with its reason.
> Before relitigating a decision, read this file. If the reason still holds, the decision stands.
> Last updated: 2026-05-23

---

## ARCHITECTURE DECISIONS

---

### ADR-001: Gemini API directly, not OpenRouter
**Decision:** Use Google AI Studio API key to call Gemini directly via `services/llm.py` (httpx SSE). OpenRouter is not used.
**Reason:** Student Google AI Studio account has generous free access to Gemini 2.5 Flash (20 RPD) and gemini-3.1-flash-lite (500 RPD) — better models than any free OpenRouter option. One less service to manage, one less API key.
**Implementation:** `GEMINI_MODEL=gemini-3.1-flash-lite` for all /ask calls. `GEMINI_MODEL_PREMIUM=gemini-2.5-flash` available for complex queries. OpenRouter key is kept in .env as a fallback but no code currently calls it.
**Revisit if:** Gemini free tier gets rate-limited heavily in production. Fallback: switch to OpenRouter by pointing to the same interface with a different base URL.

---

### ADR-002: pgvector inside Supabase, not Pinecone
**Decision:** Use the pgvector extension inside Supabase Postgres as the vector store.
**Reason:** Supabase free tier includes pgvector. No extra service, no extra API key, no extra cost. At MVP scale (~300 policy chunks for 10 countries), pgvector performance is indistinguishable from Pinecone.
**Implementation:** `vector(384)` column in `policy_chunks`; ivfflat index in `001_initial_schema.sql`; `match_policy_chunks` RPC function deployed in Supabase.
**Revisit if:** Vector search becomes a bottleneck above 500k chunks. Migration to Pinecone is straightforward — same embedding format, different client.

---

### ADR-003: Local embeddings via sentence-transformers, not OpenAI
**Decision:** Use `all-MiniLM-L6-v2` from sentence-transformers, running on the dev machine.
**Reason:** Zero API cost, zero rate limits, runs offline. 384-dimensional embeddings — smaller than OpenAI's 1536-dim but sufficient for policy document retrieval at MVP scale. Downtime at embedding time does not affect query time.
**Implementation:** `services/embeddings.py`: `chunk_text` (512 words, 64 word overlap) → `embed` → `embed_and_store`. Run via `python ingest.py`.
**Revisit if:** Embedding quality is noticeably poor on retrieval. Upgrade path: `all-mpnet-base-v2` (better quality, same cost) or Gemini Embedding API (free tier, 768-dim).

---

### ADR-004: Scoring weights are 100% user-declared, no hardcoded defaults
**Decision:** The scoring engine applies exactly the weights the user sends. No backend defaults override user intent.
**Reason:** The product's core promise is personalization. Two users with identical profiles but different priorities must get different rankings. Hardcoded defaults would make us no better than a generic visa website.
**Implementation:** Weights come from the frontend drag-UI on step 5, sent in the /rank request body. Backend validates they sum to 1.0 and normalises if not. Backend never substitutes its own values.
**Revisit if:** User testing shows most users skip the weight step — then offer preset profiles ("I care most about PR speed") as starting points, not overrides.

---

### ADR-005: Frontend starts Week 1, parallel to backend
**Decision:** Lovable frontend development starts in Week 1, not after the backend is complete.
**Reason:** Lovable credits are limited. The frontend needs the full build period. API contract is locked in Week 1 so both sides can build independently without breaking each other.
**Rule:** Lovable prompt is always written in Claude (claude.ai) first. Never spend a credit on a vague prompt. Frontend uses localStorage mock data in early weeks; real API data from /rank and /ask when ready.

---

### ADR-006: Antigravity for boilerplate, Claude Code for architecture
**Decision:** Split code generation between Claude Code (complex, cross-file, architectural) and Antigravity (scoped, single-function, boilerplate).
**Reason:** Claude Code understands the full codebase but has a context budget. Antigravity is generous for code generation. Using Antigravity for repetitive tasks preserves Claude Code's context budget for hard problems.
**Hard rule:** Never run both on the same file simultaneously. Note in CONTEXT.md which files are owned by which agent.

---

### ADR-007: D3.js force-directed graph for the knowledge map
**Decision:** The results page shows a D3.js force-directed network graph of countries as a core feature, not a nice-to-have.
**Reason:** This is the visual differentiator. No immigration tool shows data this way. Obsidian-style node graphs are familiar to the target demographic. The graph shows country similarity clusters that ranked lists cannot convey.
**Implementation:** D3.js force simulation. Nodes = countries (size = total score, color = tier). Edges = cosine similarity between country pairs for the specific user profile, computed in `services/scoring.py` and returned in `graph_data` from /rank. Runs entirely in the browser — no extra backend call needed.
**Revisit if:** D3.js inside Lovable/Next.js proves difficult to integrate. Fallback: `react-force-graph` or `vis.js`.

---

### ADR-008: Upstash Redis for caching (not yet implemented)
**Decision:** Use Upstash Redis free tier for caching /rank responses by profile_hash.
**Reason:** Free tier (10k commands/day) is sufficient for MVP. HTTP-based access works from anywhere — no Redis server to manage. Scoring is deterministic for a given profile, so caching is safe.
**Status:** Not yet implemented. Not blocking launch. Implement after /alerts and change detector are done.
**Revisit if:** 10k commands/day is exceeded (good problem to have).

---

### ADR-009: Resend for transactional email, not SendGrid
**Decision:** Use Resend for sending policy-change alert emails.
**Reason:** Resend free tier is 3,000 emails/month. Cleaner API than SendGrid. Better developer experience. Free forever at MVP scale.
**Status:** Not yet implemented. Blocked on change_detector being built first.
**Revisit if:** 3,000 emails/month is exceeded.

---

### ADR-010: Hybrid RAG (pgvector similarity + keyword ilike), not vector-only
**Decision:** The /ask RAG pipeline merges results from two retrieval methods: pgvector cosine similarity search and Postgres `ilike` keyword search. FlashRank reranker was considered and dropped.
**Reason:** Legal and policy text has specific terminology (visa names, thresholds, dates) that semantic search alone misses. A user asking "Graduate Route salary threshold" needs keyword matching, not just vector similarity. The merged approach covers both. FlashRank added latency without meaningful quality improvement over the merged results.
**Implementation:** `services/rag.py`: runs both searches, deduplicates by chunk ID, returns top-k merged results to Gemini.

---

### ADR-011: Field-specific job_market scores
**Decision:** The `job_market` factor score is not a single number per country — it varies by the user's field of study.
**Reason:** Germany is excellent for engineering but mediocre for law. Canada is strong for computer science but weak for medicine (licensing barriers). A single job_market score would mislead users in professional fields.
**Implementation:** `data/country_scores.py`: `COUNTRY_DATA` dict has `job_market` as a nested dict keyed by field string (e.g., `"computer_science"`, `"medicine"`). `services/scoring.py` looks up the user's field before applying weights. 8 fields covered: computer_science, data_science, engineering, business, medicine, law, design, finance.

---

### ADR-012: Relevance filter on chunks before embedding (is_relevant_chunk)
**Decision:** Not every scraped paragraph gets embedded. `is_relevant_chunk()` in `services/embeddings.py` filters out administrative boilerplate before storing.
**Reason:** Quality over quantity. Germany's Residence Act scraped ~239 raw chunks but most are section headers, signatures, and administrative text with no policy information. Storing them pollutes retrieval and wastes Supabase storage. After filtering, DE drops to ~216 substantive chunks.
**Implementation:** `is_relevant_chunk(text)` checks for minimum length, filters common boilerplate patterns, and returns False for chunks that don't contain policy-relevant content.

---

### ADR-013: Manual curated MD docs for thin-scraped countries
**Decision:** Countries where scraping yields few chunks (SG, NL, CA, GB) are supplemented with manually written immigration briefs in `curated_immigration_data.md`.
**Reason:** Some government sites are JS-rendered or geo-blocked, yielding 1-13 chunks. That's not enough context for useful RAG answers. Rather than waiting for better scrapers, curated briefs written from authoritative sources fill the gap immediately.
**Implementation:** `scrapers/md_ingest.py` parses `curated_immigration_data.md` into structured documents. `ingest.py` runs this as Phase 1b before embedding. Curated docs are treated identically to scraped docs in the embedding pipeline.

---

### ADR-014: Monorepo — frontend and backend in the same git repo
**Decision:** `frontend/` and `backend/` live in the same git repository.
**Reason:** Simpler for a solo/small team build. No cross-repo coordination for shared types or API contract changes. One `git clone`, one place to look for everything.
**Tradeoff:** Lovable manages the `frontend/` folder — do not manually edit files Lovable owns, as it will overwrite them on the next generation.

---

## PRODUCT DECISIONS

---

### PDR-001: No login required for the first ranking
**Decision:** Users get their ranked country list without creating an account.
**Reason:** Removes friction at the highest drop-off moment. The result is the hook. Once they see it, they create an account to save it and get alerts.
**Implementation:** /rank and /ask are public endpoints. The shareable URL encodes the profile_hash. Login is prompted when the user tries to save a profile or enable alerts.

---

### PDR-002: Design is bright and optimistic, not dark or corporate
**Decision:** Palette is electric indigo (#5B4FE8) + sunrise orange (#FF6B35) on warm off-white (#FAFAF8). Not a dark dashboard.
**Reason:** The user is making one of the most hopeful decisions of their life — choosing a country to build their future. The product should feel like possibility, not bureaucracy.
**Typography:** Plus Jakarta Sans (display) + Inter (body). Both free on Google Fonts.

---

### PDR-003: All four pillars present in MVP, at reduced depth
**Decision:** Real-time data, proactive alerts, personalized ranking, and AI chat are all in the MVP — not post-MVP.
**Reason:** Any single pillar is replicable with a ChatGPT prompt. The combination is what makes Exit Plan defensible.
**Scope control:** 10 countries not 30; email alerts not push notifications; 8 fields not all professions.

---

## DECISION LOG TEMPLATE

When making a new decision, add it here:

```
### ADR-XXX / PDR-XXX: [Title]
**Decision:** What was decided.
**Reason:** Why. What alternatives were considered and rejected.
**Implementation:** How it works in the code (file, function, etc.).
**Revisit if:** The condition under which this decision should be reconsidered.
```
