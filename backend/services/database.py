"""
SportShield AI — Supabase Database Service
Handles all PostgreSQL operations and metadata persistence.
"""
import os
from datetime import datetime, timezone
from typing import cast, Any
from supabase import create_client, Client
from postgrest import CountMethod
_supabase_client: Client | None = None
def get_supabase_client() -> Client:
    """Singleton Supabase client."""
    global _supabase_client
    if _supabase_client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        if not url or not key:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env"
            )
        _supabase_client = create_client(url, key)
    return _supabase_client

# ─── Assets ───────────────────────────────────────────────
def insert_asset(metadata: dict) -> dict:
    """Store asset metadata in Supabase after fingerprinting."""
    client = get_supabase_client()
    row = {
        "asset_id": metadata["asset_id"],
        "filename": metadata["filename"],
        "original_filename": metadata.get("original_filename"),
        "sport": metadata["sport"],
        "team": metadata["team"],
        "event": metadata.get("event", ""),
        "description": metadata.get("description", ""),
        "owner": metadata.get("owner", ""),
        "date": metadata.get("date", ""),
        "file_url": metadata.get("file_url"),
        "content_type": metadata.get("content_type"),
        "file_size_mb": metadata.get("file_size_mb"),
        "phash": metadata.get("phash"),
        "fingerprinted_at": datetime.now(timezone.utc).isoformat(),
    }
    result = client.table("assets").insert(row).execute()
    return cast(dict, result.data[0]) if result.data else row

def get_assets(user_id: str | None = None, limit: int = 50, offset: int = 0) -> dict:
    """List protected assets with pagination, newest first."""
    client = get_supabase_client()
    query = client.table("assets").select("*", count=CountMethod.exact).order("created_at", desc=True)
    if user_id:
        query = query.eq("owner", user_id)
    
    end_range = offset + limit - 1
    result = query.range(offset, end_range).execute()
    data = cast(list[dict], result.data) or []
    total = getattr(result, "count", 0) or len(data)
    return {"total": total, "assets": data}

def get_dashboard_stats(user_id: str) -> dict:
    """Fetch aggregate statistics for the dashboard, filtered by user."""
    client = get_supabase_client()
    
    # We use PostgREST join syntax to filter violations, scans, and reports based on the asset owner
    try:
        violations = client.table("violations").select("id, assets!inner(owner)", count=CountMethod.exact).eq("assets.owner", user_id).limit(1).execute()
        total_violations = getattr(violations, "count", 0) or 0
    except Exception:
        total_violations = 0

    try:
        assets = client.table("assets").select("asset_id", count=CountMethod.exact).eq("owner", user_id).limit(1).execute()
        total_assets = getattr(assets, "count", 0) or 0
    except Exception:
        total_assets = 0

    try:
        scans = client.table("scans").select("id, assets!inner(owner)", count=CountMethod.exact).eq("assets.owner", user_id).limit(1).execute()
        total_scans = getattr(scans, "count", 0) or 0
    except Exception:
        total_scans = 0

    try:
        reports = client.table("reports").select("report_id, assets!inner(owner)", count=CountMethod.exact).eq("assets.owner", user_id).limit(1).execute()
        total_reports = getattr(reports, "count", 0) or 0
    except Exception:
        total_reports = 0

    return {
        "active_threats": total_violations,
        "assets_scanned": total_scans,
        "assets_protected": total_assets,
        "takedowns_issued": total_reports
    }


# ─── Scans ─────────────────────────────────────────────────
def insert_scan(asset_id: str, query_used: str = "") -> dict:
    """Create a scan record when a scan starts."""
    client = get_supabase_client()
    row = {
        "asset_id": asset_id,
        "status": "scanning",
        "query_used": query_used,
    }
    result = client.table("scans").insert(row).execute()
    return cast(dict, result.data[0]) if result.data else row

def update_scan_status(
    scan_id: str,
    status: str,
    total_scanned: int = 0,
    violations_found: int = 0,
    errors: list | None = None,
) -> dict:
    """Update scan status on completion or failure."""
    client = get_supabase_client()
    update = {
        "status": status,
        "total_scanned": total_scanned,
        "violations_found": violations_found,
        "errors": errors or [],
    }
    if status in ("completed", "failed"):
        update["completed_at"] = datetime.now(timezone.utc).isoformat()
    result = (
        client.table("scans").update(update).eq("id", scan_id).execute()
    )
    return cast(dict, result.data[0]) if result.data else update

def get_scan_history(asset_id: str | None = None, user_id: str | None = None) -> list[dict]:
    """List scan history, optionally filtered by asset and by asset owner."""
    client = get_supabase_client()
    # Inner-join on assets so scans are scoped to the owner's assets
    # (same join pattern as get_dashboard_stats).
    select_clause = "*, assets!inner(owner)" if user_id else "*"
    query = client.table("scans").select(select_clause).order("started_at", desc=True)
    if user_id:
        query = query.eq("assets.owner", user_id)
    if asset_id:
        query = query.eq("asset_id", asset_id)
    result = query.execute()
    return cast(list[dict], result.data) or []

