import os
import httpx
from PIL import Image
import io
from googleapiclient.discovery import build
from services.fingerprint import compare_image_to_db
from datetime import datetime

# Google API setup
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

def build_google_client():
    return build(
        "customsearch",
        "v1",
        developerKey=GOOGLE_API_KEY
    )

async def download_image(url: str) -> Image.Image | None:
    """Download image from URL and return PIL Image"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
            if response.status_code == 200:
                image = Image.open(
                    io.BytesIO(response.content)
                ).convert("RGB")
                return image
    except Exception:
        return None

async def scan_google_for_asset(
    asset_id: str,
    description: str,
    sport: str,
    team: str,
    threshold: float = None
) -> dict:
    """
    Search Google for unauthorized copies of an asset.
    Returns list of violations found.
    """
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        return {
            "error": "Google API keys not configured in .env"
        }

    if threshold is None:
        threshold = float(os.getenv("SIMILARITY_THRESHOLD", 0.85))

    # Build search query
    query = f"{sport} {team} {description} official media"

    print(f"🔍 Scanning web for: {query}")

    violations = []
    scanned_urls = []
    errors = []

    try:
        service = build_google_client()

        # Search for images
        result = service.cse().list(
            q=query,
            cx=GOOGLE_CSE_ID,
            searchType="image",
            num=10  # max per request on free tier
        ).execute()

        items = result.get("items", [])
        print(f"📸 Found {len(items)} images to scan")

        for item in items:
            image_url = item.get("link")
            page_url = item.get("image", {}).get("contextLink", image_url)

            if not image_url:
                continue

            scanned_urls.append(image_url)

            # Download and compare
            image = await download_image(image_url)
            if image is None:
                errors.append({
                    "url": image_url,
                    "reason": "Could not download"
                })
                continue

            # Compare against our protected asset
            matches = compare_image_to_db(image, threshold=threshold)

            # Filter matches for this specific asset
            asset_matches = [
                m for m in matches
                if m["asset_id"] == asset_id
            ]

            if asset_matches:
                best_match = asset_matches[0]
                violations.append({
                    "image_url": image_url,
                    "page_url": page_url,
                    "title": item.get("title", "Unknown"),
                    "clip_similarity": best_match["clip_similarity"],
                    "phash_distance": best_match["phash_distance"],
                    "is_likely_copy": best_match["is_likely_copy"],
                    "detected_at": datetime.utcnow().isoformat(),
                    "asset_id": asset_id
                })

    except Exception as e:
        return {
            "error": f"Scan failed: {str(e)}",
            "asset_id": asset_id
        }

    print(f"🚨 Found {len(violations)} violations")

    return {
        "asset_id": asset_id,
        "query_used": query,
        "total_scanned": len(scanned_urls),
        "violations_found": len(violations),
        "violations": violations,
        "errors": errors,
        "scanned_at": datetime.utcnow().isoformat()
    }