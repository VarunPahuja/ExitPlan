# EXIT PLAN — PROMPTS.md
> Ready-to-paste prompts for every agent and every major task.
> Pick the prompt, fill any [BRACKETS], paste into the agent. Never go in blind.
> Last updated: 2026-05-23

---

## SECTION 1: CLAUDE CODE SESSION STARTER

Paste this at the start of every Claude Code terminal session:

```
Read CONTEXT.md in the project root before doing anything else.
Current task: [PASTE THE TASK FROM CONTEXT.md SECTION 5]
Do not modify files outside the scope of this task.
Stack: FastAPI, Python, Supabase (Postgres + pgvector + Auth), sentence-transformers (local), Gemini 2.5 Flash via Google AI Studio.
All env vars are in backend/.env — read them via python-dotenv, never hardcode.
After completing, tell me exactly what to update in CONTEXT.md sections 2 and 3.
```

---

## SECTION 2: REMAINING BACKEND PROMPTS

---

### Backend Task 1: /alerts endpoint — full CRUD

```
Read CONTEXT.md and backend/routers/alerts.py before starting.
Stack: FastAPI, Supabase Python client, Pydantic.

Build the full /alerts endpoint in backend/routers/alerts.py. Replace the existing stub.

The user_alerts table schema is:
  id (uuid pk), user_id (uuid fk users), country_id (uuid fk countries),
  alert_type (text), message (text), plain_english (text),
  sent_at (timestamptz), read_at (timestamptz), source_url (text)

Implement these routes (all require auth via get_current_user from services/auth.py):

GET /alerts/
  Returns all alerts for the current user, ordered by sent_at desc.
  Response: { "alerts": [AlertResponse, ...] }

POST /alerts/subscribe
  Body: { "country_code": "DE" }
  Adds the country to the user's saved_countries array in the users table.
  Upserts — no error if already subscribed.
  Response: { "subscribed": true, "country_code": "DE" }

DELETE /alerts/unsubscribe/{country_code}
  Removes country from user's saved_countries array.
  Response: { "unsubscribed": true, "country_code": "DE" }

PUT /alerts/preferences
  Body: { "email_alerts": true, "alert_types": ["policy_change", "visa_quota"] }
  Updates alert preferences stored as jsonb in users.weights column (add a preferences jsonb column to users table if it doesn't exist — write the ALTER TABLE migration as a comment at the top of the file).
  Response: updated preferences object

AlertResponse Pydantic model:
  id: str, country_code: str, country_name: str, alert_type: str,
  message: str, plain_english: str, sent_at: datetime, read_at: Optional[datetime],
  source_url: str

Use the existing Supabase client from db/supabase.py. Do not create a new client.
After completing, tell me what to update in CONTEXT.md.
```

---

### Backend Task 2: Change detector

```
Read CONTEXT.md and backend/services/change_detector.py before starting.
Stack: FastAPI, Supabase, BeautifulSoup, difflib.

Build the change detector in backend/services/change_detector.py.

The function signature:
  async def detect_changes(country_code: str) -> list[PolicyChange]

Logic:
1. Run the appropriate scraper for the given country_code (import from backend/scrapers/runner.py).
   The scraper returns a list of dicts with keys: content, source_url, visa_type.
2. For each scraped document, retrieve the most recent stored chunk for the same source_url
   from the policy_chunks table in Supabase.
3. Use difflib.SequenceMatcher to compare old content vs new content.
   Treat anything below 0.85 similarity ratio as a meaningful change.
4. For each meaningful change:
   - Write a row to the policy_changes table:
     country_id (look up from countries table by code), visa_type, change_summary,
     detected_at (now()), old_value (old content truncated to 500 chars),
     new_value (new content truncated to 500 chars)
   - Also call embed_and_store() from services/embeddings.py to update the chunk.
5. Return a list of PolicyChange objects (Pydantic model: country_code, visa_type,
   change_summary, detected_at, source_url).

Also write a standalone async main() at the bottom for manual CLI use:
  python -m backend.services.change_detector --country DE

The policy_changes table schema:
  id (uuid pk), country_id (uuid fk countries), visa_type (text),
  change_summary (text), detected_at (timestamptz), old_value (text), new_value (text)

Do not implement scheduling — that is Celery's job. This function just runs once when called.
After completing, tell me what to update in CONTEXT.md.
```

