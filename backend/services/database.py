"""
SportShield AI — Supabase Database Service
Handles all PostgreSQL operations. ChromaDB remains for vector embeddings only.
"""
import os
from datetime import datetime, timezone
from supabase import create_client, Client
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
    return result.data[0] if result.data else row
def get_assets() -> list[dict]:
    """List all protected assets, newest first."""
    client = get_supabase_client()
    result = (
        client.table("assets")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return result.data or []


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
    return result.data[0] if result.data else row
def update_scan_status(
    scan_id: str,
    status: str,
    total_scanned: int = 0,
    violations_found: int = 0,
    errors: list = None,
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
    return result.data[0] if result.data else update
def get_scan_history(asset_id: str = None) -> list[dict]:
    """List scan history, optionally filtered by asset."""
    client = get_supabase_client()
    query = client.table("scans").select("*").order("started_at", desc=True)
    if asset_id:
        query = query.eq("asset_id", asset_id)
    result = query.execute()
    return result.data or []
def get_scan_by_id(scan_id: str) -> dict | None:
    """Get a single scan record by its ID."""
    client = get_supabase_client()
    result = (
        client.table("scans").select("*").eq("id", scan_id).single().execute()
    )
    return result.data

# ─── Violations ────────────────────────────────────────────
def insert_violation(violation_data: dict, scan_id: str = None) -> dict:
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
    return result.data[0] if result.data else row
def get_violations(
    asset_id: str = None,
    severity: str = None,
) -> list[dict]:
    """Query violations with optional filters, sorted by similarity desc."""
    client = get_supabase_client()
    query = (
        client.table("violations")
        .select("*")
        .order("clip_similarity", desc=True)
    )
    if asset_id:
        query = query.eq("asset_id", asset_id)
    if severity:
        query = query.eq("severity", severity)
    result = query.execute()
    return result.data or []
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
    return result.data[0] if result.data else row
def get_reports() -> list[dict]:
    """List all reports, newest first."""
    client = get_supabase_client()
    result = (
        client.table("reports")
        .select("*")
        .order("generated_at", desc=True)
        .execute()
    )
    return result.data or []
