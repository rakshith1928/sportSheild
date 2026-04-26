from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid
import aiofiles
from datetime import datetime
from PIL import Image
import io
from services.fingerprint import (
    fingerprint_image,
    get_all_assets,
    compare_image_to_db
)

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
    """Upload and fingerprint a sports media asset"""

    # Step 1 — Validate file type
    all_allowed = ALLOWED_IMAGE_TYPES | ALLOWED_VIDEO_TYPES
    if file.content_type not in all_allowed:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file.content_type} not supported."
        )

    # Step 2 — Read content
    content = await file.read()

    # Step 3 — Validate size
    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({size_mb:.1f}MB). Max {MAX_SIZE_MB}MB."
        )

    # Step 4 — Check duplicate BEFORE saving to disk
    if file.content_type in ALLOWED_IMAGE_TYPES:
        try:
            image = Image.open(io.BytesIO(content)).convert("RGB")
            duplicates = compare_image_to_db(image)
            if duplicates:
                return JSONResponse(
                    status_code=409,
                    content={
                        "success": False,
                        "duplicate": True,
                        "message": "This asset is already protected!",
                        "matches": duplicates
                    }
                )
        except Exception as e:
            # If image can't be read at all, reject immediately
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image file: {str(e)}"
            )

    # Step 5 — Save file to disk (only reaches here if not duplicate)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    asset_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    filename = f"{asset_id}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    # Step 6 — Build metadata
    metadata = {
        "asset_id": asset_id,
        "filename": filename,
        "original_filename": file.filename,
        "sport": sport,
        "team": team,
        "event": event,
        "description": description,
        "owner": owner,
        "date": date,
        "uploaded_at": datetime.utcnow().isoformat(),
        "file_size_mb": round(size_mb, 2),
        "content_type": file.content_type
    }

    # Step 7 — Fingerprint and store
    try:
        result = fingerprint_image(file_path, metadata)

        # Handle bad image
        if "error" in result:
            os.remove(file_path)
            raise HTTPException(
                status_code=400,
                detail=f"Image error: {result['error']}"
            )

        # Success
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "asset_id": asset_id,
                "filename": filename,
                "file_url": f"/uploads/{filename}",
                "fingerprint": result,
                "message": "Asset fingerprinted and protected!"
            }
        )

    except HTTPException:
        raise

    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=500,
            detail=f"Fingerprinting failed: {str(e)}"
        )

@router.get("/assets")
async def list_assets():
    """List all protected assets"""
    assets = get_all_assets()
    return {
        "total": len(assets),
        "assets": assets
    }