---

### Backend Task 3: Resend email alerts

```
Read CONTEXT.md and backend/services/alert_engine.py before starting.
Stack: FastAPI, Resend Python SDK, Supabase.
Env var: RESEND_API_KEY in backend/.env

Build the alert engine in backend/services/alert_engine.py.

The function signature:
  async def send_policy_alert(change: PolicyChange) -> None

Logic:
1. Query the users table in Supabase for all users whose saved_countries array
   contains the country_code from the PolicyChange.
2. For each user with email_alerts enabled in their preferences:
   - Call Resend to send a transactional email.
   - Use resend.Emails.send() with:
       from: "Exit Plan <alerts@exitplan.app>"
       to: user.email
       subject: f"Policy change in {country_name} that affects you"
       html: (see template below)

Email HTML template (write as a Python f-string):
- Heading: "Immigration update: {country_name}"
- Body: The change.change_summary in plain English
- Key detail: "What this means for you: {change.plain_english_summary}"
  (generate this with a Gemini call — prompt: "In one plain sentence for an Indian student,
   explain what this immigration policy change means: {change.change_summary}")
- Source link: "Read the official update →" linking to change.source_url
- Footer: "You're receiving this because you're watching {country_name} on Exit Plan.
           Unsubscribe from country alerts."
- Design: simple, minimal HTML — no complex CSS. White background, #5B4FE8 heading color.

Also export:
  async def notify_all_affected_users(changes: list[PolicyChange]) -> None
  (loops over changes and calls send_policy_alert for each)

Use RESEND_API_KEY from os.environ. Raise a clear error if the key is missing.
After completing, tell me what to update in CONTEXT.md.
```

---

## SECTION 3: LOVABLE PROMPTS

> Always paste these directly into Lovable. Do not paraphrase.
> These reference exact field names and enum values from API_CONTRACT.md.

---

### Lovable Prompt 1: Results page — real data from localStorage

```
Update the Exit Plan results page at /results.

CRITICAL: The page currently shows hardcoded data. Replace all hardcoded data with real data.

DATA SOURCE: On page load, read the JSON object stored in localStorage under the key
"exitplan_results". This object matches the /rank API response exactly:

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
      "visa_types": ["Critical Skills Employment Permit", "General Employment Permit"],
      "pr_timeline_years": 2,
      "last_updated": "2026-05-22"
    }
  ],
  "graph_data": { "nodes": [...], "edges": [...] },
  "profile_hash": "abc123",
  "shareable_url": "http://localhost:3000/results/abc123"
}

The profile builder already stores this data in localStorage after calling POST /rank/.
If localStorage is empty, redirect to /profile.

LAYOUT: Two columns. Left 40%: ranked country cards. Right 60%: div with id="knowledge-graph"
(leave this as a placeholder — it will be wired to D3.js separately).

LEFT COLUMN — ranked country cards:
Render one card per entry in ranked_countries array, in order.

Each card shows:
- Country flag emoji + country_name (large, bold)
- total_score as a large number that animates count-up from 0 to the final value
  over 1 second on page load (use a simple requestAnimationFrame loop)
- 5 horizontal factor score bars, one per key in scores object:
  Label: "Job Market", "PR Timeline", "Visa Ease", "Salary vs Cost", "Language"
  Bar fill width = score / 100 as a percentage
  Bar color: green (#22c55e) if score > 75, amber (#f59e0b) if 50-75, red (#ef4444) if < 50
- verdict text in italic below the bars
- tier badge: "great" = indigo badge, "good" = green badge, "moderate" = amber, "low" = red
- Two small buttons: "Ask AI" (links to /ask?country={country_code}) and "Learn more"

The rank 1 card gets: elevated shadow, electric indigo (#5B4FE8) left border,
"Best match" badge in sunrise orange (#FF6B35) at top right.

ABOVE THE CARDS:
- A subtitle line reading the profile from localStorage: show nationality, field, degree_level
  (e.g., "Results for IN · computer_science · masters")
- "Adjust priorities" link that goes back to /profile (step 5)

TOP RIGHT:
- Share button. On click: copy the shareable_url from localStorage data to clipboard.
  Show a "Copied!" toast for 2 seconds.

LOADING STATE: If localStorage has the key but the data hasn't loaded yet, show skeleton
cards (grey rectangles with a shimmer animation) in place of the real cards.

MOBILE: Stack columns vertically. Knowledge graph div goes below cards on mobile.

Design system: electric indigo (#5B4FE8) primary, sunrise orange (#FF6B35) CTAs,
warm off-white (#FAFAF8) background, Plus Jakarta Sans headings, Inter body.
```

