import io
import json
import zipfile

import httpx
import pytest

from test_workflow import setup_case, run_training
from vasp_app.domain import Coverage, Snapshot, TraceSpec
from vasp_app.engine import analyze
from vasp_app.execution import DurableBudget, ExecutionStopped, execute_plan, merge_scope
from vasp_app.fixtures import training_snapshot
from vasp_app.providers import Acquisition, BudgetExhausted
from vasp_app.reports import verify_bundle
from vasp_app.store import SessionLocal, Job, Record, User, read_artifact, digest, artifact, canonical
from vasp_app.worker import claim_one, run_job


def prepared(clients, budget=4):
    c = setup_case(clients)
    i = clients["investigator"]
    parent, _ = run_training(i, c["id"])
    r = i.post(f"/api/analyses/{parent['id']}/query-plan", json={"budget_requests": budget})
    assert r.status_code == 200, r.text
    plan = r.json()
    url = f"/api/analyses/{parent['id']}/query-plans/{plan['id']}/execute"
    body = {"version": plan["version"], "plan_sha256": plan["sha256"]}
    return c, parent, plan, url, body


def queued(clients, budget=4):
    c, parent, plan, url, body = prepared(clients, budget)
    r = clients["investigator"].post(url, json=body, headers={"Idempotency-Key": "execute-plan-test"})
    assert r.status_code == 202, r.text
    return c, parent, plan, r.json()


def test_training_execution_preserves_parent_bundle_and_reassessment(clients):
    c, parent, plan, j = queued(clients)
    run_job(*claim_one(with_token=True))
    i = clients["investigator"]
    result = i.get("/api/analyses/" + j["id"]).json()
    assert result["status"] == "COMPLETED_WITH_GAPS", result
    execution = result["result"]["execution"]
    assert execution["reserved_request_slots"] == execution["successful_http_responses"] == 0
    assert execution["automatic_recursive_expansion"] is False
    assert execution["parent_snapshot_sha256"] == parent["result"]["snapshot_sha256"]
    assert any("fixture-expanded-deposit" in x["path"] for x in result["result"]["analysis"]["candidates"])
    assert i.get("/api/analyses/" + parent["id"]).json()["result"] == parent["result"]
    bundle = i.get("/api/analyses/" + j["id"] + "/bundle.zip")
    assert bundle.status_code == 200, bundle.text
    assert verify_bundle(bundle.content)["replay"] == "matched"
    with zipfile.ZipFile(io.BytesIO(bundle.content)) as archive:
        assert canonical(plan["plan"]) in [archive.read(n) for n in archive.namelist()]
        assert read_artifact(parent["result"]["snapshot_sha256"]) in [
            archive.read(n) for n in archive.namelist()
        ]
    again = i.post(
        "/api/analyses/" + j["id"] + "/reassess", headers={"Idempotency-Key": "reassess-executed-plan"}
    )
    assert again.status_code == 202, again.text
    assert not any(k.startswith("execution_") for k in again.json()["request"])
    run_job(*claim_one(with_token=True))
    reassessed = i.get("/api/analyses/" + again.json()["id"]).json()
    assert "execution" not in reassessed["result"]
    assert reassessed["result"]["acquisition_metrics"]["attempted_http_requests"] == 0
    assert reassessed["result"]["analysis"]["candidates"] == result["result"]["analysis"]["candidates"]


def test_plan_execution_binding_permissions_and_idempotency(clients):
    c, parent, plan, url, body = prepared(clients)
    i = clients["investigator"]
    headers = {"Idempotency-Key": "bound-execution-test"}
    assert clients["reviewer"].post(url, json=body, headers=headers).status_code == 403
    for name in ("outsider", "unassigned"):
        assert clients[name].post(url, json=body, headers=headers).status_code == 404
    assert i.post(url, json={**body, "version": 99}, headers=headers).status_code == 409
    assert i.post(url, json={**body, "plan_sha256": "0" * 64}, headers=headers).status_code == 409
    first = i.post(url, json=body, headers=headers)
    assert first.status_code == 202, first.text
    assert i.post(url, json=body, headers=headers).json()["id"] == first.json()["id"]
    assert i.post(url, json=body, headers={"Idempotency-Key": "fresh-key-same-plan"}).status_code == 409
    assert i.post(url, json={**body, "version": body["version"] + 1}, headers=headers).status_code == 409


