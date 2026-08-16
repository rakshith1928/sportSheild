"""Shared fixtures for the upload pipeline tests.

No network, no real Supabase, no CLIP model download:
- Supabase client is faked (records uploads/removes).
- pgvector store functions are faked (record upserts).
- CLIP model globals are turned off by default (per-test overrides allowed).
- The Supabase auth dependency is overridden with a fixed user.
"""
import io
import os
import sys
from types import SimpleNamespace

import cv2
import pytest
from PIL import Image
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Keep FFmpeg's stderr quiet (corrupt-media tests decode garbage on purpose)
try:
    cv2.setLogLevel(0)  # 0 == LOG_LEVEL_SILENT (enum constant not exposed in all builds)
except Exception:
    pass

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import services.fingerprint as fingerprint  # noqa: E402
import services.vector_store as vector_store  # noqa: E402
from dependencies import get_current_user  # noqa: E402
from routers import upload as upload_mod  # noqa: E402


def make_png_bytes(size=(32, 32), color=(255, 107, 107)) -> bytes:
    """Generate a tiny real PNG in memory."""
    img = Image.new("RGB", size, color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


class FakeStorageBucket:
    def __init__(self, recorder):
        self._recorder = recorder

    def upload(self, path, file, file_options=None):
        self._recorder["uploads"].append(
            {"path": path, "size": len(file), "options": file_options}
        )
        return {"Id": path}

    def get_public_url(self, path):
        return f"https://fake.supabase.co/storage/v1/object/public/assets/{path}"

    def remove(self, paths):
        removed = list(paths)
        self._recorder["removes"].append(removed)
        return [{"Id": p} for p in removed]


class FakeSupabase:
    def __init__(self, recorder):
        self._recorder = recorder
        self._bucket = FakeStorageBucket(recorder)

    @property
    def storage(self):
        return self

    def from_(self, name):
        self._recorder["bucket"] = name
        return self._bucket


@pytest.fixture(autouse=True)
def fake_supabase(monkeypatch):
    """Record Supabase Storage interactions instead of hitting the network."""
    recorder = {"uploads": [], "removes": [], "bucket": None}
    monkeypatch.setattr(
        upload_mod, "get_supabase_client", lambda: FakeSupabase(recorder)
    )
    return recorder


@pytest.fixture(autouse=True)
def fake_vector_store(monkeypatch):
    """Record pgvector upserts; pretend one asset already exists."""
    upserts = []

    def fake_upsert(asset_id, embedding, metadata, document=""):
        upserts.append(
            {"asset_id": asset_id, "embedding": embedding, "metadata": metadata}
        )

    monkeypatch.setattr(vector_store, "upsert_asset_embedding", fake_upsert)
    monkeypatch.setattr(vector_store, "count_assets", lambda: 1)
    return upserts


@pytest.fixture(autouse=True)
def fake_db_insert(monkeypatch):
    """Record the `assets` table insert."""
    inserts = []
    monkeypatch.setattr(upload_mod, "db_insert_asset", lambda m: inserts.append(m))
    return inserts


@pytest.fixture(autouse=True)
def clip_model_off(monkeypatch):
    """No CLIP model by default (avoids torch inference in tests)."""
    monkeypatch.setattr(fingerprint, "_clip_model", None)
    monkeypatch.setattr(fingerprint, "_clip_processor", None)


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(upload_mod.router, prefix="/upload")
    app.dependency_overrides[get_current_user] = (
        lambda: SimpleNamespace(id="test-user-123")
    )
    return TestClient(app)


@pytest.fixture
def media_spy(monkeypatch):
    """Wrap the real fingerprint dispatcher to record the temp file path
    and whether the file existed while fingerprinting ran."""
    real = fingerprint.fingerprint_media
    rec = {}

    def spy(file_path, metadata, content_type):
        rec["path"] = file_path
        rec["existed_during_processing"] = os.path.exists(file_path)
        return real(file_path, metadata, content_type)

    monkeypatch.setattr(upload_mod, "fingerprint_media", spy)
    return rec
