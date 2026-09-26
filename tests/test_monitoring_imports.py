from vasp_app.store import SessionLocal, Job, Record
from vasp_app.worker import schedule_watches, claim_one, run_job

ADDRESS = "0x" + "1" * 40
DEST = "0x" + "2" * 40


def new_case(clients):
    r = clients["investigator"].post(
        "/api/cases",
        json={"title": "Import and monitor test", "reference": "TEST-IMPORT", "members": ["reviewer"]},
    )
    assert r.status_code == 201
    return r.json()["id"]


def test_snapshot_import_downgrades_claims_and_is_case_scoped(clients):
    i = clients["investigator"]
    case_id = new_case(clients)
    snapshot = {
        "mode": "imported",
        "origin": "Explicit synthetic test using valid address syntax",
        "collected_at": 200,
        "window_start": 100,
        "window_end": 200,
        "events": [
            {
                "id": "event-1",
                "chain": "ethereum",
                "txid": "synthetic-tx",
                "senders": [ADDRESS],
                "recipient": DEST,
                "asset": "ethereum:native",
                "amount": "100",
                "decimals": 18,
                "timestamp": 110,
                "evidence": ["synthetic-source"],
            }
        ],
        "assertions": [
            {
                "id": "untrusted-label",
                "chain": "ethereum",
                "address": DEST,
                "entity": "Synthetic service",
                "category": "exchange",
                "grade": "reviewed",
                "source_family": "fixture",
                "source": "Synthetic test source",
                "evidence": ["fixture"],
            }
        ],
        "coverage": [
            {"chain": "ethereum", "address": ADDRESS, "status": "complete", "reason": "Synthetic test only"}
        ],
    }
    imported = i.post(
        "/api/cases/" + case_id + "/snapshots",
        json={"snapshot": snapshot, "provenance": "Synthetic test input; no real investigation data"},
    )
    assert imported.status_code == 201, imported.text
    data = {
        "mode": "imported",
        "snapshot_id": imported.json()["id"],
        "spec": {"chain": "ethereum", "address": ADDRESS, "start": 100, "end": 200},
    }
    job = i.post(
        "/api/cases/" + case_id + "/analyses", json=data, headers={"Idempotency-Key": "import-job-123"}
    )
    assert job.status_code == 202, job.text
    job_id = claim_one()
    run_job(job_id)
    result = i.get("/api/analyses/" + job_id).json()["result"]["analysis"]
    assert result["mode"] == "imported"
    assert result["candidates"][0]["status"] == "hypothesis"
    assert result["certificate"]["nearest_evidenced_hops"] is None
    case_two = new_case(clients)
    assert (
        i.post(
            "/api/cases/" + case_two + "/analyses",
            json=data,
            headers={"Idempotency-Key": "different-case-123"},
        ).status_code
        == 422
    )
    snapshot["events"][0]["senders"] = ["fixture:unreal"]
    assert (
        i.post(
            "/api/cases/" + case_id + "/snapshots",
            json={"snapshot": snapshot, "provenance": "Synthetic test invalid address"},
        ).status_code
        == 422
    )


def test_watch_scheduling_is_durable_and_deduplicated(clients):
    i = clients["investigator"]
    case_id = new_case(clients)
    created = i.post(
        "/api/cases/" + case_id + "/watches",
        json={
            "spec": {"chain": "ethereum", "address": ADDRESS, "start": 100, "end": 200, "max_requests": 1},
            "interval_minutes": 15,
        },
    )
    assert created.status_code == 201, created.text
    watch_id = created.json()["id"]
    schedule_watches()
    schedule_watches()
    with SessionLocal() as db:
        watch = db.get(Record, watch_id)
        assert watch.payload["last_job_id"]
        first_id = watch.payload["last_job_id"]
        assert len(list(db.query(Job).all())) == 1
        j = db.get(Job, first_id)
        j.status = "COMPLETED_WITH_GAPS"
        j.result = {"analysis": {"candidates": [], "risk": {"classification": "unassessed"}, "frontiers": []}}
        db.commit()
    schedule_watches()
    with SessionLocal() as db:
        watch = db.get(Record, watch_id)
        assert watch.payload["baseline"]
        p = dict(watch.payload)
        p["next_run"] = 0
        watch.payload = p
        db.commit()
    schedule_watches()
    with SessionLocal() as db:
        watch = db.get(Record, watch_id)
        second_id = watch.payload["last_job_id"]
        assert second_id != first_id
        j = db.get(Job, second_id)
        j.status = "COMPLETED_WITH_GAPS"
        j.result = {
            "analysis": {
                "candidates": [],
                "risk": {"classification": "unassessed"},
                "frontiers": [{"address": ADDRESS, "reason": "incomplete_coverage"}],
            }
        }
        db.commit()
    schedule_watches()
    schedule_watches()
    with SessionLocal() as db:
        alerts = list(db.query(Record).filter(Record.kind == "alert").all())
        assert len(alerts) == 1
    assert i.post("/api/watches/" + watch_id + "/toggle").json()["enabled"] is False


def test_closed_case_watch_does_not_schedule(clients):
    i = clients["investigator"]
    case_id = new_case(clients)
    assert (
        i.post(
            "/api/cases/" + case_id + "/watches",
            json={
                "spec": {"chain": "ethereum", "address": ADDRESS, "start": 100, "end": 200},
                "interval_minutes": 15,
            },
        ).status_code
        == 201
    )
    c = i.get("/api/cases/" + case_id).json()
    assert (
        i.patch("/api/cases/" + case_id, json={"version": c["version"], "status": "Closed"}).status_code
        == 200
    )
    schedule_watches()
    with SessionLocal() as db:
        assert db.query(Job).count() == 0