---

### Lovable Prompt 2: Knowledge graph — D3.js force simulation

```
Add a real D3.js force-directed knowledge graph to the Exit Plan results page.

The placeholder div with id="knowledge-graph" already exists in the right column.
Replace the placeholder content with a working D3.js force simulation.

DATA SOURCE: Read from localStorage key "exitplan_results". Use graph_data from the response:
  graph_data.nodes — array of { id, label, total_score, tier }
  graph_data.edges — array of { source, target, similarity, reason }

D3.js IMPLEMENTATION (write as a useEffect hook that runs after the component mounts):

1. Import D3 from "d3" (install as a dependency if not already present).

2. Create an SVG inside the #knowledge-graph div, full width and height of the container.

3. Force simulation:
   - forceLink: use edges array, distance = 120
   - forceManyBody: strength = -300
   - forceCenter: center of the SVG
   - forceCollide: radius = 40 to prevent overlap

4. EDGES: Draw lines between nodes. Stroke opacity = similarity value (0 to 1).
   Stroke color = #cbd5e1 (slate-300). Stroke width = 1.5px.
   On hover, show a tooltip with the reason string.

5. NODES: Draw circles. Radius = 20 + (total_score / 10).
   Color by tier:
     "great" → #5B4FE8 (indigo)
     "good"  → #22c55e (green)
     "moderate" → #f59e0b (amber)
     "low"   → #ef4444 (red)
   Inside each node: country code text (2 letters, white, 12px bold).
   Below each node: country label text (country name, 11px, slate-600).

6. INTERACTIONS:
   - Drag nodes to reposition (use d3.drag).
   - On click of a node: scroll the left-column card for that country into view
     and add a temporary highlight ring (2px indigo border) for 1.5 seconds.
   - On hover of a node: show a tooltip with country_name and total_score.

7. TOOLTIP: A floating div positioned near the cursor. Style: white background,
   rounded corners, small shadow, 12px text.

8. On window resize, re-render the SVG to fit the new container size.

If graph_data is missing from localStorage or has no nodes, show a message:
"Graph unavailable — run a search first."

Design: The graph background should be warm off-white (#FAFAF8), matching the page.
No axis, no legend needed — nodes are self-labelled.
```

---

### Lovable Prompt 3: Sign in page — Google OAuth via Supabase

