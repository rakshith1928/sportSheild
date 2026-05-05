# 🛡️ SportShield AI
### Enterprise-grade Digital Asset Protection for Sports Media using AI Fingerprinting

> Built for the Google for Developers Hackathon on Hack2Skill

[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2015-black?logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Supabase](https://img.shields.io/badge/Database-Supabase-3ECF8E?logo=supabase)](https://supabase.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🚀 What It Does

SportShield AI protects sports media organizations from copyright theft at scale:

1. **Upload** — Sports orgs upload official media (images/videos)
2. **Fingerprint** — System creates a dual AI fingerprint (pHash + CLIP embeddings)
3. **Scan** — Web scanner autonomously detects unauthorized copies across the internet
4. **Explain** — RAG engine generates legal context (DMCA, Indian Copyright Act) for each violation
5. **Report** — One-click automated PDF takedown notices

---

## 🧠 Tech Stack

| Layer | Tool |
|---|---|
| **Image Fingerprinting** | pHash + CLIP (`openai/clip-vit-base-patch32`) |
| **Video Fingerprinting** | CLIP frame sampling |
| **Vector Search** | ChromaDB |
| **Web Scanning** | Google Custom Search API |
| **RAG Knowledge Base** | LangChain + ChromaDB |
| **LLM Explanations** | Groq (`llama3-70b-8192`) |
| **Backend** | FastAPI + Python |
| **Frontend** | Next.js 15 (App Router) + Tailwind CSS v4 |
| **Auth** | Supabase Auth (SSR) |
| **Database** | Supabase (PostgreSQL) |
| **Storage** | Supabase Storage (Phase 5) |
| **Deploy** | Railway (backend) + Vercel (frontend) |

---

## 📁 Project Structure

```
sportshield/
├── backend/
│   ├── main.py                  # FastAPI entry point + CORS + lifespan
│   ├── routers/
│   │   ├── upload.py            # Asset upload + fingerprinting
│   │   ├── scan.py              # Web scanning + violation detection
│   │   ├── explain.py           # RAG legal explanations
│   │   └── report.py            # PDF report generation
│   ├── services/
│   │   ├── fingerprint.py       # pHash + CLIP fingerprinting
│   │   ├── web_scanner.py       # Google Custom Search scanning
│   │   ├── rag_engine.py        # LangChain RAG engine
│   │   ├── database.py          # Supabase PostgreSQL service
│   │   └── report_generator.py  # PDF generation
│   ├── knowledge_base/
│   │   └── ip_laws/             # DMCA, Indian Copyright Act docs
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx             # Public Landing Page
│   │   │   ├── login/page.tsx       # Auth Gateway
│   │   │   ├── dashboard/           # Protected Dashboard (requires auth)
│   │   │   │   ├── layout.tsx       # Auth-guarded layout
│   │   │   │   └── page.tsx         # Main dashboard
│   │   │   └── auth/callback/       # Supabase OAuth callback
│   │   ├── components/
│   │   │   ├── auth/AuthForm.tsx    # Login/Signup form
│   │   │   └── dashboard/           # StatCard, AlertRow, SeverityBadge
│   │   ├── utils/supabase/          # Supabase SSR client helpers
│   │   └── middleware.ts            # Route protection middleware
│   └── package.json
└── README.md
```

---

## ⚙️ Local Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- A [Supabase](https://supabase.com) project
- A [Groq](https://console.groq.com) API key
- A [Google Custom Search](https://programmablesearchengine.google.com) Engine + API key

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Fill in your API keys in .env

# Run server
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Setup environment
cp .env.local.example .env.local
# Fill in your Supabase credentials in .env.local

# Run dev server
npm run dev
```

---

## 🔑 Environment Variables

### Backend (`backend/.env`)
```env
GROQ_API_KEY=your_groq_key
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_custom_search_engine_id
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
CHROMA_DB_PATH=./chroma_db
UPLOAD_DIR=./uploads
```

### Frontend (`frontend/.env.local`)
```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_SITE_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/upload/asset` | Upload + fingerprint an asset |
| `GET` | `/upload/assets` | List all protected assets |
| `POST` | `/scan/{asset_id}` | Trigger a web scan for an asset |
| `GET` | `/scan/violations` | Get all detected violations |
| `GET` | `/scan/history` | Get past scan history |
| `POST` | `/explain/violation` | Get RAG legal context for a violation |
| `POST` | `/report/generate` | Generate a PDF takedown report |
| `GET` | `/health` | Health check |

---

## 🏗️ Build Progress

- [x] Phase 1 — Design System & Component Migration (globals.css, StatCard, AlertRow, SeverityBadge)
- [x] Phase 2 — Auth & Landing Page Gateway (Supabase Auth, /login, /auth/callback, middleware protection)
- [ ] Phase 3 — Static Dashboard Layout (App.tsx → dashboard/page.tsx)
- [ ] Phase 4 — Real-time API Client (api.ts + Supabase Realtime)
- [ ] Phase 5 — Upload Flow & Cloud Storage (Supabase Storage)
- [ ] Phase 6 — Violations RAG & Reports (DetailsDrawer + PDF)
- [ ] Phase 7 — Enterprise Backend Scalability (Queues, RBAC, Pagination)

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.
