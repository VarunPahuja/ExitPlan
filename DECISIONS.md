# EXIT PLAN — DECISIONS.md
> Every non-obvious architectural or product decision lives here with its reason.
> Before relitigating a decision, read this file. If the reason still holds, the decision stands.
> Last updated: Week 0

---

## ARCHITECTURE DECISIONS

---

### ADR-001: OpenRouter instead of direct Gemini/OpenAI API
**Decision:** Use OpenRouter as the single LLM gateway.
**Reason:** Model rotation without code changes. When one free model hits rate limits, change `OPENROUTER_MODEL` in .env and redeploy. One API key, one endpoint, access to every major LLM. Free models available (Gemini Flash, DeepSeek, Llama 3).
**Model priority order:** Gemini 1.5 Flash → DeepSeek Chat → Llama 3.1 8B → Mistral 7B
**What this means in code:** One config variable. `OPENROUTER_MODEL=google/gemini-flash-1.5`. Change this string when needed.
**Revisit if:** OpenRouter goes down or removes free tier. Fallback: direct Gemini API (same code, different base URL).

---

### ADR-002: pgvector instead of Pinecone
**Decision:** Use pgvector extension inside Supabase Postgres as the vector store.
**Reason:** Supabase free tier includes pgvector. No extra service, no extra cost, no extra API key. At MVP scale (10 countries, ~50k policy chunks max), pgvector performance is indistinguishable from Pinecone.
**Revisit if:** Vector search becomes a bottleneck above 500k chunks. Migration to Pinecone is straightforward — same embedding format.

---

### ADR-003: sentence-transformers running locally for embeddings
**Decision:** Use `all-MiniLM-L6-v2` from sentence-transformers, running on the dev machine.
**Reason:** Zero API cost, zero rate limits, runs offline. 384-dimensional embeddings — smaller than OpenAI's but sufficient for policy document retrieval at MVP scale.
**Tradeoff:** Slower than API-based embedding on first run (model download ~80MB). After that, fast.
**Revisit if:** Embedding quality is noticeably poor on retrieval. Upgrade path: `all-mpnet-base-v2` (better quality, same cost) or Gemini embedding API (free tier).

---

### ADR-004: Scoring weights are 100% user-declared, no hardcoded defaults
**Decision:** The backend scoring engine applies whatever weights the user sends. No defaults override user intent.
**Reason:** The product's core promise is personalization. Two users with identical profiles but different priorities should get different rankings. Hardcoded defaults would make us no better than a generic visa website.
**Implementation:** Weights come from the frontend drag-UI, sent in the /rank request body. Backend validates they sum to 1.0 and normalises if not. Backend never substitutes its own values.
**Revisit if:** User testing shows most users skip the weight step — then we can offer preset profiles ("I care most about PR speed", "I care most about jobs") as starting points, not overrides.

---

### ADR-005: Frontend starts Week 1, parallel to backend
**Decision:** Lovable frontend development starts in Week 1, not after backend is complete.
**Reason:** 5 Lovable credits/day means the frontend needs the full 8 weeks. API contract is locked Week 1 so both sides can build independently without breaking each other.
**Risk:** Frontend may temporarily use mock data before backend endpoints are ready. That is intentional — mock data in Week 1-2, real data from Week 3 onwards.
**Rule:** Lovable prompt is always written in Claude (claude.ai) before spending a credit. Never spend a credit on a vague prompt.

---

### ADR-006: Antigravity for boilerplate, Claude Code for architecture
**Decision:** Split code generation between Claude Code (complex, cross-file, architectural) and Antigravity (scoped, single-function, boilerplate).
**Reason:** Claude Code understands the full codebase but has token limits on the $20 plan. Antigravity is generous for code generation. Using Antigravity for repetitive tasks preserves Claude Code's context budget for hard problems.
**Hard rule:** Never run both on the same file simultaneously. Always note in CONTEXT.md which files are "owned" by which agent at any moment.

---

### ADR-007: D3.js force-directed graph for country knowledge map
**Decision:** The results page shows a D3.js force-directed network graph of countries as a core feature, not a nice-to-have.
**Reason:** This is the visual differentiator. No immigration tool shows data this way. Obsidian-style node graphs are familiar to the target demographic (technical students). The graph shows country similarity clusters that ranked lists cannot convey.
**Implementation:** D3.js force simulation. Nodes = countries (size = total score, color = tier). Edges = similarity score between country pairs for the user's specific profile. Runs entirely in the browser — no backend call needed after /rank returns graph_data.
**Revisit if:** D3.js inside Lovable/Next.js proves difficult to integrate. Fallback: vis.js or a React-specific force graph library.

---

### ADR-008: Upstash Redis instead of self-hosted Redis
**Decision:** Use Upstash Redis free tier for caching and pub/sub.
**Reason:** Free tier (10k commands/day) is sufficient for MVP. No server to manage. HTTP-based access works from anywhere — no need to keep a Redis server running on a local machine.
**Revisit if:** 10k commands/day is exceeded (only happens with significant real traffic — a good problem to have).

---

### ADR-009: Resend instead of SendGrid for email
**Decision:** Use Resend for transactional email alerts.
**Reason:** Resend free tier is 3,000 emails/month. Cleaner API than SendGrid. Better developer experience. Free forever at MVP scale.
**Revisit if:** 3,000 emails/month is exceeded.

### ADR-010: Gemini API directly instead of OpenRouter
Decision: Use Google AI Studio API key directly with Gemini 2.5 Flash.
Reason: Student account has access to Gemini 2.5 Flash free. Better 
model than any free OpenRouter option. One less service to manage.
Revisit if: API key gets rate-limited heavily in production.

---

## PRODUCT DECISIONS

---

### PDR-001: All four pillars in MVP
**Decision:** Real-time data, proactive alerts, personalized ranking, and outcome data are all in the MVP — not post-MVP.
**Reason:** Any one pillar alone is replicable with a ChatGPT prompt. The combination is what makes Exit Plan defensible. Launching with only the ranker is launching a worse version of a Google search.
**Scope control:** Each pillar launches at reduced depth (e.g. 10 countries not 30, email alerts not push) but all four are present.

---

### PDR-002: No login required for first result
**Decision:** Users get their ranked country list without creating an account.
**Reason:** Removes friction at the highest-drop-off moment. The result is the hook. Once they see it, they create an account to save it and get alerts.
**Implementation:** /rank is a public endpoint. The shareable URL encodes the profile hash. Login is prompted when the user tries to save a profile or enable alerts.

---

### PDR-003: Design is bright and optimistic, not dark and "strategic"
**Decision:** Palette is electric indigo + sunrise orange on warm off-white. Not a dark dashboard.
**Reason:** The user is someone making one of the most hopeful decisions of their life — choosing a country to build their future in. The product should feel like possibility, not bureaucracy.
**Typography:** Plus Jakarta Sans (display) + Inter (body). Both free on Google Fonts.

---

### PDR-004: Outcome data seeded manually at launch
**Decision:** The 20-30 launch outcome stories are manually collected and entered, not user-submitted.
**Reason:** Cold start problem. A community feature with zero data is worse than no community feature. Manual seeding from Reddit, forums, and personal network gives enough signal to make the feature feel real.
**Sources:** r/ImmigrationToGermany, r/ukvisa, r/ImmigrationCanada, personal contacts.

---

## DECISION LOG TEMPLATE

When you make a new decision, add it here:

```
### ADR-XXX / PDR-XXX: [Title]
**Decision:** What was decided.
**Reason:** Why. What alternatives were considered and rejected.
**Tradeoff:** What you gave up.
**Revisit if:** The condition under which this decision should be reconsidered.
```