import base64
import io
import zipfile
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from vasp_app.store import SessionLocal, Job, now, canonical
from vasp_app.worker import claim_one, run_job
from vasp_app.reports import verify_bundle


def setup_case(clients):
    i = clients["investigator"]
    r = i.post(
        "/api/cases",
        json={"title": "Training investigation", "reference": "TEST-001", "members": ["reviewer"]},
    )
    assert r.status_code == 201, r.text
    return r.json()


def run_training(client, case_id, key="test-idempotency-1"):
    body = {
        "mode": "fixture",
        "spec": {"chain": "ethereum", "address": "fixture:suspect", "start": 1750000000, "end": 1750001000},
    }
    r = client.post(f"/api/cases/{case_id}/analyses", json=body, headers={"Idempotency-Key": key})
    assert r.status_code == 202, r.text
    job_id = claim_one()
    assert job_id == r.json()["id"]
    run_job(job_id)
    result = client.get("/api/analyses/" + job_id)
    assert result.json()["status"] == "COMPLETED_WITH_GAPS", result.text
    return result.json(), body


def test_case_boundary_and_csrf(clients):
    c = setup_case(clients)
    for name in ["outsider", "unassigned"]:
        assert clients[name].get("/api/cases/" + c["id"]).status_code == 404
        assert clients[name].get("/api/cases").json() == []
    assert clients["reviewer"].get("/api/cases/" + c["id"]).status_code == 200
    assert (
        clients["reviewer"].post("/api/cases", json={"title": "Denied", "reference": "bad"}).status_code
        == 403
    )
    client = clients["investigator"]
    token = client.headers.pop("X-CSRF-Token")
    assert client.post("/api/cases", json={"title": "Denied", "reference": "bad"}).status_code == 403
    client.headers["X-CSRF-Token"] = token
    assert (
        client.post(
            "/api/cases",
            json={"title": "Denied", "reference": "bad"},
            headers={"Origin": "https://evil.invalid"},
        ).status_code
        == 403
    )


def test_job_idempotency_and_access(clients):
    c = setup_case(clients)
    i = clients["investigator"]
    j, body = run_training(i, c["id"])
    plan = i.post("/api/analyses/" + j["id"] + "/query-plan", json={"budget_requests": 4})
    assert plan.status_code == 200, plan.text
    assert plan.json()["plan"]["execution"] == "ADVISORY_ONLY"
    assert plan.json()["plan"]["selected_estimated_requests"] <= 4
    assert (
        clients["outsider"]
        .post("/api/analyses/" + j["id"] + "/query-plan", json={"budget_requests": 4})
        .status_code
        == 404
    )
    second = i.post(
        "/api/cases/" + c["id"] + "/analyses", json=body, headers={"Idempotency-Key": "test-idempotency-1"}
    )
    assert second.json()["id"] == j["id"]
    body["spec"]["max_hops"] = 4
    assert (
        i.post(
            "/api/cases/" + c["id"] + "/analyses",
            json=body,
            headers={"Idempotency-Key": "test-idempotency-1"},
        ).status_code
        == 409
    )
    assert clients["outsider"].get("/api/analyses/" + j["id"]).status_code == 404
    assert clients["unassigned"].get("/api/analyses/" + j["id"] + "/bundle.zip").status_code == 404


def test_report_bundle_replay_and_tamper(clients):
    c = setup_case(clients)
    i = clients["investigator"]
    j, _ = run_training(i, c["id"])
    pdf = i.get("/api/analyses/" + j["id"] + "/report.pdf")
    assert pdf.status_code == 200
    assert pdf.content.startswith(b"%PDF-")
    bundle = i.get("/api/analyses/" + j["id"] + "/bundle.zip")
    assert bundle.status_code == 200, bundle.text
    result = verify_bundle(bundle.content)
    assert result["integrity"] == "valid"
    assert result["replay"] == "matched"
    assert result["identity_trusted"] is False
    trusted = verify_bundle(bundle.content, result["signer_sha256"])
    assert trusted["identity_trusted"] is True
    tampered = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(bundle.content)) as src, zipfile.ZipFile(tampered, "w") as dst:
        for name in src.namelist():
            dst.writestr(name, b"changed" if name == "snapshot.json" else src.read(name))
    import pytest

    with pytest.raises(ValueError):
        verify_bundle(tampered.getvalue())
    response = i.post(
        "/api/evidence/verify", files={"file": ("bundle.zip", bundle.content, "application/zip")}
    )
    assert response.status_code == 200, response.text
    assert (
        i.post(
            "/api/evidence/verify", files={"file": ("bad.zip", tampered.getvalue(), "application/zip")}
        ).status_code
        == 422
    )


