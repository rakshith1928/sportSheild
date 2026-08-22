import asyncio
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse
import os
import uuid
import shutil
import tempfile
import aiofiles
import logging
from datetime import datetime, timezone
from PIL import Image
import io
from services.fingerprint import (
    fingerprint_media,
    compare_image_to_db
)
from services.database import insert_asset as db_insert_asset, get_assets as db_get_assets, get_supabase_client
from dependencies import get_current_user, limiter
from fastapi import Depends

logger = logging.getLogger(__name__)

router = APIRouter()

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/mpeg", "video/quicktime"}
MAX_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", 50))
# Storage object extension is derived from the (validated) content type,
# never from the untrusted user-supplied filename.
EXT_BY_CONTENT_TYPE = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "video/mp4": ".mp4",
    "video/mpeg": ".mpg",
    "video/quicktime": ".mov",
}


def _delete_storage_object(supabase, filename: str) -> None:
    """Best-effort removal of a Supabase Storage object to prevent orphans."""
    try:
        supabase.storage.from_("assets").remove([filename])
    except Exception as cleanup_err:
        logger.error(f"Failed to delete orphaned storage object {filename}: {cleanup_err}")


# Signed URLs handed to clients live for 1 hour. The 'assets' bucket is
# PRIVATE (see backend/migrations/002_storage_private.sql): user media must
# never be exposed via public /object/public/ URLs.
SIGNED_URL_EXPIRY_SECONDS = 3600


def _signed_url(supabase, path: str) -> str | None:
    """Create a short-lived signed URL for one storage object."""
    try:
        result = supabase.storage.from_("assets").create_signed_url(
            path, SIGNED_URL_EXPIRY_SECONDS
        )
        return result.get("signedURL") or result.get("signedUrl")
    except Exception as e:
        logger.error(f"Failed to sign URL for {path}: {e}")
        return None


def _attach_signed_urls(supabase, rows: list[dict]) -> list[dict]:
    """Replace stored storage-paths in `file_url` with signed URLs, batched.

    Legacy rows may hold absolute public URLs; their object path is parsed
    back out so they get re-signed too. Failures leave the original value.
    """
    paths = [r.get("file_url") for r in rows if r.get("file_url")]
    if not paths:
        return rows
    try:
        signed = supabase.storage.from_("assets").create_signed_urls(
            paths, SIGNED_URL_EXPIRY_SECONDS
        )
    except Exception as e:
        logger.error(f"Batch URL signing failed: {e}")
        return rows
    by_path = {
        item.get("path"): (item.get("signedURL") or item.get("signedUrl"))
        for item in signed or []
        if not item.get("error")
    }
    out = []
    for row in rows:
        row = dict(row)
        url = row.get("file_url")
        if url and url in by_path and by_path[url]:
            row["file_url"] = by_path[url]
        elif url and url.startswith("http"):
            # Legacy public URL — extract the object path and sign it singly.
            marker = "/object/public/assets/"
            if marker in url:
                path = url.split(marker, 1)[1]
                signed_single = _signed_url(supabase, path)
                if signed_single:
                    row["file_url"] = signed_single
        out.append(row)
    return out


STREAM_CHUNK_SIZE = 1024 * 1024  # 1MB


class FileTooLargeError(Exception):
    """Raised when a streamed upload crosses the configured byte cap."""


async def stream_upload_to_disk(upload_file, dest_path: str, max_bytes: int,
                                chunk_size: int = STREAM_CHUNK_SIZE) -> int:
    """Stream an UploadFile to disk in chunks, enforcing max_bytes.

    Aborts mid-transfer (without reading the rest of the body into memory)
    once the cap is crossed. Returns the number of bytes written.
    """
    written = 0
    async with aiofiles.open(dest_path, "wb") as out:
        while True:
            chunk = await upload_file.read(chunk_size)
            if not chunk:
                break
            written += len(chunk)
            if written > max_bytes:
                raise FileTooLargeError(
                    f"upload exceeded {max_bytes} bytes after {written} written"
                )
            await out.write(chunk)
    return written