@pytest.mark.parametrize(
    "change", ["closed", "other_analysis", "stale_policy", "altered_plan", "no_selection"]
)
def test_plan_rejects_invalid_execution_inputs(clients, change):
    c, parent, plan, url, body = prepared(clients, 1 if change == "no_selection" else 4)
    i = clients["investigator"]
    with SessionLocal() as db:
        if change == "closed":
            r = db.get(Record, c["id"])
            r.payload = {**r.payload, "status": "Closed"}
        if change in ("stale_policy", "altered_plan"):
            r = db.get(Record, plan["id"])
            p = {**r.payload["plan"], "policy_version": "unsupported"}
            r.payload = {**r.payload, "plan": p}
            if change == "stale_policy":
                h = artifact(canonical(p))
                r.payload = {**r.payload, "sha256": h}
                body["plan_sha256"] = h
        db.commit()
    if change == "other_analysis":
        other, _ = run_training(i, c["id"], "separate-analysis-for-plan")
        # Different specification produces a different result hash even over the same fixture.
        with SessionLocal() as db:
            r = db.get(Job, other["id"])
            payload = json.loads(json.dumps(r.result))
            payload["analysis"]["certificate"]["specification"]["max_hops"] = 2
            payload["result_sha256"] = artifact(canonical(payload["analysis"]))
            r.result = payload
            db.commit()
        url = url.replace(parent["id"], other["id"])
    response = i.post(url, json=body, headers={"Idempotency-Key": "reject-invalid-plan"})
    assert response.status_code == (422 if change == "no_selection" else 409), response.text


def acquisition_for(spec, handler):
    a = Acquisition(spec)
    a.client.close()
    a.client = httpx.Client(transport=httpx.MockTransport(handler))
    return a


def test_durable_budget_reuses_saved_responses_and_counts_lost_slots(clients, monkeypatch):
    _, _, plan, job = queued(clients, 4)
    job_id, attempt = claim_one(with_token=True)
    budget = DurableBudget(job_id, attempt, plan["sha256"], 4)
    monkeypatch.setattr("vasp_app.providers.time.sleep", lambda _: None)
    sent = []

    def handler(request):
        sent.append(request)
        return httpx.Response(200, json={"observed": len(sent)})

    spec = TraceSpec.model_validate(job["request"]["spec"]).model_copy(update={"max_requests": 4})
    a = acquisition_for(spec, handler)
    budget.attach(a)
    first, sha = a.fetch("Mock provider", "https://provider.invalid/page/1")
    assert first == {"observed": 1}
    a.close()
    budget.reserve()  # Simulated crash before dispatch/response persistence.
    with SessionLocal() as db:
        j = db.get(Job, job_id)
        j.lease_until = 0
        db.commit()
    recovered_id, recovered_attempt = claim_one(with_token=True)
    assert recovered_attempt == 2
    with pytest.raises(ExecutionStopped):
        budget.reserve()
    recovered = DurableBudget(recovered_id, recovered_attempt, plan["sha256"], 4)
    a = acquisition_for(spec, handler)
    recovered.attach(a)
    assert a.fetch("Mock provider", "https://provider.invalid/page/1") == (first, sha)
    assert len(sent) == 1 and a.calls == 2 and a.cache_hits == 1
    a.fetch("Mock provider", "https://provider.invalid/page/2")
    a.fetch("Mock provider", "https://provider.invalid/page/3")
    with pytest.raises(BudgetExhausted):
        a.fetch("Mock provider", "https://provider.invalid/page/4")
    assert len(sent) == 3 and a.calls == 4
    a.close()


@pytest.mark.parametrize("change", ["cancel", "membership", "inactive", "role", "closed"])
def test_permission_or_case_change_prevents_further_spend(clients, change, monkeypatch):
    c, _, plan, job = queued(clients)
    job_id, attempt = claim_one(with_token=True)
    budget = DurableBudget(job_id, attempt, plan["sha256"], 4)
    sent = []
    spec = TraceSpec.model_validate(job["request"]["spec"])
    a = acquisition_for(spec, lambda req: sent.append(req) or httpx.Response(200, json=[]))
    budget.attach(a)
    monkeypatch.setattr("vasp_app.providers.time.sleep", lambda _: None)
    with SessionLocal() as db:
        case, actor, j = db.get(Record, c["id"]), db.get(User, "investigator"), db.get(Job, job_id)
        if change == "cancel":
            j.status = "CANCELLED"
        elif change == "membership":
            case.payload = {**case.payload, "members": []}
        elif change == "inactive":
            actor.active = False
        elif change == "role":
            actor.role = "reviewer"
        else:
            case.payload = {**case.payload, "status": "Closed"}
        db.commit()
    with pytest.raises(ExecutionStopped):
        a.fetch("Mock provider", "https://provider.invalid/page/1")
    assert not sent
    a.close()


def test_corrupted_checkpoint_and_cached_artifact_fail_closed(clients):
    _, _, plan, _ = queued(clients)
    job_id, attempt = claim_one(with_token=True)
    budget = DurableBudget(job_id, attempt, plan["sha256"], 4)
    with pytest.raises(ExecutionStopped):
        DurableBudget(job_id, attempt, "0" * 64, 4)
    with SessionLocal() as db:
        r = db.get(Record, budget.record_id)
        r.payload = {**r.payload, "cache": {"synthetic-key": "0" * 64}}
        db.commit()
    corrupt = DurableBudget(job_id, attempt, plan["sha256"], 4)
    a = Acquisition(TraceSpec(chain="ethereum", address="fixture:suspect", start=1750000000, end=1750001000))
    try:
        with pytest.raises(FileNotFoundError):
            corrupt.attach(a)
    finally:
        a.close()


