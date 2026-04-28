import os
import httpx
import asyncio
from PIL import Image
import io
from googleapiclient.discovery import build
from services.fingerprint import compare_image_to_db
from datetime import datetime

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

            if response.status_code != 200:
                print(f" Bad status {response.status_code} for {url}")
                return None

            content_type = response.headers.get("content-type", "")
            if "image" not in content_type:
                print(f" Not an image ({content_type}): {url}")
                return None

            if len(response.content) > 5 * 1024 * 1024:
                print(f" Image too large (>5MB): {url}")
                return None

            image = Image.open(
                io.BytesIO(response.content)
            ).convert("RGB")
            return image

    except Exception as e:
        print(f"Failed to download {url}: {e}")
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
    Downloads all images in parallel then compares.
    """
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        return {
            "error": "Google API keys not configured in .env"
        }

    if threshold is None:
        threshold = float(os.getenv("SIMILARITY_THRESHOLD", 0.85))

    #Improved search query
    query = f"{team} {sport} {description} logo OR poster OR official"
    print(f"🔍 Scanning web for: {query}")

    violations = []
    scanned_urls = []
    errors = []
    seen_urls = set()

    try:
        service = build_google_client()

        result = service.cse().list(
            q=query,
            cx=GOOGLE_CSE_ID,
            searchType="image",
            num=10
        ).execute()

        # Handle empty results safely
        items = result.get("items", []) or []
        print(f"Found {len(items)} images to scan")

        #Build parallel download tasks
        tasks = []
        url_map = []

        for item in items:
            image_url = item.get("link")
            page_url = item.get("image", {}).get("contextLink", image_url)

            # Skip if no URL or already seen
            if not image_url or image_url in seen_urls:
                continue

            seen_urls.add(image_url)
            scanned_urls.append(image_url)

            tasks.append(download_image(image_url))
            url_map.append((image_url, page_url, item))

        # Download all images in parallel
        print(f"⬇️ Downloading {len(tasks)} images in parallel...")
        images = await asyncio.gather(*tasks)

        # Process results
        for img, (image_url, page_url, item) in zip(images, url_map):
            if img is None:
                errors.append({
                    "url": image_url,
                    "reason": "Download failed"
                })
                continue

            # Compare against protected assets
            matches = compare_image_to_db(img, threshold=threshold)

            # Filter for this specific asset
            asset_matches = [
                m for m in matches
                if m["asset_id"] == asset_id
            ]

            if asset_matches:
                # Sort and pick best match
                best_match = sorted(
                    asset_matches,
                    key=lambda x: x["clip_similarity"],
                    reverse=True
                )[0]

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

    # Sort violations by similarity
    violations = sorted(
        violations,
        key=lambda x: x["clip_similarity"],
        reverse=True
    )

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