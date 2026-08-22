import imagehash
from PIL import Image
import numpy as np
import logging
import os
import uuid
from transformers import CLIPProcessor, CLIPModel
import torch
import cv2
from typing import Optional, Any, cast
from services import vector_store

logger = logging.getLogger(__name__)

# Global variables
_clip_model: Optional[Any] = None
_clip_processor: Optional[Any] = None
device = "cuda" if torch.cuda.is_available() else "cpu"

# Number of evenly-spaced frames sampled from a video for CLIP embedding
MAX_VIDEO_FRAMES = 5


def init_clip_model():
    global _clip_model, _clip_processor

    logger.info(f"🖥️ Using device: {device}")
    logger.info("Loading CLIP model...")
    _clip_model = cast(Any, CLIPModel).from_pretrained("openai/clip-vit-base-patch32")
    _clip_processor = cast(Any, CLIPProcessor).from_pretrained("openai/clip-vit-base-patch32")

    if _clip_model:
        _clip_model.to(device)
        _clip_model.eval()

    asset_count = vector_store.count_assets()
    logger.info(f"✅ CLIP ready on {device}. Assets in pgvector DB: {asset_count}")


def get_clip_embedding(image: Image.Image) -> list:
    """Get CLIP embedding for image"""
    if _clip_processor is None or _clip_model is None:
        return []

    inputs = _clip_processor(images=image, return_tensors="pt").to(device)

    with torch.no_grad():
        embedding = _clip_model.get_image_features(**inputs)

    embedding = embedding / embedding.norm(dim=-1, keepdim=True)
    return embedding.squeeze().tolist()


def get_phash(image: Image.Image) -> str:
    """Get perceptual hash of image"""
    return str(imagehash.phash(image))


def fingerprint_image(image_path: str, metadata: dict) -> dict:
    """
    Dual fingerprint:
    Layer 1 - pHash (fast, detects exact copies)
    Layer 2 - CLIP embedding (smart, detects edited copies)
    """
    try:
        image = Image.open(image_path).convert("RGB")
    except Exception as e:
        return {"error": f"Could not open image: {str(e)}"}

    asset_id = metadata.get("asset_id", str(uuid.uuid4()))

    phash = get_phash(image)
    clip_embedding = get_clip_embedding(image)

    # Store in Supabase pgvector
    vector_store.upsert_asset_embedding(asset_id=asset_id, embedding=clip_embedding)

    total = vector_store.count_assets()

    return {
        "asset_id": asset_id,
        "phash": phash,
        "duplicate": False,
        "stored_in_db": True,
        "device_used": device,
        "total_assets": total,
    }


def extract_video_frames(video_path: str, max_frames: int = MAX_VIDEO_FRAMES) -> list:
    """
    Sample up to `max_frames` evenly spaced frames from a video.

    Returns a list of BGR numpy frames. Raises ValueError if the video
    cannot be opened or no frames can be read.
    """
    cap = cv2.VideoCapture(video_path)
    try:
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")

        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        if total > max_frames:
            indices = np.linspace(0, total - 1, max_frames).astype(int)
        elif total > 0:
            indices = range(total)
        else:
            # Container reports no frame count — read sequentially instead
            indices = range(max_frames)

        frames = []
        for index in indices:
            if total > 0:
                cap.set(cv2.CAP_PROP_POS_FRAMES, int(index))
            ok, frame = cap.read()
            if not ok or frame is None:
                continue
            frames.append(frame)
            if len(frames) >= max_frames:
                break

        if not frames:
            raise ValueError("Could not read any frames from video")
        return frames
    finally:
        cap.release()


def fingerprint_video(video_path: str, metadata: dict) -> dict:
    """
    Video fingerprint via CLIP frame sampling:
    - pHash of the middle sampled frame (fast, detects exact copies)
    - mean CLIP embedding over the sampled frames (detects edited copies)
    """
    try:
        frames = extract_video_frames(video_path)
    except ValueError as e:
        return {"error": str(e)}

    pil_frames = [
        Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)) for frame in frames
    ]
    representative = pil_frames[len(pil_frames) // 2]

    asset_id = metadata.get("asset_id", str(uuid.uuid4()))

    phash = get_phash(representative)

    embeddings = [get_clip_embedding(img) for img in pil_frames]
    embeddings = [e for e in embeddings if e]
    if embeddings:
        mean_embedding = np.mean(embeddings, axis=0)
        norm = float(np.linalg.norm(mean_embedding))
        clip_embedding = (mean_embedding / norm).tolist() if norm > 0 else []
    else:
        logger.warning("⚠️ CLIP embedding failed or model not initialized — storing empty embedding.")
        clip_embedding = []

    # NOTE: the local file path is intentionally NOT persisted anywhere — it
    # is a temporary file that is deleted right after fingerprinting.
    # Store in Supabase pgvector
    vector_store.upsert_asset_embedding(asset_id=asset_id, embedding=clip_embedding)

    total = vector_store.count_assets()

    return {
        "asset_id": asset_id,
        "phash": phash,
        "duplicate": False,
        "stored_in_db": True,
        "device_used": device,
        "total_assets": total,
        "type": "video",
        "frame_count": len(frames),
    }


def fingerprint_media(file_path: str, metadata: dict, content_type: str) -> dict:
    """Fingerprint a staged media file by its content type (image or video)."""
    if content_type.startswith("video/"):
        return fingerprint_video(file_path, metadata)
    if content_type.startswith("image/"):
        return fingerprint_image(file_path, metadata)
    return {"error": f"Unsupported content type: {content_type}"}


def compare_image_to_db(image: Image.Image, threshold: float | None = None) -> list:
    """
    Compare image against all stored assets.
    Returns matches above similarity threshold.
    """
    if threshold is None:
        threshold = float(os.getenv("SIMILARITY_THRESHOLD", 0.85))

    if vector_store.count_assets() == 0:
        return []

    query_phash = imagehash.hex_to_hash(get_phash(image))
    query_embedding = get_clip_embedding(image)
    if not query_embedding:
        logger.warning("⚠️ CLIP embedding failed or model not initialized — returning no matches.")
        return []

    raw_matches = vector_store.query_assets(
        query_embedding=query_embedding,
        n_results=10,
        threshold=threshold,
    )

    matches = []
    for row in raw_matches:
        similarity = float(row.get("similarity", 0))
        phash_hex = row.get("phash") or "0" * 16

        stored_phash = imagehash.hex_to_hash(phash_hex)
        phash_distance = query_phash - stored_phash

        matches.append({
            "asset_id": row.get("id"),
            "clip_similarity": round(similarity, 4),
            "phash_distance": phash_distance,
            "is_likely_copy": phash_distance < 10 or similarity > 0.92,
        })

    return sorted(matches, key=lambda x: x["clip_similarity"], reverse=True)
