"""Data-flow tests for the scan pipeline (audit B4).

The web scanner returns its result under the key ``total_scanned``, but
the scan router read ``urls_scanned`` when persisting the scan record —
so every completed scan was stored with total_scanned=0.
"""
from routers import scan as scan_mod


AUTH = {"Authorization": "Bearer valid-token"}


def test_scan_persists_total_scanned_from_scanner_result(
    full_client, db_env, fake_asset_lookup, monkeypatch
):
    fake_asset_lookup["asset-own"] = {
        "asset_id": "asset-own",
        "owner": "user-a",
        "sport": "cricket",
        "team": "Mumbai Indians",
        "description": "official poster",
    }

    async def fake_scan(**kwargs):
        return {
            "violations": [],
            "violations_found": 0,
            "total_scanned": 7,
        }

    recorded = []

    def fake_update_scan_status(**kwargs):
        recorded.append(kwargs)
        return None

    monkeypatch.setattr(scan_mod, "scan_google_for_asset", fake_scan)
    monkeypatch.setattr(scan_mod, "update_scan_status", fake_update_scan_status)

    resp = full_client.post("/scan/asset-own", headers=AUTH)
    assert resp.status_code == 200, resp.text

    completed = [r for r in recorded if r.get("status") == "completed"]
    assert completed, "update_scan_status was never called with status=completed"
    # The scanner says 7 URLs were scanned; the stored record must agree.
    assert completed[0]["total_scanned"] == 7