def test_dual_review_request_and_signed_response(clients):
    c = setup_case(clients)
    i = clients["investigator"]
    reviewer = clients["reviewer"]
    j, _ = run_training(i, c["id"])
    key = Ed25519PrivateKey.generate()
    public = base64.b64encode(
        key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    ).decode()
    result = i.post(
        "/api/recipients",
        json={
            "entity": "Example Exchange Alpha",
            "mode": "training",
            "jurisdiction": "Synthetic test jurisdiction",
            "channel": "Local test only",
            "verification_source": "Synthetic identity verified by test harness; not a real VASP",
            "expires_at": int(now() + 86400),
            "signing_public_key": public,
        },
    )
    assert result.status_code == 201, result.text
    recipient = result.json()
    decision = {
        "version": recipient["version"],
        "decision": "approve",
        "rationale": "Independent synthetic test review",
    }
    assert i.post("/api/records/" + recipient["id"] + "/review", json=decision).status_code == 403
    assert reviewer.post("/api/records/" + recipient["id"] + "/review", json=decision).status_code == 200
    request = i.post(
        "/api/cases/" + c["id"] + "/requests",
        json={
            "job_id": j["id"],
            "candidate_index": 0,
            "recipient_id": recipient["id"],
            "type": "disclosure",
            "legal_basis": "Synthetic workflow test only",
            "scope": "Synthetic request: no real action or external dispatch",
        },
    )
    assert request.status_code == 201, request.text
    request = request.json()
    assert i.get("/api/requests/" + request["id"] + "/export").status_code == 409
    approved = reviewer.post(
        "/api/records/" + request["id"] + "/review",
        json={
            "version": request["version"],
            "decision": "approve",
            "rationale": "Independent test-only review of exact payload",
        },
    )
    assert approved.status_code == 200, approved.text
    exported = i.get("/api/requests/" + request["id"] + "/export")
    assert exported.status_code == 200
    assert exported.json()["delivery_status"] == "NOT_SENT"
    payload = {
        "request_id": request["id"],
        "request_sha256": request["body_sha256"],
        "finding": "Synthetic confirmation only",
    }
    signed = {
        "request_id": request["id"],
        "payload": payload,
        "signature": base64.b64encode(key.sign(canonical(payload))).decode(),
    }
    response = i.post("/api/cases/" + c["id"] + "/feedback", json=signed)
    assert response.status_code == 201, response.text
    assert response.json()["signature_verified"]
    assert response.json()["status"] == "pending"
    assert i.post("/api/cases/" + c["id"] + "/feedback", json=signed).status_code == 409
    response_record = response.json()
    # Reviewing a signed unstructured finding must not silently manufacture a label.
    reviewed = reviewer.post(
        "/api/records/" + response_record["id"] + "/review",
        json={
            "version": response_record["version"],
            "decision": "approve",
            "rationale": "Review unstructured findings without attribution promotion",
        },
    )
    assert reviewed.status_code == 200, reviewed.text
    assert "promoted_assertion_id" not in reviewed.json()
    signed["payload"]["finding"] = "tampered"
    assert i.post("/api/cases/" + c["id"] + "/feedback", json=signed).status_code == 422

    candidate = j["result"]["analysis"]["candidates"][0]
    payload = {
        "schema": "atlas.service-response.v1",
        "request_id": request["id"],
        "request_sha256": request["body_sha256"],
        "attestation": {
            "chain": candidate["chain"],
            "address": candidate["address"],
            "entity": candidate["entity"],
            "category": "exchange",
            "role": "deposit",
            "valid_from": 1750000000,
            "valid_to": 1750001000,
        },
    }

    def signed_payload(value):
        return {
            "request_id": request["id"],
            "payload": value,
            "signature": base64.b64encode(key.sign(canonical(value))).decode(),
        }

    wrong_scope = {
        **payload,
        "attestation": {**payload["attestation"], "address": "fixture:different-wallet"},
    }
    assert i.post("/api/cases/" + c["id"] + "/feedback", json=signed_payload(wrong_scope)).status_code == 422
    response = i.post("/api/cases/" + c["id"] + "/feedback", json=signed_payload(payload))
    assert response.status_code == 201, response.text
    f = response.json()
    decision = {
        "version": f["version"],
        "decision": "approve",
        "rationale": "Independently verified scoped synthetic service attestation",
    }
    assert i.post("/api/records/" + f["id"] + "/review", json=decision).status_code == 403
    reviewed = reviewer.post("/api/records/" + f["id"] + "/review", json=decision)
    assert reviewed.status_code == 200, reviewed.text
    promoted_id = reviewed.json()["promoted_assertion_id"]
    assert reviewer.post("/api/records/" + f["id"] + "/review", json=decision).status_code == 409
    records = i.get("/api/cases/" + c["id"] + "/records").json()
    promoted = next(r for r in records if r["id"] == promoted_id)
    assert promoted["mode"] == "training"
    assert promoted["assertion"]["source_family"].startswith("service-key:")

    reassessed = i.post(
        "/api/analyses/" + j["id"] + "/reassess", headers={"Idempotency-Key": "reassessment-with-feedback"}
    )
    assert reassessed.status_code == 202, reassessed.text
    run_job(claim_one())
    later = i.get("/api/analyses/" + reassessed.json()["id"]).json()
    assert later["result"]["snapshot_sha256"] != j["result"]["snapshot_sha256"]
    assert any(
        a["id"] == promoted["assertion"]["id"]
        for a in later["result"]["analysis"]["candidates"][0]["assertions"]
    )
    bundle = i.get("/api/analyses/" + later["id"] + "/bundle.zip")
    assert verify_bundle(bundle.content)["replay"] == "matched"
    with zipfile.ZipFile(io.BytesIO(bundle.content)) as z:
        assert any(f["envelope_sha256"] in name for name in z.namelist())
    later_request = i.post(
        "/api/cases/" + c["id"] + "/requests",
        json={
            "job_id": later["id"],
            "candidate_index": 0,
            "recipient_id": recipient["id"],
            "type": "disclosure",
            "legal_basis": "Synthetic workflow authority only",
            "scope": "Synthetic request before assertion withdrawal",
        },
    )
    assert later_request.status_code == 201, later_request.text
    lr = later_request.json()
    assert (
        reviewer.post(
            "/api/records/" + lr["id"] + "/review",
            json={
                "version": lr["version"],
                "decision": "approve",
                "rationale": "Independent review before synthetic correction",
            },
        ).status_code
        == 200
    )
    assert i.get("/api/requests/" + lr["id"] + "/export").status_code == 200

    withdrawal = i.post(
        "/api/assertions/" + promoted_id + "/withdrawal",
        json={
            "version": promoted["version"],
            "rationale": "Synthetic provider correction: supporting claim was withdrawn",
        },
    )
    assert withdrawal.status_code == 201, withdrawal.text
    w = withdrawal.json()
    assert i.get("/api/analyses/" + later["id"]).json()["evidence_changes"] == []
    decision = {
        "version": w["version"],
        "decision": "approve",
        "rationale": "Independent review of signed correction evidence",
    }
    assert i.post("/api/records/" + w["id"] + "/review", json=decision).status_code == 403
    withdrawn = reviewer.post("/api/records/" + w["id"] + "/review", json=decision)
    assert withdrawn.status_code == 200, withdrawn.text
    assert later["id"] in withdrawn.json()["affected_jobs"]
    stale = i.get("/api/analyses/" + later["id"]).json()
    assert stale["evidence_changes"]
    assert stale["result"]["snapshot_sha256"] == later["result"]["snapshot_sha256"]
    assert i.get("/api/requests/" + lr["id"] + "/export").status_code == 409
    assert i.get("/api/requests/" + request["id"] + "/export").status_code == 200
    assert i.get("/api/analyses/" + later["id"] + "/report.pdf").status_code == 409
    assert i.get("/api/analyses/" + later["id"] + "/snapshot").status_code == 200
    assert (
        i.post(
            "/api/cases/" + c["id"] + "/requests",
            json={
                "job_id": later["id"],
                "candidate_index": 0,
                "recipient_id": recipient["id"],
                "type": "disclosure",
                "legal_basis": "Synthetic basis only",
                "scope": "Synthetic stale evidence request",
            },
        ).status_code
        == 409
    )
    next_job = i.post(
        "/api/analyses/" + later["id"] + "/reassess",
        headers={"Idempotency-Key": "reassessment-after-withdrawal"},
    )
    assert next_job.status_code == 202, next_job.text
    run_job(claim_one())
    refreshed = i.get("/api/analyses/" + next_job.json()["id"]).json()
    assert not refreshed["evidence_changes"]
    assert all(
        a["id"] != promoted["assertion"]["id"]
        for n in refreshed["result"]["analysis"]["graph"]["nodes"]
        for a in n["labels"]
    )