```
Build the Exit Plan sign in page at /signin.

PURPOSE: Users sign in with Google to save their profile and get immigration alerts.
Auth provider: Supabase Auth with Google OAuth.

LAYOUT: Centred card on a warm off-white (#FAFAF8) background.

CARD CONTENT (vertical stack, generous padding):
1. Exit Plan logo or wordmark at top
2. Headline: "Save your results. Get alerts when policies change."
3. Subheadline (smaller, slate-500): "Sign in with Google — no password needed."
4. Google sign-in button:
   - Full width, white background, thin border, Google logo on left, text "Continue with Google"
   - On click: call supabase.auth.signInWithOAuth({ provider: 'google' })
   - Supabase handles the redirect to Google and the callback automatically
5. Below the button, small text: "By signing in you agree to our terms.
   Exit Plan never posts anything to your Google account."
6. Below that, grey separator, then: "Just exploring? " with a link "View results without saving →"
   that goes back to /results.

AFTER SIGN IN:
- Supabase redirects back to the app. On the callback, check for a session.
- If session exists: call PUT /profile/ with the profile data from localStorage "exitplan_results"
  to save the user's profile. Then redirect to /results.
- Use supabase.auth.onAuthStateChange() to listen for the session.

ERROR STATE:
- If OAuth fails, show a red banner: "Sign in failed — please try again."
  with a retry button.

LOADING STATE:
- While waiting for Google redirect to complete, show a spinner and "Signing you in..."

The supabase client is already configured in the project. Use the existing instance.
Redirect URL for OAuth should be: {FRONTEND_URL}/auth/callback (set in Supabase dashboard).

Design system: electric indigo (#5B4FE8) primary, warm off-white (#FAFAF8) background,
Plus Jakarta Sans headings, Inter body. Mobile responsive — card should be full-width on mobile.
```

---

## SECTION 4: ANTIGRAVITY USAGE GUIDE

Antigravity is for scoped, single-file, boilerplate tasks. Use it to preserve Claude Code's context budget.

### Template (paste this every Antigravity session):
```
Project: Exit Plan (FastAPI backend, immigration ranking platform for Indian students)
Stack: FastAPI, Python, Supabase (Postgres + pgvector), sentence-transformers, Gemini API
File: backend/services/[FILENAME].py
Do NOT touch any other files. Do not add imports from files that don't exist.

Task: Write [SPECIFIC FUNCTION NAME] with this exact signature:
[PASTE FUNCTION SIGNATURE]

It should: [DESCRIBE WHAT IT DOES IN 2-3 SENTENCES]
Input: [DESCRIBE INPUT TYPE AND SHAPE]
Output: [DESCRIBE RETURN TYPE AND SHAPE]
Edge cases to handle: [LIST SPECIFIC EDGE CASES]
```

### Good Antigravity tasks:
- Writing `is_relevant_chunk(text: str) -> bool` with specific filter patterns
- Writing a Pydantic model for a new response shape
- Writing a helper that formats a prompt string for Gemini
- Writing a single SQL query function against Supabase

### Bad Antigravity tasks (use Claude Code instead):
- Anything touching more than one service file
- New endpoint registration (requires changes to main.py + router file)
- Schema changes (require migration file + Supabase dashboard)
- Debugging failures that require reading logs or tracing execution

---

## SECTION 5: HOW TO USE THIS CLAUDE (claude.ai)

This conversation is for strategy, prompts, and decisions — not for running code.

### Use claude.ai for:
- Reviewing and refining Lovable prompts before spending a credit
- Deciding between two architectural approaches (read DECISIONS.md first)
- Writing the exact prompt for Claude Code when the task is complex
- Updating CONTEXT.md, DECISIONS.md, API_CONTRACT.md, PROMPTS.md after a session
- Debugging strategy when Claude Code is stuck (describe the error, paste relevant code)

### How to start a productive session here:
1. Paste the relevant sections of CONTEXT.md (sections 2–5 are usually enough)
2. Describe what you just completed or what you're about to start
3. Ask one focused question or request one deliverable

### What NOT to do:
- Don't paste full file contents unless the question is specifically about that file
- Don't ask "what should I build next?" — the answer is always CONTEXT.md section 5
- Don't ask claude.ai to write code that will be pasted directly into the backend — use Claude Code for that

### Workflow for a new Lovable screen:
1. Tell this Claude: "I want to build [SCREEN NAME]. Here's the current API contract for relevant endpoints: [PASTE FROM API_CONTRACT.md]"
2. This Claude refines the prompt if needed, then hands you the final version
3. You paste the prompt from PROMPTS.md Section 3 (already pre-written above) into Lovable
4. After Lovable responds, come back here and update CONTEXT.md section 2
