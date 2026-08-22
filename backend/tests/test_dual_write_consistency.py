"""Dual-write consistency: assets metadata + asset_embeddings pgvector row.

The two tables are written by separate HTTP calls (no shared transaction),
so the upload flow must compensate on failure: if the metadata insert
fails after the embedding was upserted, the embedding row is deleted and
the storage object removed — an asset that is invisible to dashboards and
tenant scoping must not keep living in pgvector (where it would still
participate in cross-tenant duplicate checks).
"""

from __future__ import annotations

import io

import pytest

from conftest import make_png_bytes


def test_metadata_insert_failure_cleans_embedding_and_storage(
    client, monkeypatch, fake_supabase
):
    from routers import upload as upload_mod
    from services import vector_store as vs

    monkeypatch.setattr(
        upload_mod, "db_insert_asset", lambda m: (_ for _ in ()).throw(RuntimeError("db down"))
    )
    deletes = []
    monkeypatch.setattr(upload_mod, "delete_asset_embedding", lambda aid: deletes.append(aid))

    resp = client.post(
        "/upload/asset",
        files={"file": ("poster.png", io.BytesIO(make_png_bytes()), "image/png")},
        data={"sport": "basketball", "team": "lakers"},
    )

    assert resp.status_code == 500, resp.text
    assert len(deletes) == 1 and deletes[0]  # embedding removed for the asset id
    assert fake_supabase["removes"], "storage object must be cleaned up too"
    # And nothing pretends success
    body = resp.json()
    assert body.get("success") is not True


def test_pgvector_metadata_holds_no_local_file_paths(client, fake_vector_store):
    """The temp file path is ephemeral (deleted right after upload); persisting
    it in pgvector metadata leaves a forever-stale pointer."""
    resp = client.post(
        "/upload/asset",
        files={"file": ("poster.png", io.BytesIO(make_png_bytes()), "image/png")},
        data={"sport": "basketball", "team": "lakers"},
    )
    assert resp.status_code == 200, resp.text
    stored_meta = fake_vector_store[0]["metadata"]
    for key in ("image_path", "file_path", "temp_dir"):
        assert key not in stored_meta
