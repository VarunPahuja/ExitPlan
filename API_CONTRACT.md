# EXIT PLAN — API_CONTRACT.md
> The contract between frontend and backend. Neither side changes this unilaterally.
> To change: update this file first, notify both sides, then implement.
> Last updated: 2026-05-23

---

## Base URL

```
Development:  http://localhost:8000
Production:   [add after deploy]
```

All endpoints return JSON unless noted. All field names use snake_case.

---

## Authentication

Protected endpoints require:
```
Authorization: Bearer <supabase_jwt_token>
```

| Endpoint | Auth required |
|----------|---------------|
| GET /health | No |
| POST /rank/ | No |
| GET /rank/preview | No |
| POST /ask/ | No |
| GET /profile/ | Yes |
| PUT /profile/ | Yes |
| GET /alerts/ | Yes |

---

## ENDPOINTS

---

### GET /health
**Purpose:** Confirm the API and database are reachable.

**Response:**
```json
{
  "status": "ok",
  "version": "0.1.0",
  "db": true
}
```

---

### POST /rank/
**Purpose:** Takes a user profile + declared priority weights, returns all 10 countries ranked.
**Auth:** Public

**Request body:**
```json
{
  "nationality": "IN",
  "current_status": "post_study",
  "field": "computer_science",
  "degree_level": "masters",
  "savings_range": "5_15L",
  "career_goal": "long_term_pr",
  "weights": {
    "job_market": 0.35,
    "pr_timeline": 0.30,
    "visa_ease": 0.15,
    "salary_cost_ratio": 0.12,
    "language": 0.08
  }
}
```

**Weights rules:**
- Must sum to 1.0. Backend validates and normalises if they don't.
- Weights are 100% user-declared. Backend never substitutes defaults.
- Frontend sends whatever the user set in the drag-priority UI on step 5.

**Response:**
```json
{
  "ranked_countries": [
    {
      "rank": 1,
      "country_code": "IE",
      "country_name": "Ireland",
      "total_score": 87.2,
      "scores": {
        "job_market": 92,
        "pr_timeline": 90,
        "visa_ease": 85,
        "salary_cost_ratio": 58,
        "language": 100
      },
      "verdict": "Strong job market and fast PR pathway make Ireland your top match.",
      "tier": "great",
      "visa_types": ["Critical Skills Employment Permit", "General Employment Permit", "Stamp 4"],
      "pr_timeline_years": 2,
      "last_updated": "2026-05-22"
    }
  ],
  "graph_data": {
    "nodes": [
      {
        "id": "IE",
        "label": "Ireland",
        "total_score": 87.2,
        "tier": "great"
      }
    ],
    "edges": [
      {
        "source": "IE",
        "target": "DE",
        "similarity": 0.96,
        "reason": "Similar job market profiles"
      }
    ]
  },
  "profile_hash": "abc123",
  "shareable_url": "http://localhost:3000/results/abc123"
}
```

**Tier thresholds:** `"great"` (80–100) | `"good"` (60–79) | `"moderate"` (40–59) | `"low"` (0–39)

---

### GET /rank/preview
**Purpose:** Returns a ranking with equal weights (0.20 each). No profile required.
**Auth:** Public
**Response:** Same shape as POST /rank/ response.

---

### POST /ask/
**Purpose:** RAG query — user asks a freeform question about a country/visa. Streams the answer via SSE.
**Auth:** Public
**Response type:** Server-Sent Events (text/event-stream)

**Request body:**
```json
{
  "query": "Can I work part-time on a student visa in Germany?",
  "country_code": "DE",
  "user_profile": {
    "nationality": "IN",
    "field": "computer_science"
  }
}
```

**Response — SSE stream:**
```
data: {"chunk": "Yes, you can work...", "done": false}
data: {"chunk": " up to 120 full days or 240 half days per year", "done": false}
data: {"chunk": " on a German student visa.", "done": false}
data: {"chunk": "", "done": true, "citations": [{"source_url": "https://bamf.de/...", "visa_type": "Student Visa"}]}
```

**Frontend behaviour:**
- Append each `chunk` to the displayed text as it arrives.
- When `done: true`, render the citations list below the answer.
- Show a typing indicator while streaming.

---

### GET /profile/
**Purpose:** Get the logged-in user's saved profile.
**Auth:** Required

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "nationality": "IN",
  "current_status": "post_study",
  "field": "computer_science",
  "degree_level": "masters",
  "savings_range": "5_15L",
  "career_goal": "long_term_pr",
  "weights": {
    "job_market": 0.35,
    "pr_timeline": 0.30,
    "visa_ease": 0.15,
    "salary_cost_ratio": 0.12,
    "language": 0.08
  },
  "saved_countries": ["DE", "CA", "NL"],
  "created_at": "2026-01-01T00:00:00Z"
}
```

**Error if not found:** 404 with `PROFILE_NOT_FOUND`

---

### PUT /profile/
**Purpose:** Create or update the logged-in user's profile. Email is taken from the JWT — do not send it in the body.
**Auth:** Required

**Request body:**
```json
{
  "nationality": "IN",
  "current_status": "post_study",
  "field": "computer_science",
  "degree_level": "masters",
  "savings_range": "5_15L",
  "career_goal": "long_term_pr",
  "weights": {
    "job_market": 0.35,
    "pr_timeline": 0.30,
    "visa_ease": 0.15,
    "salary_cost_ratio": 0.12,
    "language": 0.08
  },
  "saved_countries": ["DE", "CA", "NL"]
}
```

**Response:** Updated profile object (same shape as GET /profile/ response).

---

### GET /alerts/
**Purpose:** Get alert history for the logged-in user.
**Auth:** Required
**Status:** STUB — returns empty list. Full implementation pending.

**Response (target shape):**
```json
{
  "alerts": [
    {
      "id": "uuid",
      "country_code": "GB",
      "country_name": "United Kingdom",
      "alert_type": "policy_change",
      "message": "UK changed Graduate Route salary threshold from £26,200 to £38,700.",
      "plain_english": "The minimum salary you need to stay in the UK after graduating just went up significantly.",
      "sent_at": "2026-01-10T09:00:00Z",
      "read_at": null,
      "source_url": "https://gov.uk/..."
    }
  ]
}
```

---

## ENUM VALUES

Frontend and backend must use these exact strings. No variations.

```
current_status:   "student" | "post_study" | "employed"

degree_level:     "bachelors" | "masters" | "phd" | "diploma"

savings_range:    "0_5L" | "5_15L" | "15L_plus"

career_goal:      "long_term_pr" | "work_experience" | "return_home"

field:            "computer_science" | "data_science" | "engineering" |
                  "business" | "medicine" | "law" | "design" | "finance" | "other"

tier:             "great" | "good" | "moderate" | "low"

country_codes:    "GB" | "CA" | "DE" | "AU" | "NL" | "PT" | "IE" | "AE" | "NZ" | "SG"

alert_types:      "policy_change" | "visa_quota" | "salary_threshold" | "pr_requirement"
```

---

## ERROR FORMAT

All errors return:
```json
{
  "error": {
    "code": "PROFILE_NOT_FOUND",
    "message": "No profile found for this user.",
    "status": 404
  }
}
```

Common error codes:
- `PROFILE_NOT_FOUND` — 404, GET /profile/ when user has no saved profile
- `UNAUTHORIZED` — 401, missing or invalid Bearer token
- `VALIDATION_ERROR` — 422, request body fails Pydantic validation
- `WEIGHTS_DO_NOT_SUM` — 422, weights sum is too far from 1.0 to normalise
- `COUNTRY_NOT_FOUND` — 404, unknown country_code in /ask request

---

## CHANGE LOG

| Date | Change | Who |
|------|--------|-----|
| 2026-05-23 | Full rewrite to reflect actual built state; added /rank/preview, field enum, SSE citations format | Varun |
| Week 1 | Initial contract defined | Varun |