def test_assertion_review_and_case_version_conflict(clients):
    c = setup_case(clients)
    i = clients["investigator"]
    r = i.post(
        "/api/cases/" + c["id"] + "/assertions",
        json={
            "assertion": {
                "id": "ignored",
                "chain": "ethereum",
                "address": "0x" + "1" * 40,
                "entity": "Test custodian",
                "category": "custodian",
                "source_family": "independent test",
                "source": "Authorised synthetic test",
                "evidence": ["test-source"],
            },
            "rationale": "Test label requiring a second reviewer",
        },
    )
    assert r.status_code == 201, r.text
    r = r.json()
    assert r["assertion"]["grade"] == "hypothesis"
    approved = clients["reviewer"].post(
        "/api/records/" + r["id"] + "/review",
        json={
            "version": r["version"],
            "decision": "approve",
            "rationale": "Reviewed supporting source for test",
        },
    )
    assert approved.json()["assertion"]["grade"] == "reviewed"
    assert (
        i.patch("/api/cases/" + c["id"], json={"version": c["version"], "status": "Closed"}).status_code
        == 200
    )
    assert (
        i.patch("/api/cases/" + c["id"], json={"version": c["version"], "status": "Open"}).status_code == 409
    )


def test_live_missing_key_never_substitutes_fixture(clients):
    c = setup_case(clients)
    i = clients["investigator"]
    r = i.post(
        "/api/cases/" + c["id"] + "/analyses",
        json={
            "mode": "live",
            "spec": {"chain": "ethereum", "address": "0x" + "1" * 40, "start": 1750000000, "end": 1750001000},
        },
        headers={"Idempotency-Key": "missing-key-test"},
    )
    assert r.status_code == 202
    job_id = claim_one()
    run_job(job_id)
    result = i.get("/api/analyses/" + job_id).json()["result"]["analysis"]
    assert result["mode"] == "live"
    assert result["candidates"] == []
    assert result["graph"]["events"] == []
    assert any("not configured" in x for x in result["limitations"])


def test_worker_claim_and_lease_recovery(clients):
    c = setup_case(clients)
    i = clients["investigator"]
    r = i.post(
        "/api/cases/" + c["id"] + "/analyses",
        json={
            "mode": "fixture",
            "spec": {
                "chain": "ethereum",
                "address": "fixture:suspect",
                "start": 1750000000,
                "end": 1750001000,
            },
        },
        headers={"Idempotency-Key": "lease-test-123"},
    )
    job_id = claim_one()
    assert job_id == r.json()["id"]
    assert claim_one() is None
    with SessionLocal() as db:
        job = db.get(Job, job_id)
        job.lease_until = 0
        db.commit()
    assert claim_one() == job_id
    run_job(job_id, claimed_attempt=1)
    stale = i.get("/api/analyses/" + job_id).json()
    assert stale["status"] == "RUNNING" and stale["result"] is None
    run_job(job_id)
    assert i.get("/api/analyses/" + job_id).json()["attempts"] == 2


def test_training_analysis_cannot_use_operational_recipient(clients):
    c = setup_case(clients)
    i = clients["investigator"]
    j, _ = run_training(i, c["id"])
    r = i.post(
        "/api/recipients",
        json={
            "mode": "operational",
            "entity": "Example Exchange Alpha",
            "jurisdiction": "Synthetic test",
            "channel": "Test only",
            "verification_source": "Synthetic test of the mode separation guard",
            "expires_at": int(now() + 86400),
        },
    ).json()
    assert (
        clients["reviewer"]
        .post(
            "/api/records/" + r["id"] + "/review",
            json={
                "version": r["version"],
                "decision": "approve",
                "rationale": "Synthetic test approval to exercise the boundary",
            },
        )
        .status_code
        == 200
    )
    response = i.post(
        "/api/cases/" + c["id"] + "/requests",
        json={
            "job_id": j["id"],
            "candidate_index": 0,
            "recipient_id": r["id"],
            "type": "disclosure",
            "legal_basis": "Synthetic test only",
            "scope": "Synthetic guard test; no real action",
        },
    )
    assert response.status_code == 409
    assert "Recipient purpose" in response.json()["detail"]


def test_modified_database_result_cannot_be_published_as_evidence(clients):
    c = setup_case(clients)
    i = clients["investigator"]
    j, _ = run_training(i, c["id"])
    import copy

    with SessionLocal() as db:
        stored = db.get(Job, j["id"])
        payload = copy.deepcopy(stored.result)
        payload["analysis"]["candidates"][0]["entity"] = "Tampered entity"
        stored.result = payload
        db.commit()
    assert i.get("/api/analyses/" + j["id"]).status_code == 409
    assert i.get("/api/analyses/" + j["id"] + "/report.pdf").status_code == 409
    assert i.get("/api/analyses/" + j["id"] + "/bundle.zip").status_code == 409
