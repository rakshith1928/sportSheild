"""B5: blocking sync work must run OFF the event loop thread.

Each test patches the blocking dependency with a probe that records whether
an asyncio event loop was running in the executing thread. Running on the
loop = the whole API froze during this call = RED.
"""

import asyncio
import io

import pytest
from PIL import Image

from conftest import FakeSupabaseClient


def _probe_result(rec, key, ret):
    """Return a callable that records whether it ran off the event loop."""

    def probe(*args, **kwargs):
        try:
            asyncio.get_running_loop()
            rec[key] = False
        except RuntimeError:
            rec[key] = True
        return ret

    return probe


def _png_bytes():
    buf = io.BytesIO()
    Image.new("RGB", (32, 32), (10, 200, 90)).save(buf, format="PNG")
    return buf.getvalue()


def test_fingerprint_media_runs_off_event_loop(client, monkeypatch):
    rec = {}
    monkeypatch.setattr(
        "routers.upload.fingerprint_media",
        _probe_result(rec, "off_loop", {"phash": "0" * 16}),
    )
    resp = client.post(
        "/upload/asset",
        files={"file": ("a.png", _png_bytes(), "image/png")},
        data={"sport": "basketball", "team": "lakers"},
    )
    assert resp.status_code == 200
    assert rec["off_loop"] is True


def test_duplicate_compare_runs_off_event_loop(client, monkeypatch):
    rec = {}
    import routers.upload as upload_mod
    monkeypatch.setattr(upload_mod, "compare_image_to_db", _probe_result(rec, "off_loop", []))
    resp = client.post(
        "/upload/asset",
        files={"file": ("a.png", _png_bytes(), "image/png")},
        data={"sport": "basketball", "team": "lakers"},
    )
    assert resp.status_code == 200
    assert rec["off_loop"] is True


def test_explain_llm_call_runs_off_event_loop(full_client, monkeypatch):
    rec = {}
    import routers.explain as explain_mod
    monkeypatch.setattr(explain_mod, "explain_violation", _probe_result(rec, "off_loop", {
        "explanation": "e", "recommended_action": "a",
        "confidence": 0.9, "severity": "high",
        "legal_context": [], "sources": [],
    }))
    resp = full_client.post(
        "/explain/violation",
        headers={"Authorization": f"Bearer {FakeSupabaseClient.VALID_TOKEN}"},
        json={
            "image_url": "https://x.example/i.jpg",
            "page_url": "https://x.example/p",
            "clip_similarity": 0.95,
        },
    )
    assert resp.status_code == 200
    assert rec["off_loop"] is True


def test_query_rag_runs_off_event_loop(full_client, monkeypatch):
    rec = {}
    import routers.explain as explain_mod
    monkeypatch.setattr(explain_mod, "query_rag", _probe_result(rec, "off_loop", []))
    resp = full_client.post(
        "/explain/search-laws?query=dmca+takedown",
        headers={"Authorization": f"Bearer {FakeSupabaseClient.VALID_TOKEN}"},
    )
    assert resp.status_code == 200
    assert rec["off_loop"] is True


class _FakeCse:
    def list(self, **kwargs):
        return self

    def execute(self):
        return {
            "items": [{
                "link": "https://img.example/found.jpg",
                "image": {"contextLink": "https://page.example/post"},
            }]
        }


class _FakeService:
    def cse(self):
        return _FakeCse()


def test_scan_pipeline_blocking_steps_run_off_event_loop(
    full_client, monkeypatch, fake_asset_lookup
):
    """The Google CSE call and per-image CLIP comparison must not block."""
    from services.fingerprint import compare_image_to_db as _unused  # noqa: F401
    import services.web_scanner as scanner

    OWNED_ASSET = {
        "asset_id": "scan-target",
        "owner": FakeSupabaseClient.USER_ID,
        "sport": "basketball",
        "team": "lakers",
        "description": "poster",
    }
    fake_asset_lookup["scan-target"] = OWNED_ASSET

    rec = {}

    def fake_build(*a, **kw):
        return _probe_result(rec, "cse_off_loop", _FakeService())()

    async def fake_download(url):
        return Image.new("RGB", (16, 16))

    def fake_compare(img, threshold=None):
        try:
            asyncio.get_running_loop()
            rec["compare_off_loop"] = False
        except RuntimeError:
            rec["compare_off_loop"] = True
        return []

    monkeypatch.setattr(scanner, "GOOGLE_API_KEY", "fake-key")
    monkeypatch.setattr(scanner, "GOOGLE_CSE_ID", "fake-cse")
    monkeypatch.setattr(scanner, "build_google_client", fake_build)
    monkeypatch.setattr(scanner, "download_image", fake_download)
    monkeypatch.setattr(scanner, "compare_image_to_db", fake_compare)

    resp = full_client.post(
        "/scan/scan-target",
        headers={"Authorization": f"Bearer {FakeSupabaseClient.VALID_TOKEN}"},
    )
    assert resp.status_code == 200
    assert rec["cse_off_loop"] is True
    assert rec["compare_off_loop"] is True
