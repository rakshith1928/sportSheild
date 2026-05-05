# Changelog

All notable changes to SportShield AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### In Progress
- Phase 3: Static Dashboard layout migration
- Phase 4: Real-time API client + Supabase Realtime
- Phase 5: Upload flow + Supabase Storage
- Phase 6: Violations RAG drawer + PDF reports
- Phase 7: Backend scalability (task queues, RBAC, pagination)

---

## [0.2.0] - 2026-05-05

### Added
- Public Landing Page (`/`) with animated hero, feature showcase, and stats
- Supabase Auth integration — Sign In / Sign Up via `/login`
- `/auth/callback` route for email confirmation flow
- Protected `/dashboard` route group with dual-layer auth guard (middleware + server layout)
- Middleware auto-redirects: unauthenticated → `/login`, authenticated → `/dashboard`
- `CONTRIBUTING.md`, `LICENSE`, `SECURITY.md`, `.env.example` files
- GitHub Issue and PR templates

### Fixed
- `location.origin` replaced with production-safe `window.location.origin` + `NEXT_PUBLIC_SITE_URL`
- Material Symbols font moved to root `layout.tsx` so it loads on every page
- Auth error handling upgraded from `catch (err: any)` to `catch (err: unknown)` with `instanceof Error`

---

## [0.1.0] - 2026-04-30

### Added
- Next.js 15 (App Router) project initialized in `frontend/`
- Tailwind CSS v4 design system with SportShield AI design tokens (`globals.css`)
- `StatCard`, `AlertRow`, `SeverityBadge` components migrated from Figma export
- `ImageWithFallback` helper component
- `utils.ts` with `clsx` + `tailwind-merge` setup
- Supabase PostgreSQL integration for assets, scans, and violations
- FastAPI backend with `upload`, `scan`, `explain`, and `report` routers
- CLIP + pHash dual fingerprinting engine
- Google Custom Search web scanner
- LangChain + ChromaDB RAG engine for legal explanations
- Groq LLM integration for violation context generation
