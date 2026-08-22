"""Security: no internal details or cross-tenant metadata in client responses.

Covers two audit findings:
- Cross-tenant duplicate leak: the 409 duplicate response must not include
  other users' asset metadata (owner, description, file_url, ...).
- Error detail leakage: HTTPException details and response bodies must not
  contain raw str(e) text from internal exceptions (connection strings,
  paths, third-party error bodies).
"""

import io

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import routers.upload as upload_mod
import routers.scan as scan_mod
import routers.explain as explain_mod


@pytest.fixture
def dup_match():
    """A pgvector match that carries another user's full stored metadata."""
    return {
        "asset_id": "other-users-asset",
        "clip_similarity": 0.97,
        "phash_distance": 2,
        "is_likely_copy": True,
        "metadata": {
            "asset_id": "other-users-asset",
            "owner": "user-b-secret-owner-id",
            "description": "PRIVATE STRATEGY BOARD",
            "file_url": "https://secret.example.com/other-user-file.jpg",
            "sport": "basketball",
            "team": "internal-team",
        },
    }


def _upload_image(client, monkeypatch, compare_result=None):
    if compare_result is not None:
        monkeypatch.setattr(upload_mod, "compare_image_to_db", lambda img: compare_result)
    png = io.BytesIO()
    try:
        from PIL import Image as PILImage
        PILImage.new("RGB", (32, 32), (200, 60, 60)).save(png, format="PNG")
    except ImportError:  # pragma: no cover
        pytest.skip("PIL unavailable")
    return client.post(
        "/upload/asset",
        files={"file": ("shot.png", png.getvalue(), "image/png")},
        data={"sport": "basketball", "team": "lakers"},
    )


def test_duplicate_response_redacts_other_users_metadata(client, monkeypatch, dup_match):
    resp = _upload_image(client, monkeypatch, compare_result=[dup_match])
    assert resp.status_code == 409
    body = resp.text
    assert "user-b-secret-owner-id" not in body
    assert "PRIVATE STRATEGY BOARD" not in body
    assert "secret.example.com" not in body
    # Match identity/scores are fine to expose; the payload blob is not.
    matches = resp.json()["matches"]
    assert matches[0]["asset_id"] == "other-users-asset"
    assert "metadata" not in matches[0]


def test_storage_upload_failure_leaks_no_internal_error(client, monkeypatch, fake_supabase):
    fake_supabase["fail_upload"] = Exception(
        "postgrest: host=db.internal.co key=SECRET-CONN-STRING"
    )
    resp = _upload_image(client, monkeypatch, compare_result=[])
    assert resp.status_code == 500
    body = resp.text
    assert "SECRET-CONN-STRING" not in body
    assert "db.internal.co" not in body


def test_fingerprint_failure_leaks_no_internal_error(client, monkeypatch):
    def boom(*a, **kw):
        raise RuntimeError("CUDA error at C:\\Users\\admin\\torch\\SECRET.dll")
    monkeypatch.setattr(upload_mod, "fingerprint_media", boom)
    resp = _upload_image(client, monkeypatch, compare_result=[])
    assert resp.status_code == 500
    assert "SECRET" not in resp.text
    assert "C:\\Users" not in resp.text


def test_scan_failure_leaks_no_internal_error(full_client, monkeypatch, fake_asset_lookup):
    from tests.conftest import FakeSupabaseClient, OWNED_ASSET
    fake_asset_lookup["scan-target"] = dict(OWNED_ASSET)

    async def fake_scan(**kwargs):
        return {
            "error": "Scan failed: googleapiclient HttpError SECRET-API-BODY",
            "asset_id": kwargs["asset_id"],
        }
    monkeypatch.setattr(scan_mod, "scan_google_for_asset", fake_scan)
    resp = full_client.post(
        "/scan/scan-target",
        headers={"Authorization": f"Bearer {FakeSupabaseClient.VALID_TOKEN}"},
    )
    assert resp.status_code == 500
    assert "SECRET-API-BODY" not in resp.text


def test_explain_failure_leaks_no_internal_error(full_client, monkeypatch):
    def boom(violation):
        raise Exception("groq.BadRequestError: org-SECRET internal trace")
    monkeypatch.setattr(explain_mod, "explain_violation", boom)
    from tests.conftest import FakeSupabaseClient
    resp = full_client.post(
        "/explain/violation",
        headers={"Authorization": f"Bearer {FakeSupabaseClient.VALID_TOKEN}"},
        json={
            "image_url": "https://x.example/i.jpg",
            "page_url": "https://x.example/p",
            "clip_similarity": 0.95,
        },
    )
    assert resp.status_code == 500
    assert "org-SECRET" not in resp.text
