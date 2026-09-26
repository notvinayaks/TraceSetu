import pytest
from vasp_app.cctp_fixture import synthetic_proof, bridge_snapshot, SEED, START
from vasp_app.cctp import verify_bridge, RECEIVED_TOPIC
from vasp_app.domain import TraceSpec, Snapshot
from vasp_app.engine import analyze, challenge


@pytest.mark.parametrize("source", ["ethereum", "polygon"])
@pytest.mark.parametrize("fee", [0, 10000])
def test_signed_protocol_links_both_directions_and_exact_net_amount(source, fee):
    p = synthetic_proof(source, fee)
    link = verify_bridge(p)
    assert link["event"].chain == source
    assert link["event"].amount == str(1000000 - fee)
    assert link["event"].senders == [SEED]
    assert link["destination_timestamp"] == START + 30
    assert link["destination_position"] == [200, 0, 1]
    assert len(link["attestation_signers"]) == 1


@pytest.mark.parametrize(
    "mutation",
    [
        "source_hash",
        "block_hash",
        "removed",
        "wrong_mint",
        "wrong_emitter",
        "wrong_nonce",
        "signature",
        "key",
        "ambiguous_mint",
        "duplicate_position",
        "malformed_log",
        "malformed_message",
        "malformed_key",
        "ambiguous_source",
        "wrong_receipt_body",
        "expired",
    ],
)
def test_invalid_or_ambiguous_evidence_cannot_become_a_bridge(mutation):
    p = synthetic_proof()
    if mutation == "source_hash":
        p.iris_response["sourceTxHash"] = p.destination_txhash
    elif mutation == "block_hash":
        p.destination_block["hash"] = p.source_block["hash"]
    elif mutation == "removed":
        p.destination_receipt["logs"][0]["removed"] = True
    elif mutation == "wrong_mint":
        p.destination_receipt["logs"][0]["data"] = "0x" + "00" * 32
    elif mutation == "wrong_emitter":
        p.destination_receipt["logs"][1]["address"] = SEED
    elif mutation == "wrong_nonce":
        p.nonce = "0x" + "11" * 32
    elif mutation == "signature":
        p.iris_response["messages"][0]["attestation"] = "0x" + "00" * 65
    elif mutation == "key":
        p.public_keys["publicKeys"] = []
    elif mutation == "ambiguous_mint":
        logs = p.destination_receipt["logs"]
        logs[1]["logIndex"] = "0x2"
        logs.insert(1, {**logs[0], "logIndex": "0x1"})
    elif mutation == "duplicate_position":
        p.destination_receipt["logs"].append(p.destination_receipt["logs"][0].copy())
    elif mutation == "malformed_log":
        p.source_receipt["logs"].append(None)
    elif mutation == "malformed_message":
        p.iris_response["messages"] = [None]
    elif mutation == "malformed_key":
        p.public_keys["publicKeys"] = [None]
    elif mutation == "ambiguous_source":
        p.source_receipt["logs"].append({**p.source_receipt["logs"][1], "logIndex": "0x2"})
    elif mutation == "wrong_receipt_body":
        log = next(row for row in p.destination_receipt["logs"] if row["topics"][0] == RECEIVED_TOPIC)
        log["data"] = log["data"][:-2] + "ff"
    elif mutation == "expired":
        p.destination_block["number"] = "0x3e8"
        p.destination_receipt["blockNumber"] = "0x3e8"
        for log in p.destination_receipt["logs"]:
            log["blockNumber"] = "0x3e8"
    with pytest.raises(ValueError):
        verify_bridge(p)


def test_review_gate_arrival_causality_and_provenance_challenge():
    s = bridge_snapshot()
    q = TraceSpec(chain="ethereum", address=SEED, start=START, end=START + 1000)
    assert not analyze(s, q)["candidates"]  # Synthetic key still needs explicit training review.
    s.bridge_proofs[0].grade = "reviewed"
    r = analyze(s, q)
    assert r["candidates"][0]["hops"] == 2
    assert r["candidates"][0]["amount_bounds"]["upper"] == "900000"
    assert r["graph"]["events"][0]["bridge_details"]["fee_amount"] == "10000"
    assert challenge(s, q, ["synthetic-cctp-v2"])["removed_candidates"]
    s.events[0].timestamp = START + 20  # After burn, before mint: cannot be a causal outflow.
    assert not analyze(s, q)["candidates"]
    s.events[0].timestamp = START + 30
    s.events[0].position = [200, 0, 0]
    assert not analyze(s, q)["candidates"]
    s.events[0].position = [200, 0, 2]
    assert analyze(s, q)["candidates"]
    q.end = START + 25
    assert any(f["reason"] == "bridge_arrival_outside_window" for f in analyze(s, q)["frontiers"])


def test_old_snapshot_serialization_omits_empty_extension():
    from vasp_app.fixtures import training_snapshot

    s = training_snapshot()
    assert "bridge_proofs" not in s.model_dump()
    assert Snapshot.model_validate(s.model_dump()).model_dump() == s.model_dump()


