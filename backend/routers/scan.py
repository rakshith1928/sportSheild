from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from services.web_scanner import scan_google_for_asset
from services.database import (
    insert_scan, update_scan_status, insert_violation,
    get_violations, check_violation_exists,
    get_scan_history, get_scan_by_id,
)
import chromadb
import asyncio
import os

router = APIRouter()


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

    # Create scan record in Supabase
    query_used = f"{metadata.get('sport', '')} {metadata.get('team', '')} {metadata.get('description', '')}"
    scan_record = insert_scan(asset_id=asset_id, query_used=query_used.strip())
    scan_id = scan_record.get("id")

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
        update_scan_status(
            scan_id=scan_id,
            status="failed",
            errors=[scan_result["error"]],
        )
        raise HTTPException(
            status_code=500,
            detail=scan_result["error"]
        )

    # Store violations in Supabase (with dedup)
    new_violations = scan_result.get("violations", [])
    stored_count = 0
    for violation in new_violations:
        if not check_violation_exists(violation["image_url"]):
            insert_violation(violation, scan_id=scan_id)
            stored_count += 1

    # Update scan record with results
    update_scan_status(
        scan_id=scan_id,
        status="completed",
        total_scanned=scan_result.get("urls_scanned", 0),
        violations_found=scan_result.get("violations_found", 0),
    )

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "asset_id": asset_id,
            "scan_id": scan_id,
            "scan_result": scan_result,
            "message": f"Scan complete! Found {scan_result['violations_found']} violations."
        }
    )


@router.get("/violations")
async def get_all_violations(severity: str = None):
    """Get all detected violations, with optional severity filter"""
    violations = get_violations(severity=severity)
    return {
        "total": len(violations),
        "violations": violations
    }


@router.get("/violations/{asset_id}")
async def get_violations_by_asset(asset_id: str):
    """Get violations for a specific asset"""
    violations = get_violations(asset_id=asset_id)
    return {
        "asset_id": asset_id,
        "total": len(violations),
        "violations": violations
    }


@router.get("/history")
async def scan_history(asset_id: str = None):
    """List all past scans, optionally filtered by asset"""
    scans = get_scan_history(asset_id=asset_id)
    return {
        "total": len(scans),
        "scans": scans
    }


@router.get("/{scan_id}/status")
async def scan_status(scan_id: str):
    """Get real-time status of a specific scan"""
    scan = get_scan_by_id(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan
