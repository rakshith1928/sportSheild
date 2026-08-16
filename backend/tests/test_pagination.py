"""Pagination bounds (audit S8).

limit/offset were unbounded and passed straight into PostgREST
range()/limit(). A client sending limit=10**8 forced Postgres to
materialize a huge result set — a cheap DoS. The data layer clamps
them so every caller is protected in one place.
"""
from conftest import FakeSupabaseClient

AUTH = {"Authorization": f"Bearer {FakeSupabaseClient.VALID_TOKEN}"}


def _last_query(db_env, table):
    qs = [q for q in db_env["queries"] if q["table"] == table]
    assert qs, f"no {table} query executed"
    return qs[-1]


def test_violations_limit_is_clamped(full_client, db_env):
    full_client.get("/scan/violations", params={"limit": 10**8, "offset": 0}, headers=AUTH)
    rng = _last_query(db_env, "violations")["range"]
    assert rng is not None
    # offset=0, limit clamped to the cap → end = cap - 1
    assert rng[0] == 0
    assert rng[1] == 199  # cap is 200


def test_violations_offset_is_clamped(full_client, db_env):
    full_client.get("/scan/violations", params={"limit": 50, "offset": 10**8}, headers=AUTH)
    rng = _last_query(db_env, "violations")["range"]
    # offset clamped to 10_000 → end = 10_000 + 50 - 1
    assert rng[0] == 10_000
    assert rng[1] == 10_049


def test_assets_limit_is_clamped(full_client, db_env):
    full_client.get("/upload/assets", params={"limit": 10**8, "offset": 0}, headers=AUTH)
    rng = _last_query(db_env, "assets")["range"]
    assert rng == (0, 199)


def test_reports_limit_is_clamped(full_client, db_env):
    full_client.get("/report/list", params={"limit": 10**8, "offset": 0}, headers=AUTH)
    rng = _last_query(db_env, "reports")["range"]
    assert rng == (0, 199)


def test_normal_pagination_unaffected(full_client, db_env):
    full_client.get("/scan/violations", params={"limit": 25, "offset": 10}, headers=AUTH)
    rng = _last_query(db_env, "violations")["range"]
    assert rng == (10, 34)
