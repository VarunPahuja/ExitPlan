# Exit Plan — Frontend

TanStack Start (React + Vite) frontend for Exit Plan.
Built with Lovable, cleaned for production.

## Setup

```bash
cp .env.example .env.local
# fill in VITE_BACKEND_URL (and Supabase keys when wiring auth)

bun install
bun dev
```

## Stack

- TanStack Start (SSR-capable Vite + TanStack Router)
- React 19, Tailwind CSS v4, shadcn/ui components
- dnd-kit for drag-and-drop priority ordering
- D3.js (CDN) for the knowledge graph on the results page
- Deploys to Cloudflare Workers via `wrangler`

## Env vars

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_BACKEND_URL` | Yes | FastAPI backend base URL (no trailing slash) |
| `VITE_SUPABASE_URL` | When auth is wired | Supabase project URL |
| `VITE_SUPABASE_ANON_KEY` | When auth is wired | Supabase anon/public key |

**Note:** This project uses Vite, not Next.js. Client-side env vars must be prefixed
with `VITE_` and accessed via `import.meta.env.VITE_*`, not `process.env.NEXT_PUBLIC_*`.

## Routes

| Route | Description |
|-------|-------------|
| `/` | Landing page |
| `/profile` | 5-step profile builder — POSTs to `/rank/` on submit |
| `/results` | Ranked country cards + D3 knowledge graph |
| `/country/:code` | Country detail + AI chat panel (chat is mocked) |
| `/signin` | Google OAuth sign in (auth mocked — wire to Supabase) |
| `/dashboard` | Saved profiles + alert feed (placeholder data) |

## Deploying

```bash
bun run build
wrangler deploy
```
