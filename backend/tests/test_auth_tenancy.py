"""Auth + tenant isolation for all API routes (Phase 0 / S1+S2).

Every route must require a valid Supabase session, and every route that
returns user data must scope it to the authenticated user's assets.
"""
import pytest

from conftest import (
    FakeSupabaseClient,
    OWNED_ASSET,
    OTHER_ASSET,
    scan_mod,
    report_mod,
    explain_mod,
)

AUTH = {"Authorization": f"Bearer {FakeSupabaseClient.VALID_TOKEN}"}
BAD_AUTH = {"Authorization": "Bearer not-a-real-token"}

# (method, path, json body, params) for every route that must be auth-gated.
AUTH_MATRIX = [
    ("POST", "/scan/asset-123", None, {}),
    ("GET", "/scan/violations", None, {}),
    ("GET", "/scan/violations/asset-123", None, {}),
    ("GET", "/scan/history", None, {}),
    ("GET", "/scan/scan-123/status", None, {}),
    ("POST", "/explain/violation", {"image_url": "u", "page_url": "p", "clip_similarity": 0.9}, {}),
    ("POST", "/explain/search-laws", None, {"query": "dmca"}),
    ("POST", "/explain/batch", [{"image_url": "u", "page_url": "p", "clip_similarity": 0.9}], {}),
    ("POST", "/report/generate", {"asset_id": "asset-123", "violations": []}, {}),
    ("GET", "/report/status/job-123", None, {}),
    ("GET", "/report/download/ABC12345", None, {}),
    ("GET", "/report/list", None, {}),
    # already-protected routes — regression guard
    ("GET", "/upload/assets", None, {}),
    ("GET", "/dashboard/stats", None, {}),
]


# ---------------------------------------------------------------------------
# Authentication matrix
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("method,path,body,params", AUTH_MATRIX,
                         ids=[f"{m} {p}" for m, p, _, _ in AUTH_MATRIX])
def test_requires_authentication(full_client, db_env, method, path, body, params):
    resp = full_client.request(method, path, json=body, params=params)
    # FastAPI's HTTPBearer returns 401 (RFC 6750) for missing credentials
    assert resp.status_code in (401, 403), (
        f"{method} {path} must require authentication, got {resp.status_code}"
    )


@pytest.mark.parametrize("method,path,body,params", AUTH_MATRIX,
                         ids=[f"{m} {p}" for m, p, _, _ in AUTH_MATRIX])
def test_rejects_invalid_token(full_client, db_env, method, path, body, params):
    resp = full_client.request(method, path, json=body, params=params, headers=BAD_AUTH)
    assert resp.status_code == 401, (
        f"{method} {path} must reject invalid tokens with 401, got {resp.status_code}"
    )


# ---------------------------------------------------------------------------
# Tenancy: scans
# ---------------------------------------------------------------------------

def test_scan_rejects_other_users_asset(full_client, db_env, fake_asset_lookup, monkeypatch):
    fake_asset_lookup["asset-other"] = OTHER_ASSET

    def scanner_must_not_run(*args, **kwargs):
        raise AssertionError("scanner must not run for another user's asset")

    monkeypatch.setattr(scan_mod, "scan_google_for_asset", scanner_must_not_run)

    resp = full_client.post("/scan/asset-other", headers=AUTH)
    assert resp.status_code == 404


def test_scan_allowed_for_owned_asset(full_client, db_env, fake_asset_lookup, monkeypatch):
    fake_asset_lookup["asset-own"] = OWNED_ASSET

    async def fake_scan(**kwargs):
        return {"violations": [], "violations_found": 0, "total_scanned": 3}

    monkeypatch.setattr(scan_mod, "scan_google_for_asset", fake_scan)

    resp = full_client.post("/scan/asset-own", headers=AUTH)
    assert resp.status_code == 200, resp.text
    assert resp.json()["success"] is True
    assert resp.json()["asset_id"] == "asset-own"


def test_scan_history_is_owner_filtered(full_client, db_env):
    db_env["rows"]["scans"] = [{"id": "s1", "status": "completed"}]
    resp = full_client.get("/scan/history", headers=AUTH)
    assert resp.status_code == 200, resp.text

    scans_queries = [q for q in db_env["queries"] if q["table"] == "scans"]
    assert scans_queries, "no scans query was executed"
    assert ("assets.owner", "user-a") in scans_queries[-1]["filters"]
    assert "assets!inner" in (scans_queries[-1]["selects"] or "")


def test_scan_history_for_other_users_asset_404(full_client, db_env, fake_asset_lookup):
    fake_asset_lookup["asset-other"] = OTHER_ASSET
    resp = full_client.get("/scan/history", params={"asset_id": "asset-other"}, headers=AUTH)
    assert resp.status_code == 404


def test_scan_status_other_users_scan_404(full_client, db_env, fake_asset_lookup):
    db_env["rows"]["scans"] = [{"id": "scan-1", "asset_id": "asset-other", "status": "completed"}]
    fake_asset_lookup["asset-other"] = OTHER_ASSET

    resp = full_client.get("/scan/scan-1/status", headers=AUTH)
    assert resp.status_code == 404