def test_previous_engine_bundles_still_replay():
    from types import SimpleNamespace
    from vasp_app.fixtures import training_snapshot
    from vasp_app.legacy.engine_v03 import analyze as historical_analyze
    from vasp_app.store import artifact, canonical
    from vasp_app.reports import make_bundle, verify_bundle

    s = training_snapshot()
    q = TraceSpec(chain="ethereum", address="fixture:suspect", start=s.window_start, end=s.window_end)
    result = historical_analyze(s, q)
    assert result["certificate"]["engine_version"] == "0.3.0"
    job = SimpleNamespace(
        id="old-engine-fixture",
        result={"analysis": result, "snapshot_sha256": artifact(canonical(s.model_dump()))},
    )
    bundle, _ = make_bundle({"reference": "OLD-ENGINE", "title": "Historical replay regression"}, job, [])
    assert verify_bundle(bundle)["replay"] == "matched"


def test_duplicate_protocol_message_proofs_never_choose_first_silently():
    s = bridge_snapshot()
    s.bridge_proofs[0].grade = "reviewed"
    duplicate = s.bridge_proofs[0].model_copy(deep=True)
    duplicate.id = "conflicting-package"
    s.bridge_proofs.append(duplicate)
    result = analyze(s, TraceSpec(chain="ethereum", address=SEED, start=START, end=START + 1000))
    assert not result["candidates"]
    assert sum(f["reason"] == "bridge_proof_unresolved" for f in result["frontiers"]) == 2


def test_bridge_review_withdrawal_reassessment_and_signed_replay(clients):
    from vasp_app.worker import claim_one, run_job
    from vasp_app.reports import verify_bundle

    i, reviewer = clients["investigator"], clients["reviewer"]
    case = i.post(
        "/api/cases",
        json={
            "title": "Synthetic cross-chain review",
            "reference": "CCTP-TEST",
            "members": ["reviewer", "admin"],
        },
    ).json()
    body = {
        "mode": "fixture",
        "fixture_scenario": "cctp-review",
        "spec": {"chain": "ethereum", "address": SEED, "start": START, "end": START + 1000},
    }

    def finish(response):
        assert response.status_code == 202, response.text
        job_id = claim_one()
        assert response.json()["id"] == job_id
        run_job(job_id)
        result = i.get("/api/analyses/" + job_id).json()
        assert result["status"].startswith("COMPLETED"), result
        return result

    j = finish(
        i.post(
            f"/api/cases/{case['id']}/analyses", json=body, headers={"Idempotency-Key": "cctp-first-analysis"}
        )
    )
    assert not j["result"]["analysis"]["candidates"]
    proposal = {
        "proof": synthetic_proof().model_dump(),
        "mode": "training",
        "rationale": "Explicit synthetic training proof; the local key is not Circle's key",
    }
    denied = clients["outsider"].post(f"/api/cases/{case['id']}/bridges", json=proposal)
    assert denied.status_code == 404
    r = i.post(f"/api/cases/{case['id']}/bridges", json=proposal)
    assert r.status_code == 201, r.text
    proof = r.json()
    assert proof["proof"]["grade"] == "hypothesis"
    decision = {
        "version": proof["version"],
        "decision": "approve",
        "rationale": "Reviewed the synthetic wire bytes and test key provenance for training only",
    }
    assert clients["admin"].post(f"/api/records/{proof['id']}/review", json=decision).status_code == 200
    # Duplicate live proposal cannot silently replace this evidence.
    assert i.post(f"/api/cases/{case['id']}/bridges", json=proposal).status_code == 409
    j2 = finish(
        i.post(f"/api/analyses/{j['id']}/reassess", headers={"Idempotency-Key": "cctp-reviewed-reassess"})
    )
    assert j2["result"]["analysis"]["candidates"][0]["hops"] == 2
    assert j2["result"]["acquisition_metrics"]["attempted_http_requests"] == 0
    bundle = i.get(f"/api/analyses/{j2['id']}/bundle.zip")
    assert bundle.status_code == 200, bundle.text[:100] if bundle.status_code != 200 else ""
    assert verify_bundle(bundle.content)["replay"] == "matched"
    challenge_result = i.post(f"/api/analyses/{j2['id']}/challenge", json={"excluded": ["synthetic-cctp-v2"]})
    assert challenge_result.status_code == 200
    assert challenge_result.json()["removed_candidates"]
    withdrawal = i.post(
        f"/api/evidence/{proof['id']}/withdrawal",
        json={
            "version": 2,
            "rationale": "Withdraw the synthetic bridge to test dependent evidence invalidation",
        },
    )
    assert withdrawal.status_code == 201, withdrawal.text
    w = withdrawal.json()
    approved = reviewer.post(
        f"/api/records/{w['id']}/review",
        json={
            "version": w["version"],
            "decision": "approve",
            "rationale": "Independent training review confirms withdrawal",
        },
    )
    assert approved.status_code == 200, approved.text
    stale = i.get(f"/api/analyses/{j2['id']}").json()
    assert stale["evidence_changes"]
    assert i.get(f"/api/analyses/{j2['id']}/bundle.zip").status_code == 409
    j3 = finish(
        i.post(f"/api/analyses/{j2['id']}/reassess", headers={"Idempotency-Key": "cctp-withdrawn-reassess"})
    )
    assert not j3["result"]["analysis"]["candidates"]
    assert i.get(f"/api/analyses/{j2['id']}/snapshot").status_code == 200
    fresh = finish(
        i.post(
            f"/api/cases/{case['id']}/analyses",
            json=body,
            headers={"Idempotency-Key": "cctp-withdrawal-new-acquisition"},
        )
    )
    assert not fresh["result"]["analysis"]["candidates"]
    assert fresh["result"]["analysis"]["certificate"]["complete"] is False
    assert (
        i.post(f"/api/cases/{case['id']}/bridges", json={**proposal, "mode": "operational"}).status_code
        == 422
    )
    new_proposal = clients["admin"].post(f"/api/cases/{case['id']}/bridges", json=proposal).json()
    new_decision = {**decision, "version": new_proposal["version"]}
    assert (
        clients["admin"].post(f"/api/records/{new_proposal['id']}/review", json=new_decision).status_code
        == 403
    )
    assert reviewer.post(f"/api/records/{new_proposal['id']}/review", json=new_decision).status_code == 200
    restored = finish(
        i.post(
            f"/api/analyses/{fresh['id']}/reassess",
            headers={"Idempotency-Key": "cctp-new-independent-approval"},
        )
    )
    assert restored["result"]["analysis"]["candidates"]
    assert not restored["evidence_changes"]


