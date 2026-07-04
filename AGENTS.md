# SportShield AI — Agent Context

## Overview

This is a monorepo for a sports media digital-asset protection tool. It has a **FastAPI-based Python backend** and a **Next.js + React-based web frontend**, connected via a REST API.

- **Backend:** `backend/` — FastAPI, ChromaDB, CLIP, pHash, Groq, Supabase.
- **Frontend:** `frontend/` — Next.js 16 (App Router), React 19, Tailwind CSS v4, Supabase Auth.

## Architecture

```
sportshield/
├── backend/           -- FastAPI entry: main.py
│   ├── routers/       -- upload, scan, explain, report, dashboard
│   └── services/        -- fingerprint, web_scanner, rag_engine, database, report_generator
└── frontend/          -- Next.js entry: src/app/
    ├── src/app/        -- page.tsx (landing), login/page.tsx, dashboard/page.tsx
    ├── src/components/
    ├── src/utils/      -- api.ts, supabase/ (SSR client)
    └── middleware.ts   -- Route protection
```

## Development Commands

**Backend (inside `backend/`):**
```bash
# Setup
python -m venv venv
. venv/bin/activate         # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run
uvicorn main:app --reload --port 8000
```

**Frontend (inside `frontend/`):**
```bash
# Use pnpm (lockfile exists)
pnpm install
pnpm dev        # localhost:3000
pnpm build      # Production build
pnpm lint       # ESLint
```

> **Note:** No test suite is currently configured. Testing is done manually.

## Navigating the Codebase

### Frontend
- **Next.js 16 / App Router:** All routes live in `frontend/src/app/`. Server Components are the default; mark interactive components with `"use client"`.
- **Auth:** Uses Supabase Auth (SSR). The server client is `createClient(cookies())` from `@/utils/supabase/server`.The client client is `createClient()` from `./frontend/src/utils/supabase/client`.
- **API Calls:** `frontend/src/utils/api.ts` (server-side fetcher with auth injection).
- **Styling:** Tailwind CSS v4. Dark theme with design tokens like Coral (`#FF6B6B`) and dark backgrounds (`#111415`).
- **Important convention:** Use default exports for pages and named exports for components.

### Backend
- **Entry Point:** `backend/main.py`.
- **Routers:** `backend/routers/` contains the main API logic.
- **Services:** `backend/services/` contains core domain logic (fingerprinting, scanning, RAG).
- **Lifespan:** The FastAPI app lifespan handles startup logic: loading the CLIP model, initializing the RAG knowledge base, and connecting to Supabase.
- **Static Files:** Uploaded assets are served from the `/uploads` path.

## Environment Setup

1. **Copy and fill environment variables:**
   - Backend: `cp backend/.env.example backend/.env`
   - Frontend: `cp frontend/.env.local.example frontend/.env.local`
2. **Required variables:** See README.md for a full list, including Groq, Google Custom Search, and Supabase keys.

## Important Constraints

- **Next.js 16:** APIs and conventions may differ from older versions.
- **`window` / `document` usage:** Do not use in Server Components. Only use in Client Components (`"use client"` or `use client` directive).
- **Server-side data fetching:** Use `async/await` directly in Server Components. Do not wrap them in `useEffect`.
- **No test framework:** The project relies on manual testing of the UI and API.

## Additional Resources

- **Per-package instructions:** `frontend/AGENTS.md` contains detailed frontend-specific guidelines (conventions, styling, common pitfalls).
- **API Spec:** See `README.md` for a list of all available backend endpoints.
