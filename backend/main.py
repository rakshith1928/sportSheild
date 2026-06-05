import logging
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger("sportshield")
logger.debug(f"Logging initialized at level={LOG_LEVEL}")

from routers import upload, scan, explain, report, dashboard
from services.rag_engine import init_rag
from services.fingerprint import init_clip_model
from services.database import get_supabase_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting SportShield AI...")
    os.makedirs(os.getenv("UPLOAD_DIR", "uploads"), exist_ok=True)
    os.makedirs("chroma_db", exist_ok=True)
    logger.info("Loading CLIP model...")
    init_clip_model()
    logger.info("Initializing RAG knowledge base...")
    init_rag()
    logger.info("Connecting to Supabase...")
    try:
        get_supabase_client()
        logger.info("Supabase connected!")
    except Exception as e:
        logger.warning(f"Supabase connection failed: {e}")
        logger.warning("  Backend will work but data won't persist across restarts.")
    logger.info("SportShield AI ready!")
    yield
    # Shutdown
    logger.info("Shutting down SportShield AI...")

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
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])

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