from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from services.web_scanner import scan_google_for_asset
from services.database import (
    insert_scan, update_scan_status, insert_violation,
    get_violations, check_violation_exists,
    get_scan_history, get_scan_by_id, get_recent_alerts
)
from services.vector_store import get_asset_by_id
import asyncio
import logging
from dependencies import get_current_user, limiter

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/{asset_id}")
@limiter.limit("3/minute")
async def scan_asset(asset_id: str, request: Request, user = Depends(get_current_user)):
    """Trigger web scan for a specific asset (owner only)"""

    # Get asset metadata from Supabase pgvector
    try:
        metadata = get_asset_by_id(asset_id)
        if not metadata:
            raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
        # Tenant isolation: only the asset owner may scan it.
        # 404 (not 403) so asset ids cannot be enumerated across users.
        if metadata.get("owner") != user.id:
            raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
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
    scan_id = str(scan_record.get("id", "")) if scan_record else ""

    # Run web scan
    logger.info(f"🔍 Starting scan for asset: {asset_id}")
    scan_result = await scan_google_for_asset(
        asset_id=asset_id,
        description=str(metadata.get("description", "")),
        sport=str(metadata.get("sport", "")),
        team=str(metadata.get("team", ""))
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
async def get_all_violations(severity: str | None = None, limit: int = 50, offset: int = 0, user = Depends(get_current_user)):
    """Get detected violations for the logged-in user's assets, with optional severity filter and pagination"""
    return get_violations(severity=severity, limit=limit, offset=offset, user_id=user.id)

@router.get("/alerts")
async def get_alerts(limit: int = 5, user = Depends(get_current_user)):
    """Get the most recent alerts (violations) for the dashboard"""
    alerts = get_recent_alerts(user_id=user.id, limit=limit)
    return alerts


@router.get("/violations/{asset_id}")
async def get_violations_by_asset(asset_id: str, limit: int = 50, offset: int = 0, user = Depends(get_current_user)):
    """Get violations for a specific asset with pagination (owner only)"""
    asset = get_asset_by_id(asset_id)
    if not asset or asset.get("owner") != user.id:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
    res = dict(get_violations(asset_id=asset_id, limit=limit, offset=offset))
    res["asset_id"] = asset_id
    return res


@router.get("/history")
async def scan_history(asset_id: str | None = None, user = Depends(get_current_user)):
    """List past scans for the logged-in user's assets, optionally filtered by asset"""
    if asset_id:
        asset = get_asset_by_id(asset_id)
        if not asset or asset.get("owner") != user.id:
            raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
    scans = get_scan_history(asset_id=asset_id, user_id=user.id)
    return {
        "total": len(scans),
        "scans": scans
    }


@router.get("/{scan_id}/status")
async def scan_status(scan_id: str, user = Depends(get_current_user)):
    """Get real-time status of a specific scan (owner only)"""
    try:
        scan = get_scan_by_id(scan_id)
    except Exception:
        scan = None
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    # Tenant isolation: the scan's asset must belong to the requesting user.
    asset = get_asset_by_id(scan.get("asset_id", ""))
    if not asset or asset.get("owner") != user.id:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan
