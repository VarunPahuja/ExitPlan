# EXIT PLAN — API_CONTRACT.md
> Locked in Week 1. Neither frontend nor backend changes this unilaterally.
> If a change is needed: update this file first, notify both sides, then implement.
> Last updated: Week 0 (pre-build)

---

## Base URL

Development: `http://localhost:8000`
Production: `[ ADD AFTER DEPLOY ]`

All endpoints return JSON unless noted. All requests/responses use snake_case.

---

## Authentication

All protected endpoints require:
```
Authorization: Bearer <supabase_jwt_token>
```
Public endpoints (no auth required): `/rank`, `/ask`, `/outcomes GET`

---

## ENDPOINTS

---

### POST /rank
**Purpose:** Takes a user profile + declared priority weights, returns ranked country list + graph data.
**Auth:** Public (no login required for first result)

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

**Notes on weights:**
- Must sum to 1.0 (backend validates and normalises if not)
- Weights are 100% user-declared — no backend defaults override them
- Frontend sends whatever the user set in the drag-priority UI

**Response:**
```json
{
  "ranked_countries": [
    {
      "rank": 1,
      "country_code": "DE",
      "country_name": "Germany",
      "total_score": 84,
      "scores": {
        "job_market": 88,
        "pr_timeline": 79,
        "visa_ease": 82,
        "salary_cost_ratio": 91,
        "language": 61
      },
      "verdict": "Germany is your strongest match — high STEM demand and a clear PR pathway within 5 years.",
      "visa_types": ["Job Seeker Visa", "EU Blue Card", "Skilled Worker Visa"],
      "pr_timeline_years": 5,
      "last_updated": "2025-01-15T10:00:00Z"
    }
  ],
  "graph_data": {
    "nodes": [
      {
        "id": "DE",
        "label": "Germany",
        "total_score": 84,
        "tier": "great"
      }
    ],
    "edges": [
      {
        "source": "DE",
        "target": "NL",
        "similarity": 0.82,
        "reason": "Similar EU Blue Card pathway + STEM demand"
      }
    ]
  },
  "profile_hash": "abc123",
  "shareable_url": "https://exitplan.app/results/abc123"
}
```

**Tier values:** `"great"` (80-100), `"good"` (60-79), `"moderate"` (40-59), `"low"` (0-39)

---

### POST /ask
**Purpose:** RAG query — user asks a freeform question about a country/visa for their situation.
**Auth:** Public
**Response type:** Server-Sent Events (streaming)

**Request body:**
```json
{
  "query": "Can I switch from a student visa to a work visa in Germany without leaving?",
  "country_code": "DE",
  "user_profile": {
    "nationality": "IN",
    "field": "computer_science",
    "degree_level": "masters",
    "current_status": "post_study"
  }
}
```

**Response (SSE stream):**
```
data: {"chunk": "Yes, in Germany you can", "done": false}
data: {"chunk": " apply for a job seeker visa", "done": false}
data: {"chunk": " without leaving the country", "done": false}
data: {"chunk": "", "done": true, "citations": [{"source": "BAMF official portal", "url": "https://bamf.de/...", "date": "2024-11-01"}]}
```

**Frontend handles:** Appending chunks as they arrive. Showing citations after `done: true`.

---

### GET /profile
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
  "created_at": "2025-01-01T00:00:00Z"
}
```

---

### PUT /profile
**Purpose:** Create or update the logged-in user's profile.
**Auth:** Required

**Request body:** Same shape as GET /profile response (minus id, email, created_at)

**Response:** Updated profile object

---

### GET /alerts
**Purpose:** Get alert history for the logged-in user.
**Auth:** Required

**Response:**
```json
{
  "alerts": [
    {
      "id": "uuid",
      "country_code": "GB",
      "country_name": "United Kingdom",
      "alert_type": "policy_change",
      "message": "UK changed Graduate Route salary threshold from £26,200 to £38,700. This affects your saved Plan B.",
      "plain_english": "The minimum salary you need to stay in the UK after graduating just went up significantly. If you were planning on the Graduate Route, your job search target has changed.",
      "sent_at": "2025-01-10T09:00:00Z",
      "read_at": null,
      "source_url": "https://gov.uk/..."
    }
  ]
}
```

---

### PUT /alerts/preferences
**Purpose:** Update alert preferences.
**Auth:** Required

**Request body:**
```json
{
  "email_alerts": true,
  "watched_countries": ["DE", "CA", "GB"],
  "alert_types": ["policy_change", "visa_quota", "salary_threshold"]
}
```

---

### GET /outcomes
**Purpose:** Get anonymized community outcome stories.
**Auth:** Public

**Query params:** `?country=DE&field=computer_science&degree=masters`

**Response:**
```json
{
  "outcomes": [
    {
      "id": "uuid",
      "nationality": "IN",
      "field": "Computer Science",
      "degree_level": "Masters",
      "destination_country": "DE",
      "visa_type": "Job Seeker Visa",
      "months_to_job": 4,
      "summary": "Got a backend engineering role at a Berlin startup. Needed B1 German for some roles but found English-only positions.",
      "year": 2024,
      "verified": true
    }
  ]
}
```

### POST /outcomes
**Purpose:** Submit a community outcome story.
**Auth:** Required

---

## ENUM VALUES

Use these exact strings — frontend and backend must match.

```
current_status:   "student" | "post_study" | "employed"
degree_level:     "bachelors" | "masters" | "phd" | "diploma"
savings_range:    "0_5L" | "5_15L" | "15L_plus"
career_goal:      "long_term_pr" | "work_experience" | "return_home"
country_codes:    "GB" | "CA" | "DE" | "AU" | "NL" | "PT" | "IE" | "AE" | "NZ" | "SG"
alert_types:      "policy_change" | "visa_quota" | "salary_threshold" | "pr_requirement"
tier:             "great" | "good" | "moderate" | "low"
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

---

## CHANGE LOG

| Date | Change | Who approved |
|------|--------|-------------|
| Week 0 | Initial contract defined | — |