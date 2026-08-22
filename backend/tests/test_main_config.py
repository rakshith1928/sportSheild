"""Fresh-deploy import + CORS configuration tests (audits B6 + B8).

B6: main.py mounted StaticFiles(directory="uploads") at import time.
StaticFiles checks the directory exists by default, so a fresh clone
(without backend/uploads/, which is gitignored) crashed at import —
the app never started. B1 moved all media to Supabase Storage +
system temp, so the local uploads dir has no remaining purpose.

B8: CORSMiddleware allow_origins treats entries as literal strings —
"*.vercel.app" never matches any real Vercel subdomain. Only
allow_origin_regex supports patterns.
"""
import importlib
import sys

from fastapi.testclient import TestClient

import pytest


def _fresh_main(tmp_path, monkeypatch):
    """Import main.py with cwd in an empty dir (no uploads/ present)."""
    assert not (tmp_path / "uploads").exists()
    monkeypatch.chdir(tmp_path)
    sys.modules.pop("main", None)
    return importlib.import_module("main")


def test_main_imports_in_fresh_environment(tmp_path, monkeypatch):
    """B6: import must not require a pre-existing uploads/ directory."""
    main_mod = _fresh_main(tmp_path, monkeypatch)
    assert main_mod.app is not None
    client = TestClient(main_mod.app)  # no context manager: lifespan skipped
    assert client.get("/health").json() == {"status": "healthy"}


@pytest.fixture
def cors_client(tmp_path, monkeypatch):
    main_mod = _fresh_main(tmp_path, monkeypatch)
    return TestClient(main_mod.app)


def test_cors_allows_vercel_subdomain(cors_client):
    r = cors_client.get("/health", headers={"Origin": "https://myapp.vercel.app"})
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") == "https://myapp.vercel.app"


def test_cors_allows_localhost_3000(cors_client):
    r = cors_client.get("/health", headers={"Origin": "http://localhost:3000"})
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_cors_rejects_lookalike_domain(cors_client):
    r = cors_client.get("/health", headers={"Origin": "https://vercel.app.evil.com"})
    assert "access-control-allow-origin" not in r.headers


def test_supabase_client_singletons_delegate_to_database(monkeypatch):
    """vector_store and rag_engine must use the shared services.database
    singleton — three independent clients meant three env-validation styles
    (RuntimeError vs KeyError) and three connection pools."""
    import services.database as database_mod
    import services.vector_store as vector_store
    import services.rag_engine as rag_engine

    sentinel = object()
    calls = []

    def fake_get_client():
        calls.append(1)
        return sentinel

    monkeypatch.setattr(database_mod, "get_supabase_client", fake_get_client)
    monkeypatch.setattr(vector_store, "_supabase", None)

    assert vector_store._get_client() is sentinel
    assert rag_engine._supabase_for_rag() is sentinel
