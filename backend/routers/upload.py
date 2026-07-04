from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid
import aiofiles
import logging
from datetime import datetime, timezone
from PIL import Image
import io
from services.fingerprint import (
    fingerprint_image,
    get_all_assets,
    compare_image_to_db
)
from services.database import insert_asset as db_insert_asset, get_assets as db_get_assets, get_supabase_client
from dependencies import get_current_user
from fastapi import Depends

logger = logging.getLogger(__name__)

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
    date: str = Form(""),
    user = Depends(get_current_user)
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

    # Step 5 — Save file to disk temporarily for fingerprinting
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    asset_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename or "")[1]
    filename = f"{asset_id}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    # Step 5.5 — Upload to Supabase Storage
    supabase = get_supabase_client()
    try:
        supabase.storage.from_("assets").upload(
            path=filename,
            file=content,
            file_options={"content-type": file.content_type}  # type: ignore
        )
        file_url = supabase.storage.from_("assets").get_public_url(filename)
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=500,
            detail=f"Supabase Storage upload failed: {str(e)}"
        )

    # Step 6 — Build metadata
    metadata = {
        "asset_id": asset_id,
        "filename": filename,
        "original_filename": file.filename,
        "sport": sport,
        "team": team,
        "event": event,
        "description": description,
        "owner": user.id,
        "date": date,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "file_size_mb": round(size_mb, 2),
        "content_type": file.content_type
    }

    # Step 7 — Fingerprint and store
    try:
        result = fingerprint_image(file_path, metadata)

        # Handle bad image
        if "error" in result:
            raise HTTPException(
                status_code=400,
                detail=f"Image error: {result['error']}"
            )

        # Step 8 — Dual-write to Supabase DB
        metadata["file_url"] = file_url
        metadata["phash"] = result.get("phash")
        try:
            db_insert_asset(metadata)
        except Exception as db_err:
            logger.warning(f"Supabase DB insert failed (non-fatal): {db_err}")

        # Success
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "asset_id": asset_id,
                "filename": filename,
                "file_url": file_url,
                "fingerprint": result,
                "message": "Asset fingerprinted, stored in cloud, and protected!"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Fingerprinting failed: {str(e)}"
        )
    finally:
        # Cleanup local temporary file regardless of HTTP success or failure
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as cleanup_err:
                logger.error(f"Failed to cleanup temp file {file_path}: {cleanup_err}")

@router.get("/assets")
async def list_assets(user = Depends(get_current_user)):
    """List all protected assets for the logged-in user"""
    try:
        supabase = get_supabase_client()
        result = (
            supabase.table("assets")
            .select("*")
            .eq("owner", user.id)
            .order("created_at", desc=True)
            .execute()
        )
        assets = result.data or []
        return {"total": len(assets), "assets": assets}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list assets: {str(e)}"
        )