def test_conflicting_events_remain_withheld_on_reacquisition_and_duplicate_pages():
    s = training_snapshot()
    first = s.events[0]
    original = s.model_copy(deep=True)
    changed = first.model_copy(update={"amount": str(int(first.amount) + 1)})

    def complete():
        return Coverage(
            chain=first.chain, address=first.senders[0], status="complete", reason="Synthetic complete page"
        )

    changes = merge_scope(s, first.chain, first.senders[0], [changed], complete())
    assert changes["conflicting_event_ids"] == [first.id]
    assert s.schema_version == "1.2" and s.reconciliation_gaps
    assert not any(e.id == first.id for e in s.events)
    assert read_artifact(changes["conflict_evidence"][0]["sha256"]) == canonical(
        {"prior": first.model_dump(), "received": changed.model_dump()}
    )
    merge_scope(s, first.chain, first.senders[0], [first], complete())
    assert not any(e.id == first.id for e in s.events)
    spec = TraceSpec(chain=first.chain, address=first.senders[0], start=s.window_start, end=s.window_end)
    result = analyze(Snapshot.model_validate(s.model_dump()), spec)
    assert any(f["reason"] == "provider_event_conflict" for f in result["frontiers"])
    assert all(first.id not in c["path"] for c in result["candidates"])
    # Contradictions within a newly acquired page are also held.
    original.events = []
    merge_scope(original, first.chain, first.senders[0], [first, changed], complete())
    assert not original.events and original.reconciliation_gaps


def test_partial_history_preserves_old_observation_but_complete_absence_is_explicit():
    s = training_snapshot()
    first = s.events[0]
    c = Coverage(chain=first.chain, address=first.senders[0], status="partial", reason="Page limit")
    merge_scope(s, first.chain, first.senders[0], [], c)
    assert any(e.id == first.id for e in s.events)
    c.status = "complete"
    changes = merge_scope(s, first.chain, first.senders[0], [], c)
    assert first.id in changes["missing_prior_event_ids"]
    assert c.status == "partial" and "canonicality" in c.reason


def test_selected_live_scope_uses_transport_and_retains_partial_evidence(clients, monkeypatch):
    _, _, plan, job = queued(clients)
    job_id, attempt = claim_one(with_token=True)
    # Independently exercise the same executor over valid Bitcoin addresses with mocked Esplora pages.
    seed = "1BoatSLRHtKNngkdXEeobR76b53LETtpyT"
    target = "1BitcoinEaterAddressDontSendf59kuE"
    snapshot = Snapshot(
        mode="live",
        origin="Mocked transport only",
        collected_at=1750001000,
        window_start=1750000000,
        window_end=1750001000,
        coverage=[Coverage(chain="bitcoin", address=seed, status="partial", reason="not fetched")],
    )
    spec = TraceSpec(chain="bitcoin", address=seed, start=snapshot.window_start, end=snapshot.window_end)
    execute = {
        **plan["plan"],
        "budget_requests": 1,
        "actions": [
            {
                "chain": "bitcoin",
                "address": seed,
                "status": "selected_estimate",
                "action": "reacquire_history",
            }
        ],
    }
    budget = DurableBudget(job_id, attempt, digest(execute), 1)
    sent = []

    def handler(request):
        sent.append(request)
        return httpx.Response(
            200,
            json=[
                {
                    "txid": str(n).zfill(64),
                    "status": {"confirmed": True, "block_time": 1750000010},
                    "vin": [{"txid": "f" * 64, "vout": 0, "prevout": {"scriptpubkey_address": seed}}],
                    "vout": [{"scriptpubkey_address": target, "value": n + 1}],
                }
                for n in range(25)
            ],
        )

    monkeypatch.setattr("vasp_app.providers.time.sleep", lambda _: None)
    output, raw, summary, _ = execute_plan(
        snapshot,
        spec,
        execute,
        budget,
        lambda **_: None,
        [],
        lambda spec, progress: acquisition_for(spec, handler),
    )
    assert len(sent) == summary["reserved_request_slots"] == 1
    assert len(output.events) == 25 and output.coverage[0].status == "partial"
    assert len(raw) == 1 and read_artifact(raw[0]["sha256"])
    assert not snapshot.events  # Parent unchanged.
    assert "fixture:" not in canonical(output.model_dump()).decode()


def test_new_custody_boundary_skips_selected_scope(clients):
    _, parent, plan, job = queued(clients)
    job_id, attempt = claim_one(with_token=True)
    budget = DurableBudget(job_id, attempt, plan["sha256"], 4)
    snap = Snapshot.model_validate_json(read_artifact(parent["result"]["snapshot_sha256"]))
    label = snap.assertions[0].model_copy(update={"address": "fixture:unresolved"})
    _, _, summary, _ = execute_plan(
        snap,
        TraceSpec.model_validate(job["request"]["spec"]),
        plan["plan"],
        budget,
        lambda **_: None,
        [label],
    )
    assert summary["actions"][0]["status"] == "skipped_new_boundary"
    assert summary["reserved_request_slots"] == 0
