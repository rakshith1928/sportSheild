import imagehash
from PIL import Image
import numpy as np
import logging
import os
import uuid
from datetime import datetime, timezone
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

    full_metadata = {
        **metadata,
        "phash": phash,
        "asset_id": asset_id,
        "image_path": image_path,
        "fingerprinted_at": datetime.now(timezone.utc).isoformat(),
        "type": "image",
    }

    # Store in Supabase pgvector
    vector_store.upsert_asset_embedding(
        asset_id=asset_id,
        embedding=clip_embedding,
        metadata=full_metadata,
        document=f"Sports asset: {metadata.get('description', '')}",
    )

    total = vector_store.count_assets()

    return {
        "asset_id": asset_id,
        "phash": phash,
        "duplicate": False,
        "stored_in_db": True,
        "device_used": device,
        "total_assets": total,
    }


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
        metadata = row.get("metadata") or {}

        stored_phash = imagehash.hex_to_hash(metadata.get("phash", "0" * 16))
        phash_distance = query_phash - stored_phash

        matches.append({
            "asset_id": metadata.get("asset_id"),
            "clip_similarity": round(similarity, 4),
            "phash_distance": phash_distance,
            "is_likely_copy": phash_distance < 10 or similarity > 0.92,
            "metadata": metadata,
        })

    return sorted(matches, key=lambda x: x["clip_similarity"], reverse=True)


def get_all_assets() -> list:
    """Get all stored assets from pgvector"""
    return vector_store.get_all_assets()