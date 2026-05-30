# Exit Plan

**Find the best country for your career and PR — personalized to you.**

Exit Plan is an AI-powered platform that ranks 10 countries based on your field, nationality, finances, and career goal. Not Reddit. Not a consultant. Real-time policy data, personalized scores, and AI answers grounded in official government sources.

## What it does

- **Personalized country ranking** — input your profile, get 10 countries ranked with scores across job market, PR timeline, visa ease, salary vs cost, and language. Weights are yours to set.

- **AI immigration chat** — ask anything about visas, PR timelines, salary thresholds. Answers stream in real time, grounded in scraped government policy documents with source citations.

- **Policy change alerts** — save your profile, get emailed when a rule changes that affects your countries.

- **Community outcome stories** — anonymized real journeys from Indian graduates who moved to these countries.

## Countries covered

United Kingdom · Canada · Germany · Australia · Netherlands · Portugal · Ireland · UAE · New Zealand · Singapore

## Tech stack

| Layer | Stack |
|-------|-------|
| Frontend | TanStack Start, React, Vite, TailwindCSS, D3.js |
| Backend | FastAPI, Python |
| Database | Supabase (Postgres + pgvector) |
| AI | Gemini 2.5 Flash, sentence-transformers |
| RAG | Hybrid vector + keyword search over 400+ policy chunks |
| Auth | Supabase Google OAuth |
| Email | Resend |

## Running locally

### Backend
```bash
cd backend
cp .env.example .env        # fill in your keys
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend
```bash
cd frontend
cp .env.example .env.local  # fill in your keys
npm install
npm run dev
```

Open http://localhost:5173

## Environment variables

**Backend** (`backend/.env`):
```
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_KEY=
GEMINI_API_KEY=
RESEND_API_KEY=
```

**Frontend** (`frontend/.env.local`):
```
VITE_BACKEND_URL=http://localhost:8000
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
```

## Status

Beta — built for Indian international students and graduates. Data based on May 2026 research. Always verify immigration rules with official sources before making decisions.

---
Built with FastAPI, Supabase, Gemini, and a lot of immigration research.
