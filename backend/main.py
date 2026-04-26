from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()

from routers import upload, scan, explain, report
from services.rag_engine import init_rag
#from services.fingerprint import init_clip_model

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting SportShield AI...")
    os.makedirs(os.getenv("UPLOAD_DIR", "uploads"), exist_ok=True)
    os.makedirs("chroma_db", exist_ok=True)
    print("📦 Loading CLIP model...")
    #init_clip_model()
    print("📚 Initializing RAG knowledge base...")
    init_rag()
    print("✅ SportShield AI ready!")
    yield
    # Shutdown
    print("👋 Shutting down SportShield AI...")

app = FastAPI(
    title="SportShield AI",
    description="Digital Asset Protection for Sports Media using AI Fingerprinting",
    version="1.0.0",
    lifespan=lifespan
)

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploaded assets
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Routers
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(scan.router, prefix="/scan", tags=["Scan"])
app.include_router(explain.router, prefix="/explain", tags=["Explain"])
app.include_router(report.router, prefix="/report", tags=["Report"])

@app.get("/")
async def root():
    return {
        "name": "SportShield AI",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}