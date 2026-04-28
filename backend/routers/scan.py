from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from services.web_scanner import scan_google_for_asset
import chromadb
import asyncio
import os

router = APIRouter()

# In-memory violations store
# Phase 5 will move this to PostgreSQL
violations_store = []

@router.post("/{asset_id}")
async def scan_asset(asset_id: str):
    """Trigger web scan for a specific asset"""

    # Get asset metadata from ChromaDB
    chroma_client = chromadb.PersistentClient(
        path=os.getenv("CHROMA_DB_PATH", "./chroma_db")
    )
    collection = chroma_client.get_or_create_collection("sports_assets")

    # Find asset by ID
    try:
        result = collection.get(ids=[asset_id])
        if not result["ids"]:
            raise HTTPException(
                status_code=404,
                detail=f"Asset {asset_id} not found"
            )
        metadata = result["metadatas"][0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Asset not found: {str(e)}"
        )

    # Run web scan
    print(f"🔍 Starting scan for asset: {asset_id}")
    scan_result = await scan_google_for_asset(
        asset_id=asset_id,
        description=metadata.get("description", ""),
        sport=metadata.get("sport", ""),
        team=metadata.get("team", "")
    )

    # Rate limit protection between scan calls
    await asyncio.sleep(1)

    # Handle scan error
    if "error" in scan_result:
        raise HTTPException(
            status_code=500,
            detail=scan_result["error"]
        )

    # Store violations in memory
    new_violations = scan_result.get("violations", [])
    for violation in new_violations:
        # Avoid duplicate violations in store
        existing_urls = [v["image_url"] for v in violations_store]
        if violation["image_url"] not in existing_urls:
            violations_store.append(violation)

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "asset_id": asset_id,
            "scan_result": scan_result,
            "message": f"Scan complete! Found {scan_result['violations_found']} violations."
        }
    )

@router.get("/violations")
async def get_violations():
    """Get all detected violations"""

    # Sort by similarity before returning
    sorted_violations = sorted(
        violations_store,
        key=lambda x: x["clip_similarity"],
        reverse=True
    )

    return {
        "total": len(sorted_violations),
        "violations": sorted_violations
    }

@router.get("/violations/{asset_id}")
async def get_violations_by_asset(asset_id: str):
    """Get violations for a specific asset"""

    asset_violations = [
        v for v in violations_store
        if v["asset_id"] == asset_id
    ]

    # Sort by similarity
    asset_violations = sorted(
        asset_violations,
        key=lambda x: x["clip_similarity"],
        reverse=True
    )

    return {
        "asset_id": asset_id,
        "total": len(asset_violations),
        "violations": asset_violations
    }

@router.delete("/violations/clear")
async def clear_violations():
    """Clear all violations from memory"""
    violations_store.clear()
    return {
        "message": "All violations cleared",
        "total": 0
    }