def test_scan_status_owned_scan_ok(full_client, db_env, fake_asset_lookup):
    db_env["rows"]["scans"] = [{"id": "scan-1", "asset_id": "asset-own", "status": "completed"}]
    fake_asset_lookup["asset-own"] = OWNED_ASSET

    resp = full_client.get("/scan/scan-1/status", headers=AUTH)
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "completed"


def test_scan_status_missing_scan_404(full_client, db_env):
    resp = full_client.get("/scan/nope/status", headers=AUTH)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Tenancy: violations
# ---------------------------------------------------------------------------

def test_violations_list_is_owner_filtered(full_client, db_env):
    db_env["rows"]["violations"] = [
        {"id": "v1", "asset_id": "asset-own", "title": "t"},
        {"id": "v2", "asset_id": "asset-own", "title": "t2"},
    ]
    resp = full_client.get("/scan/violations", headers=AUTH)
    assert resp.status_code == 200, resp.text
    assert resp.json()["total"] == 2

    violations_queries = [q for q in db_env["queries"] if q["table"] == "violations"]
    assert violations_queries, "no violations query was executed"
    assert ("assets.owner", "user-a") in violations_queries[-1]["filters"]
    assert "assets!inner" in (violations_queries[-1]["selects"] or "")


def test_violations_by_other_users_asset_404(full_client, db_env, fake_asset_lookup):
    fake_asset_lookup["asset-other"] = OTHER_ASSET
    resp = full_client.get("/scan/violations/asset-other", headers=AUTH)
    assert resp.status_code == 404


def test_violations_by_owned_asset_ok(full_client, db_env, fake_asset_lookup):
    fake_asset_lookup["asset-own"] = OWNED_ASSET
    db_env["rows"]["violations"] = [{"id": "v1", "asset_id": "asset-own", "title": "t"}]

    resp = full_client.get("/scan/violations/asset-own", headers=AUTH)
    assert resp.status_code == 200, resp.text
    assert resp.json()["asset_id"] == "asset-own"
    assert resp.json()["total"] == 1


# ---------------------------------------------------------------------------
# Tenancy: reports
# ---------------------------------------------------------------------------

def test_report_generate_rejects_other_users_asset(full_client, db_env, fake_asset_lookup, monkeypatch):
    fake_asset_lookup["asset-other"] = OTHER_ASSET

    def job_must_not_run(job_id):
        raise AssertionError("report job must not be enqueued for another user's asset")

    monkeypatch.setattr(report_mod, "create_job", job_must_not_run)

    resp = full_client.post(
        "/report/generate",
        json={"asset_id": "asset-other", "violations": []},
        headers=AUTH,
    )
    assert resp.status_code == 404


def test_report_list_is_owner_filtered(full_client, db_env):
    db_env["rows"]["reports"] = [{"report_id": "R1", "asset_id": "asset-own"}]
    resp = full_client.get("/report/list", headers=AUTH)
    assert resp.status_code == 200, resp.text
    assert resp.json()["total"] == 1

    report_queries = [q for q in db_env["queries"] if q["table"] == "reports"]
    assert report_queries, "no reports query was executed"
    assert ("assets.owner", "user-a") in report_queries[-1]["filters"]
    assert "assets!inner" in (report_queries[-1]["selects"] or "")


def test_report_download_other_users_report_404(full_client, db_env):
    # No report rows at all => the owner-scoped lookup must come up empty.
    resp = full_client.get("/report/download/ABC12345", headers=AUTH)
    assert resp.status_code == 404

    report_queries = [q for q in db_env["queries"] if q["table"] == "reports"]
    assert report_queries, "no owner-scoped reports query was executed"
    assert ("assets.owner", "user-a") in report_queries[-1]["filters"]
    assert ("report_id", "ABC12345") in report_queries[-1]["filters"]


def test_report_download_malformed_id_404(full_client, db_env):
    # Generated ids are 8 uppercase hex chars; anything else is rejected
    # before touching the database or filesystem.
    resp = full_client.get("/report/download/not-a-valid-id", headers=AUTH)
    assert resp.status_code == 404
    assert [q for q in db_env["queries"] if q["table"] == "reports"] == []


# ---------------------------------------------------------------------------
# Explain endpoints: auth-gated, functional for a valid session
# ---------------------------------------------------------------------------

def test_explain_endpoints_work_for_valid_session(full_client, db_env, monkeypatch):
    monkeypatch.setattr(
        explain_mod,
        "explain_violation",
        lambda v: {
            "confidence": 0.9,
            "severity": "high",
            "explanation": "e",
            "legal_context": [],
            "recommended_action": "a",
        },
    )
    monkeypatch.setattr(explain_mod, "query_rag", lambda q, law_filter=None: [])

    r1 = full_client.post(
        "/explain/violation",
        json={"image_url": "u", "page_url": "p", "clip_similarity": 0.95},
        headers=AUTH,
    )
    assert r1.status_code == 200, r1.text

    r2 = full_client.post("/explain/search-laws", params={"query": "dmca"}, headers=AUTH)
    assert r2.status_code == 200, r2.text

    r3 = full_client.post(
        "/explain/batch",
        json=[{"image_url": "u", "page_url": "p", "clip_similarity": 0.95}],
        headers=AUTH,
    )
    assert r3.status_code == 200, r3.text
    assert r3.json()["total_explained"] == 1
