"""
Centralised Supabase pgvector client for SportShield.

Two vector collections:
  - asset_embeddings  (512-dim CLIP)   — uploaded asset fingerprints
  - rag_documents     (384-dim MiniLM) — legal knowledge base chunks

Required SQL (run once in Supabase SQL Editor):
─────────────────────────────────────────────────
create extension if not exists vector;

create table if not exists asset_embeddings (
  id         text primary key,
  embedding  vector(512),
  metadata   jsonb,
  document   text,
  created_at timestamptz default now()
);
create index on asset_embeddings using ivfflat (embedding vector_cosine_ops);

create table if not exists rag_documents (
  id         uuid primary key default gen_random_uuid(),
  content    text,
  metadata   jsonb,
  embedding  vector(384),
  created_at timestamptz default now()
);
create index on rag_documents using ivfflat (embedding vector_cosine_ops);

-- RPC for cosine similarity search (asset fingerprints)
create or replace function match_assets(
  query_embedding vector(512),
  match_count int,
  similarity_threshold float
)
returns table (
  id text,
  metadata jsonb,
  similarity float
)
language sql stable as $$
  select
    id,
    metadata,
    1 - (embedding <=> query_embedding) as similarity
  from asset_embeddings
  where 1 - (embedding <=> query_embedding) >= similarity_threshold
  order by embedding <=> query_embedding
  limit match_count;
$$;

-- RPC for cosine similarity search (RAG documents, required by LangChain)
create or replace function match_rag_documents(
  query_embedding vector(384),
  match_count int,
  filter jsonb default '{}'
)
returns table (
  id uuid,
  content text,
  metadata jsonb,
  similarity float
)
language sql stable as $$
  select
    id,
    content,
    metadata,
    1 - (embedding <=> query_embedding) as similarity
  from rag_documents
  where metadata @> filter
  order by embedding <=> query_embedding
  limit match_count;
$$;
─────────────────────────────────────────────────
"""

from __future__ import annotations
import logging
import os
from typing import Any, cast
from postgrest import CountMethod
from supabase import create_client, Client

logger = logging.getLogger(__name__)

_supabase: Client | None = None


def _get_client() -> Client:
    global _supabase
    if _supabase is None:
        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_SERVICE_KEY"]
        _supabase = create_client(url, key)
    return _supabase


# ---------------------------------------------------------------------------
# Asset Embeddings (CLIP 512-dim)
# ---------------------------------------------------------------------------

def upsert_asset_embedding(
    asset_id: str,
    embedding: list[float],
    metadata: dict[str, Any],
    document: str = "",
) -> None:
    """Store or update a CLIP embedding for a protected asset."""
    client = _get_client()
    client.table("asset_embeddings").upsert({
        "id": asset_id,
        "embedding": embedding,
        "metadata": metadata,
        "document": document,
    }).execute()
    logger.debug(f"📌 Upserted embedding for asset {asset_id}")


def query_assets(
    query_embedding: list[float],
    n_results: int = 10,
    threshold: float = 0.85,
) -> list[dict[str, Any]]:
    """
    Find the closest assets using cosine similarity via the match_assets RPC.
    Returns list of dicts with: id, metadata, similarity.
    """
    client = _get_client()
    try:
        resp = client.rpc(
            "match_assets",
            {
                "query_embedding": query_embedding,
                "match_count": n_results,
                "similarity_threshold": threshold,
            },
        ).execute()
        rows = resp.data
        if not isinstance(rows, list):
            return []
        return cast(list[dict[str, Any]], rows)
    except Exception as e:
        logger.error(f"query_assets RPC failed: {e}")
        return []


def get_asset_by_id(asset_id: str) -> dict[str, Any] | None:
    """Retrieve a single asset's metadata by its ID."""
    client = _get_client()
    resp = client.table("asset_embeddings").select("id,metadata").eq("id", asset_id).limit(1).execute()
    rows = resp.data
    if not isinstance(rows, list) or len(rows) == 0:
        return None
    row = cast(dict[str, Any], rows[0])
    return {**(row.get("metadata") or {}), "asset_id": row["id"]}


def get_all_assets() -> list[dict[str, Any]]:
    """Return metadata for every stored asset."""
    client = _get_client()
    resp = client.table("asset_embeddings").select("id,metadata").execute()
    rows = resp.data
    if not isinstance(rows, list):
        return []
    return [
        {**(cast(dict[str, Any], row).get("metadata") or {}), "asset_id": cast(dict[str, Any], row)["id"]}
        for row in rows
    ]


def count_assets() -> int:
    """Return the total number of stored asset embeddings."""
    client = _get_client()
    resp = client.table("asset_embeddings").select("id", count=CountMethod.exact).execute()
    return resp.count or 0


# ---------------------------------------------------------------------------
# RAG Documents (MiniLM 384-dim) — consumed by LangChain SupabaseVectorStore
# ---------------------------------------------------------------------------

def count_rag_documents() -> int:
    """Return the number of legal knowledge chunks already loaded."""
    client = _get_client()
    resp = client.table("rag_documents").select("id", count=CountMethod.exact).execute()
    return resp.count or 0
