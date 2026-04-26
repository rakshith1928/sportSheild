import imagehash
from PIL import Image
import numpy as np
import chromadb
import os
import uuid
from datetime import datetime
from transformers import CLIPProcessor, CLIPModel
import torch
import cv2
from typing import Optional

# Global variables
clip_model = None
clip_processor = None
chroma_client = None
asset_collection = None

def init_clip_model():
    global clip_model, clip_processor, chroma_client, asset_collection

    print("Loading CLIP model...")
    clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    clip_model.eval()

    # Init ChromaDB
    chroma_client = chromadb.PersistentClient(
        path=os.getenv("CHROMA_DB_PATH", "./chroma_db")
    )
    asset_collection = chroma_client.get_or_create_collection(
        name="sports_assets",
        metadata={"hnsw:space": "cosine"}
    )
    print(f"✅ CLIP ready. Assets in DB: {asset_collection.count()}")

def get_clip_embedding(image: Image.Image) -> list:
    """Get CLIP embedding for image"""
    inputs = clip_processor(images=image, return_tensors="pt")
    with torch.no_grad():
        embedding = clip_model.get_image_features(**inputs)
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
    image = Image.open(image_path).convert("RGB")
    asset_id = metadata.get("asset_id", str(uuid.uuid4()))

    # Generate both fingerprints
    phash = get_phash(image)
    clip_embedding = get_clip_embedding(image)

    # Store in ChromaDB
    asset_collection.upsert(
        ids=[asset_id],
        embeddings=[clip_embedding],
        metadatas=[{
            **metadata,
            "phash": phash,
            "asset_id": asset_id,
            "image_path": image_path,
            "fingerprinted_at": datetime.utcnow().isoformat(),
            "type": "image"
        }],
        documents=[f"Sports asset: {metadata.get('description', '')}"]
    )

    return {
        "asset_id": asset_id,
        "phash": phash,
        "stored_in_db": True,
        "total_assets": asset_collection.count()
    }

def compare_image_to_db(image: Image.Image, threshold: float = None) -> list:
    """
    Compare image against all stored assets
    Returns matches above similarity threshold
    """
    if threshold is None:
        threshold = float(os.getenv("SIMILARITY_THRESHOLD", 0.85))

    if asset_collection.count() == 0:
        return []

    # Layer 1: pHash
    query_phash = imagehash.hex_to_hash(get_phash(image))

    # Layer 2: CLIP similarity search
    query_embedding = get_clip_embedding(image)

    results = asset_collection.query(
        query_embeddings=[query_embedding],
        n_results=min(10, asset_collection.count()),
        include=["metadatas", "distances", "documents"]
    )

    matches = []
    if results and results["ids"][0]:
        for asset_id, distance, metadata in zip(
            results["ids"][0],
            results["distances"][0],
            results["metadatas"][0]
        ):
            # Convert distance to similarity score
            similarity = 1 - (distance / 2)

            if similarity >= threshold:
                stored_phash = imagehash.hex_to_hash(
                    metadata.get("phash", "0" * 16)
                )
                phash_distance = query_phash - stored_phash

                matches.append({
                    "asset_id": metadata.get("asset_id"),
                    "clip_similarity": round(similarity, 4),
                    "phash_distance": int(phash_distance),
                    "is_likely_copy": phash_distance < 10 or similarity > 0.92,
                    "metadata": metadata
                })

    return matches

def get_all_assets() -> list:
    """Get all stored assets"""
    if asset_collection.count() == 0:
        return []

    results = asset_collection.get(include=["metadatas"])
    seen = set()
    assets = []

    for metadata in results["metadatas"]:
        asset_id = metadata.get("asset_id")
        if asset_id not in seen:
            seen.add(asset_id)
            assets.append(metadata)

    return assets