@router.post("/asset")
@limiter.limit("10/minute")
async def upload_asset(
    request: Request,
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

    # Step 2 — Stage file in OS temp (temporary processing storage only).
    # Never inside the project/source tree; the per-request directory is
    # removed in the `finally` block below on every success/failure path.
    asset_id = str(uuid.uuid4())
    ext = EXT_BY_CONTENT_TYPE[file.content_type]
    filename = f"{asset_id}{ext}"
    temp_dir = tempfile.mkdtemp(prefix=f"sportshield-upload-{asset_id[:8]}-")
    file_path = os.path.join(temp_dir, filename)

    try:
        # Step 3 — Stream to disk with a hard byte cap. Oversized bodies are
        # rejected mid-transfer instead of being buffered fully in memory.
        try:
            size_bytes = await stream_upload_to_disk(
                file, file_path, MAX_SIZE_MB * 1024 * 1024
            )
        except FileTooLargeError:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max {MAX_SIZE_MB}MB."
            )
        size_mb = size_bytes / (1024 * 1024)

        # Step 4 — Load size-verified bytes for fingerprinting/storage.
        with open(file_path, "rb") as fh:
            content = fh.read()
        if file.content_type in ALLOWED_IMAGE_TYPES:
            try:
                image = Image.open(io.BytesIO(content)).convert("RGB")
                duplicates = await asyncio.to_thread(compare_image_to_db, image)
                if duplicates:
                    # Redact stored metadata: the caller only needs to know THAT
                    # a match exists, not other users' owner/description/file_url.
                    redacted_matches = [
                        {
                            "asset_id": m.get("asset_id"),
                            "clip_similarity": m.get("clip_similarity"),
                            "phash_distance": m.get("phash_distance"),
                            "is_likely_copy": m.get("is_likely_copy"),
                        }
                        for m in duplicates
                    ]
                    return JSONResponse(
                        status_code=409,
                        content={
                            "success": False,
                            "duplicate": True,
                            "message": "This asset is already protected!",
                            "matches": redacted_matches
                        }
                    )
            except Exception as e:
                # If image can't be read at all, reject immediately
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid image file: {str(e)}"
                )

        # Step 5.5 — Upload to Supabase Storage
        supabase = get_supabase_client()
        try:
            supabase.storage.from_("assets").upload(
                path=filename,
                file=content,
                file_options={"content-type": file.content_type}  # type: ignore
            )
            # Persist the storage PATH only; clients get short-lived signed
            # URLs generated at read time (the bucket is private).
            file_url = filename
        except Exception as e:
            logger.error(f"Supabase Storage upload failed for {filename}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Storage upload failed. Please try again."
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

        # Step 7 — Fingerprint (image or video) and store.
        # Anything that fails AFTER the Supabase upload must delete the
        # cloud object so no orphaned storage objects remain.
        try:
            result = await asyncio.to_thread(
                fingerprint_media, file_path, metadata, file.content_type
            )

            # Handle bad media
            if "error" in result:
                kind = "Video" if file.content_type.startswith("video/") else "Image"
                raise HTTPException(
                    status_code=400,
                    detail=f"{kind} error: {result['error']}"
                )

            # Step 8 — Dual-write to Supabase DB
            metadata["file_url"] = file_url
            metadata["phash"] = result.get("phash")
            try:
                db_insert_asset(metadata)
            except Exception as db_err:
                logger.warning(f"Supabase DB insert failed (non-fatal): {db_err}")

            # Success — hand the uploader a previewable signed URL
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "asset_id": asset_id,
                    "filename": filename,
                    "file_url": _signed_url(supabase, file_url),
                    "fingerprint": result,
                    "message": "Asset fingerprinted, stored in cloud, and protected!"
                }
            )

        except HTTPException:
            _delete_storage_object(supabase, filename)
            raise
        except Exception as e:
            _delete_storage_object(supabase, filename)
            logger.error(f"Fingerprinting failed for {asset_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Processing failed. Please try again."
            )
    finally:
        # Cleanup the temporary directory (file included) on every path
        shutil.rmtree(temp_dir, ignore_errors=True)

@router.get("/assets")
async def list_assets(limit: int = 50, offset: int = 0, user = Depends(get_current_user)):
    """List protected assets for the logged-in user with pagination"""
    try:
        result = db_get_assets(user_id=user.id, limit=limit, offset=offset)
        # The bucket is private: swap stored storage-paths for short-lived
        # signed URLs before anything reaches the client.
        supabase = get_supabase_client()
        result = dict(result)
        result["assets"] = _attach_signed_urls(supabase, result.get("assets", []))
        return result
    except Exception as e:
        logger.error(f"List assets failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Could not list assets. Please try again."
        )