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
import services.database as database_mod  # noqa: E402
import dependencies as dependencies_mod  # noqa: E402
from dependencies import get_current_user  # noqa: E402
from routers import upload as upload_mod  # noqa: E402
from routers import scan as scan_mod  # noqa: E402
from routers import explain as explain_mod  # noqa: E402
from routers import report as report_mod  # noqa: E402
from routers import dashboard as dashboard_mod  # noqa: E402


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
        fail = self._recorder.get("fail_upload")
        if fail is not None:
            raise fail
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


# ---------------------------------------------------------------------------
# Full-app fixtures for auth / tenancy tests
# ---------------------------------------------------------------------------

class FakeQuery:
    """Records PostgREST query shape and serves canned rows per table."""

    def __init__(self, recorder, table):
        self.recorder = recorder
        self.table = table
        self.selects = None
        self.filters = []
        self.range_args = None
        self.single_mode = None
        self._pending_row = None

    def select(self, cols="*", count=None):
        self.selects = cols
        return self

    def eq(self, col, val):
        self.filters.append((col, val))
        return self

    def order(self, col, **kwargs):
        return self

    def range(self, a, b):
        self.range_args = (a, b)
        return self

    def limit(self, n):
        return self

    def single(self):
        self.single_mode = "single"
        return self

    def maybe_single(self):
        self.single_mode = "maybe_single"
        return self

    def insert(self, row):
        self._pending_row = row
        return self

    def update(self, values):
        self._pending_row = values
        return self

    def execute(self):
        self.recorder["queries"].append(
            {
                "table": self.table,
                "selects": self.selects,
                "filters": list(self.filters),
                "range": self.range_args,
                "single_mode": self.single_mode,
                "insert": self._pending_row,
            }
        )
        rows = list(self.recorder["rows"].get(self.table, []))
        if self._pending_row is not None:
            rows = [self._pending_row]
        if self.single_mode == "single":
            if not rows:
                raise ValueError("no rows in single query")  # emulate PostgrestException
            return SimpleNamespace(data=rows[0], count=None)
        if self.single_mode == "maybe_single":
            return SimpleNamespace(data=rows[0] if rows else None, count=None)
        return SimpleNamespace(data=rows, count=None)


class FakeSupabaseClient:
    """Stands in for the Supabase client: fake auth + recording query builder."""

    VALID_TOKEN = "valid-token"
    USER_ID = "user-a"

    def __init__(self, recorder):
        self.recorder = recorder

    class _Auth:
        def __init__(self, recorder):
            self.recorder = recorder

        def get_user(self, token):
            self.recorder["auth_tokens"].append(token)
            if token == FakeSupabaseClient.VALID_TOKEN:
                return SimpleNamespace(user=SimpleNamespace(id=FakeSupabaseClient.USER_ID))
            return None

    @property
    def auth(self):
        return self._Auth(self.recorder)

    def table(self, name):
        return FakeQuery(self.recorder, name)


@pytest.fixture
def db_env(monkeypatch):
    """Fake Supabase client shared by the database service and the auth dependency.

    Recorder shape:
      rows:      {table: [row, ...]} — canned data returned by selects
      queries:   [{table, selects, filters, single_mode}, ...] — every query executed
      auth_tokens: [token, ...] — tokens seen by auth.get_user
    """
    recorder = {"rows": {}, "queries": [], "auth_tokens": []}
    client = FakeSupabaseClient(recorder)
    monkeypatch.setattr(database_mod, "get_supabase_client", lambda: client)
    monkeypatch.setattr(dependencies_mod, "get_supabase_client", lambda: client)
    return recorder


@pytest.fixture
def fake_asset_lookup(monkeypatch):
    """Fake pgvector asset lookup used by scan/report routers.

    Tests fill the returned dict: {asset_id: metadata_with_owner, ...}
    """
    assets = {}

    def fake_get_asset_by_id(asset_id):
        return assets.get(asset_id)

    monkeypatch.setattr(scan_mod, "get_asset_by_id", fake_get_asset_by_id)
    monkeypatch.setattr(report_mod, "get_asset_by_id", fake_get_asset_by_id)
    return assets


@pytest.fixture
def full_client(monkeypatch, db_env, fake_asset_lookup):
    """App with ALL routers, real auth dependency, rate limiting disabled.

    (No get_current_user override — these tests exercise the real JWT gate.)
    """
    monkeypatch.setattr(dependencies_mod.limiter, "enabled", False)
    app = FastAPI()
    app.include_router(upload_mod.router, prefix="/upload", tags=["Upload"])
    app.include_router(scan_mod.router, prefix="/scan", tags=["Scan"])
    app.include_router(explain_mod.router, prefix="/explain", tags=["Explain"])
    app.include_router(report_mod.router, prefix="/report", tags=["Report"])
    app.include_router(dashboard_mod.router, prefix="/dashboard", tags=["Dashboard"])
    return TestClient(app)


OWNED_ASSET = {
    "asset_id": "asset-own",
    "owner": "user-a",
    "sport": "cricket",
    "team": "Mumbai Indians",
    "description": "Team jersey",
}
OTHER_ASSET = {
    "asset_id": "asset-other",
    "owner": "user-b",
    "sport": "cricket",
    "team": "RCB",
    "description": "Team jersey",
}
