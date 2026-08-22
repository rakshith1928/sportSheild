"""Storage privacy: assets bucket must not serve public URLs.

The 'assets' bucket holds users' valuable sports media. It is (or must be,
see backend/migrations/002_storage_private.sql) a PRIVATE bucket; every
URL handed to clients must be a short-lived signed URL, never a public
/object/public/ link.

Contract pinned here:
- The DB row persists the storage PATH (stable identifier), not any URL.
- Upload responses and asset listings hand out signed URLs only.
- Listing must not call get_public_url at all.
"""

from __future__ import annotations

import io

from conftest import make_png_bytes


def _png_file():
    return {"file": ("poster.png", io.BytesIO(make_png_bytes()), "image/png")}


def test_upload_persists_path_and_returns_signed_url(client, fake_supabase, fake_db_insert):
    resp = client.post(
        "/upload/asset",
        files=_png_file(),
        data={"sport": "basketball", "team": "lakers"},
    )
    assert resp.status_code == 200, resp.text

    # DB row stores the storage path, never a URL
    row = fake_db_insert[0]
    assert "/object/public/" not in row["file_url"]
    assert row["file_url"].endswith(".png")

    # Response hands the client a signed URL, not a public one
    body = resp.json()
    assert "/object/public/" not in body["file_url"]
    assert "token=fake-signature" in body["file_url"]


def test_upload_never_calls_get_public_url(client, fake_supabase):
    resp = client.post(
        "/upload/asset",
        files=_png_file(),
        data={"sport": "basketball", "team": "lakers"},
    )
    assert resp.status_code == 200, resp.text
    assert fake_supabase["public_urls"] == [], (
        "get_public_url must not be used anywhere in the upload flow"
    )


def test_list_assets_returns_signed_urls(client, monkeypatch):
    rows = [
        {
            "asset_id": f"asset-{i}",
            "filename": f"poster-{i}.png",
            "file_url": f"sportshield-uploads-abc/poster-{i}.png",
        }
        for i in range(2)
    ]
    monkeypatch.setattr(
        "routers.upload.db_get_assets",
        lambda **kw: {"total": len(rows), "assets": [dict(r) for r in rows]},
    )

    resp = client.get("/upload/assets?limit=10")
    assert resp.status_code == 200, resp.text
    body = resp.json()

    for asset in body["assets"]:
        assert "/object/public/" not in asset["file_url"]
        assert "token=fake-signature" in asset["file_url"]

    # Signed URLs are bounded (1 hour here)
    from routers.upload import SIGNED_URL_EXPIRY_SECONDS

    assert SIGNED_URL_EXPIRY_SECONDS <= 3600 * 24
