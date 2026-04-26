from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid
import aiofiles
from datetime import datetime

router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/mpeg", "video/quicktime"}
MAX_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", 50))

@router.post("/asset")
async def upload_asset(
    file: UploadFile = File(...),
    sport: str = Form(...),
    team: str = Form(...),
    event: str = Form(""),
    description: str = Form(""),
    owner: str = Form(""),
    date: str = Form("")
):
    # Validate file type
    if file.content_type not in ALLOWED_IMAGE_TYPES | ALLOWED_VIDEO_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported."
        )

    # Validate size
    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({size_mb:.1f}MB)."
        )

    # Save file
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    asset_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    filename = f"{asset_id}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    return JSONResponse({
        "success": True,
        "asset_id": asset_id,
        "filename": filename,
        "message": "Asset uploaded successfully! Fingerprinting coming in Phase 2."
    })

@router.get("/assets")
async def list_assets():
    return {
        "total": 0,
        "assets": [],
        "message": "Full asset list coming in Phase 2"
    }