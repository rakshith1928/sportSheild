"""Severity unification: one shared threshold function, persisted on insert.

Before this fix the violations.severity column was never written, so the
frontend's high/medium/low filter always returned 0 rows, and severity was
computed ad-hoc in three places with different thresholds.
"""

import pytest

import services.database as db


def test_severity_boundaries():
    # > 0.9 high; > 0.75 medium; else low (matches existing alert logic)
    assert db.severity_from_similarity(0.91) == "high"
    assert db.severity_from_similarity(0.9) == "medium"
    assert db.severity_from_similarity(0.76) == "medium"
    assert db.severity_from_similarity(0.75) == "low"
    assert db.severity_from_similarity(0.4) == "low"
    assert db.severity_from_similarity(None) == "low"


def test_insert_violation_writes_severity(db_env):
    db.insert_violation(
        {
            "image_url": "https://x.example/i.jpg",
            "page_url": "https://pirate.example/p",
            "title": "Stolen poster",
            "clip_similarity": 0.95,
            "phash_distance": 2,
            "is_likely_copy": True,
        },
        scan_id="scan-1",
    )
    ins = [
        q["insert"]
        for q in db_env["queries"]
        if q["table"] == "violations" and q.get("insert")
    ]
    assert ins, "violation insert was recorded"
    row = ins[-1]
    assert row["severity"] == "high"
    assert row["clip_similarity"] == 0.95


def test_insert_violation_medium_and_low(db_env):
    for sim, expected in [(0.8, "medium"), (0.5, "low")]:
        db.insert_violation(
            {
                "image_url": f"https://x.example/{sim}.jpg",
                "page_url": "https://pirate.example/p",
                "clip_similarity": sim,
            },
        )
    ins = [
        q["insert"]["severity"]
        for q in db_env["queries"]
        if q["table"] == "violations" and q.get("insert")
    ]
    assert ins == ["medium", "low"]


def test_get_violations_severity_filter_applied(db_env):
    db_env["rows"]["violations"] = []
    db.get_violations(severity="high", user_id="user-a")
    q = [q for q in db_env["queries"] if q["table"] == "violations"][-1]
    assert ("severity", "high") in q["filters"]


def test_get_recent_alerts_use_shared_thresholds(db_env):
    rows = [
        {
            "id": 1,
            "title": "t1",
            "page_url": "https://p1",
            "detected_at": "2026-01-01T00:00:00Z",
            "clip_similarity": 0.95,
            "assets": {"owner": "user-a"},
        },
        {
            "id": 2,
            "title": "t2",
            "page_url": "https://p2",
            "detected_at": "2026-01-02T00:00:00Z",
            "clip_similarity": 0.62,
            "assets": {"owner": "user-a"},
        },
    ]
    db_env["rows"]["violations"] = rows
    alerts = db.get_recent_alerts(user_id="user-a")
    assert alerts[0]["severity"] == db.severity_from_similarity(0.95)
    assert alerts[1]["severity"] == db.severity_from_similarity(0.62)