def get_scan_by_id(scan_id: str) -> dict | None:
    """Get a single scan record by its ID."""
    client = get_supabase_client()
    result = (
        client.table("scans").select("*").eq("id", scan_id).single().execute()
    )
    return cast(dict | None, result.data)

# ─── Violations ────────────────────────────────────────────
def insert_violation(violation_data: dict, scan_id: str | None = None) -> dict:
    """Store a detected violation."""
    client = get_supabase_client()
    row = {
        "asset_id": violation_data.get("asset_id"),
        "scan_id": scan_id,
        "image_url": violation_data["image_url"],
        "page_url": violation_data["page_url"],
        "title": violation_data.get("title", "Unknown"),
        "clip_similarity": violation_data["clip_similarity"],
        "phash_distance": violation_data.get("phash_distance"),
        "is_likely_copy": violation_data.get("is_likely_copy", False),
        "detected_at": violation_data.get("detected_at",
                                          datetime.now(timezone.utc).isoformat()),
    }
    result = client.table("violations").insert(row).execute()
    return cast(dict, result.data[0]) if result.data else row

def get_violations(
    asset_id: str | None = None,
    severity: str | None = None,
    limit: int = 50,
    offset: int = 0,
    user_id: str | None = None,
) -> dict:
    """Query violations with optional filters and pagination, sorted by similarity desc.

    When `user_id` is given, results are scoped to that user's assets via an
    inner join (violations whose asset row is missing or owned by someone
    else are excluded).
    """
    client = get_supabase_client()
    select_clause = "*, assets!inner(owner)" if user_id else "*"
    query = (
        client.table("violations")
        .select(select_clause, count=CountMethod.exact)
        .order("clip_similarity", desc=True)
    )
    if user_id:
        query = query.eq("assets.owner", user_id)
    if asset_id:
        query = query.eq("asset_id", asset_id)
    if severity:
        query = query.eq("severity", severity)
    end_range = offset + limit - 1
    result = query.range(offset, end_range).execute()
    data = cast(list[dict], result.data) or []
    total = getattr(result, "count", 0) or len(data)
    return {"total": total, "violations": data}

def get_recent_alerts(user_id: str, limit: int = 5) -> list[dict]:
    """Fetch the most recent violations for a user's assets, formatted as alerts for the dashboard."""
    client = get_supabase_client()
    
    result = (
        client.table("violations")
        .select("*, assets!inner(owner)")
        .eq("assets.owner", user_id)
        .order("detected_at", desc=True)
        .limit(limit)
        .execute()
    )
    
    alerts = []
    for row in result.data or []:
        if not isinstance(row, dict):
            continue
            
        # Determine severity based on similarity score
        sim_val = row.get("clip_similarity", 0)
        sim = float(cast(Any, sim_val)) if sim_val is not None else 0.0
        severity = "high" if sim > 0.9 else "medium" if sim > 0.75 else "low"
        
        # Format the date (we will send the ISO string and let frontend format it if needed, or simple mock)
        alerts.append({
            "id": row.get("id"),
            "title": row.get("title") or "Unauthorized distribution detected",
            "source": row.get("page_url"),
            "time": row.get("detected_at"),
            "severity": severity,
            "status": "New"
        })
        
    return alerts

def check_violation_exists(image_url: str) -> bool:
    """Check if a violation with this image_url already exists (dedup)."""
    client = get_supabase_client()
    result = (
        client.table("violations")
        .select("id")
        .eq("image_url", image_url)
        .limit(1)
        .execute()
    )
    return bool(result.data)
# ─── Reports ──────────────────────────────────────────────
def insert_report(report_meta: dict) -> dict:
    """Store report metadata after PDF generation."""
    client = get_supabase_client()
    row = {
        "report_id": report_meta["report_id"],
        "asset_id": report_meta.get("asset_id"),
        "violations_analyzed": report_meta.get("violations_analyzed", 0),
        "file_path": report_meta.get("file_path"),
        "download_url": report_meta.get("download_url"),
    }
    result = client.table("reports").insert(row).execute()
    return cast(dict, result.data[0]) if result.data else row

def get_reports(limit: int = 50, offset: int = 0, user_id: str | None = None) -> dict:
    """List reports with pagination, newest first, optionally scoped by asset owner."""
    client = get_supabase_client()
    select_clause = "*, assets!inner(owner)" if user_id else "*"
    query = client.table("reports").select(select_clause, count=CountMethod.exact).order("generated_at", desc=True)
    if user_id:
        query = query.eq("assets.owner", user_id)
    end_range = offset + limit - 1
    result = query.range(offset, end_range).execute()
    data = cast(list[dict], result.data) or []
    total = getattr(result, "count", 0) or len(data)
    return {"total": total, "reports": data}

def get_report_by_id(report_id: str, user_id: str) -> dict | None:
    """Fetch a single report scoped to the user's assets (owner-join)."""
    client = get_supabase_client()
    result = (
        client.table("reports")
        .select("*, assets!inner(owner)")
        .eq("report_id", report_id)
        .eq("assets.owner", user_id)
        .maybe_single()
        .execute()
    )
    return cast(dict | None, result.data)
