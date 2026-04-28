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
