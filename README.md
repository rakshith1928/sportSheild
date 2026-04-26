# 🛡️ SportShield AI
### Digital Asset Protection for Sports Media using AI Fingerprinting

Built for Google for Developers Hackathon on Hack2Skill

---

## 🚀 How It Works

1. Sports org uploads official media (images/videos)
2. System creates dual AI fingerprint (pHash + CLIP embeddings)
3. Web scanner detects unauthorized copies across the internet
4. RAG engine explains violations with legal context (DMCA, Indian Copyright Act)
5. Generate takedown notices automatically

---

## 🧠 Tech Stack

| Layer | Tool |
|---|---|
| Image Fingerprinting | pHash + CLIP (openai/clip-vit-base-patch32) |
| Video Fingerprinting | CLIP frame sampling |
| Similarity Search | ChromaDB |
| Web Scanning | Google Custom Search API |
| RAG Knowledge Base | LangChain + ChromaDB |
| LLM Explanations | Groq (llama3-70b) |
| Backend | FastAPI + Python |
| Frontend | Next.js 14 + Tailwind CSS |
| Deploy | Railway (backend) + Vercel (frontend) |

---

## 📁 Project Structure

```
sportshield/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── routers/
│   │   ├── upload.py        # Asset upload + fingerprinting
│   │   ├── scan.py          # Web scanning
│   │   ├── explain.py       # RAG legal explanations
│   │   └── report.py        # PDF report generation
│   ├── services/
│   │   ├── fingerprint.py   # pHash + CLIP fingerprinting
│   │   ├── web_scanner.py   # Google search scanning
│   │   ├── rag_engine.py    # LangChain RAG
│   │   └── report_generator.py
│   ├── knowledge_base/
│   │   └── ip_laws/         # DMCA, Copyright Act docs
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx         # Dashboard
│   │   ├── upload/          # Upload assets
│   │   ├── dashboard/       # Violations dashboard
│   │   └── violations/      # Violation details
│   └── components/
└── README.md
```

---

## ⚙️ Setup

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
# Edit .env with your API keys

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

# Run dev server
npm run dev
```

---

## 🔑 API Keys Needed

| Key | Where to get | Cost |
|---|---|---|
| GROQ_API_KEY | console.groq.com | Free |
| GOOGLE_API_KEY | console.developers.google.com | Free tier |
| GOOGLE_CSE_ID | programmablesearchengine.google.com | Free |

---

## 📡 API Endpoints

```
POST /upload/asset          Upload + fingerprint asset
GET  /upload/assets         List all protected assets
POST /scan/{asset_id}       Trigger web scan
GET  /scan/violations       Get all violations
POST /explain/violation     RAG legal explanation
GET  /report/{id}           Download PDF report
GET  /health                Health check
```

---

## 🏗️ Build Phases

- [x] Phase 1 — Project setup + folder structure
- [ ] Phase 2 — pHash + CLIP fingerprinting engine
- [ ] Phase 3 — Google web scanner
- [ ] Phase 4 — RAG legal engine
- [ ] Phase 5 — FastAPI endpoints
- [ ] Phase 6 — Next.js dashboard
- [ ] Phase 7 — Deploy

---