@pytest.mark.parametrize("forward", [True, False])
def test_read_only_acquisition_correlates_and_expands_destination(monkeypatch, forward):
    import httpx
    from vasp_app.providers import Acquisition
    from vasp_app.config import settings
    from vasp_app.cctp import REGISTRY
    from vasp_app.cctp_fixture import RECIPIENT

    p = synthetic_proof()
    if not forward:
        p.iris_response["messages"][0].pop("forwardTxHash")
    monkeypatch.setattr(settings, "etherscan_api_key", "synthetic-test-key")
    monkeypatch.setattr(settings, "cctp_enabled", True)
    monkeypatch.setattr("vasp_app.providers.time.sleep", lambda _: None)
    requests = []

    def handler(request):
        assert request.method == "GET"
        requests.append(request)
        params = request.url.params
        if request.url.path == "/v2/messages/0":
            payload = p.iris_response
        elif request.url.path == "/v2/publicKeys":
            payload = p.public_keys
        elif params.get("action") == "getLogs":
            assert params["topic2"] == p.nonce and params["topic0_2_opr"] == "and"
            payload = {"status": "1", "result": [p.destination_receipt["logs"][1]]}
        elif params.get("module") == "proxy":
            dest = params["chainid"] == "137"
            payload = {
                "result": (p.destination_receipt if dest else p.source_receipt)
                if params["action"] == "eth_getTransactionReceipt"
                else (p.destination_block if dest else p.source_block)
            }
        else:
            rows = []
            if params.get("address") == SEED and params.get("action") == "tokentx":
                rows = [
                    {
                        "from": SEED,
                        "to": "0x" + "00" * 20,
                        "hash": p.source_txhash,
                        "contractAddress": REGISTRY["ethereum"]["usdc"],
                        "tokenDecimal": "6",
                        "value": "1000000",
                        "timeStamp": str(START + 10),
                    }
                ]
            payload = {"status": "1", "result": rows}
        return httpx.Response(200, json=payload)

    def acquire(budget):
        a = Acquisition(
            TraceSpec(chain="ethereum", address=SEED, start=START, end=START + 1000, max_requests=budget)
        )
        a.client.close()
        a.client = httpx.Client(transport=httpx.MockTransport(handler))
        try:
            return a.collect([]), a.calls
        finally:
            a.close()

    s, calls = acquire(30)
    assert calls <= 30
    assert len(s.bridge_proofs) == 1
    assert s.bridge_proofs[0].grade == "provider"
    assert any(c.chain == "polygon" and c.address == RECIPIENT for c in s.coverage)
    assert any(e.kind == "bridge" for e in s.events)
    assert any(
        e["bridge_details"]
        for e in analyze(s, TraceSpec(chain="ethereum", address=SEED, start=START, end=START + 1000))[
            "graph"
        ]["events"]
        if e["kind"] == "bridge"
    )
    partial, calls = acquire(7)
    assert calls == 7
    assert not partial.bridge_proofs
    assert (
        partial.events
    )  # The already reconciled source transfer survives a later bridge timeout/budget stop.
    assert any("CCTP" in limit for limit in partial.limitations)
