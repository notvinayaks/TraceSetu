"""Bounded live-connector checks through the authenticated application workflow.

Successful acquisition is not independent ownership or whole-chain validation.
"""
import hashlib
import json
import time
import uuid
from pathlib import Path
from pydantic import Field, model_validator
from .domain import Contract, TraceSpec
from .addresses import validate_address
from .reports import verify_bundle


class ExpectedTransfer(Contract):
    txid: str = Field(min_length=1, max_length=160)
    recipient: str = Field(min_length=1, max_length=160)
    asset: str = Field(min_length=1, max_length=160)
    amount: str = Field(pattern=r"^\d{1,80}$")
    reference: str = Field(min_length=1, max_length=500)


class ValidationCheck(Contract):
    name: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{0,59}$")
    spec: TraceSpec
    expected_transfers: list[ExpectedTransfer] = Field(default_factory=list, max_length=30)

    @model_validator(mode="after")
    def scope(self):
        self.spec.address = validate_address(self.spec.chain, self.spec.address)
        return self


class ValidationPlan(Contract):
    schema_version: str = "tracesetu.live-validation-plan.v1"
    checks: list[ValidationCheck] = Field(min_length=1, max_length=12)

    @model_validator(mode="after")
    def bounded(self):
        if self.schema_version != "tracesetu.live-validation-plan.v1":
            raise ValueError("Unknown validation plan schema")
        if len({c.name for c in self.checks}) != len(self.checks):
            raise ValueError("Validation check names must be unique")
        if sum(c.spec.max_requests for c in self.checks) > 200:
            raise ValueError("A validation run is limited to 200 total configured HTTP requests")
        return self


def assess(check, job, snapshot=None, bundle=None, trusted_fingerprint=None):
    result = job.get("result") or {}
    metrics = result.get("acquisition_metrics") or {}
    manifest = {
        "chain": check.spec.chain, "check": check.name, "spec": check.spec.model_dump(),
        "job_id": job.get("id"), "job_status": job.get("status"),
        "checked_at": int(time.time()), "status": "failed",
        "successful_http_responses": metrics.get("successful_http_responses", 0),
        "attempted_http_requests": metrics.get("attempted_http_requests", 0),
        "full_chain_validated": False, "ownership_validated": False,
        "independent_ground_truth_validated": False,
        "scope": "This bounded acquisition and replay only. Reference provenance requires independent review.",
    }
    if job.get("request", {}).get("mode") != "live":
        raise ValueError("Live validation rejects fixture or imported analyses")
    if snapshot is None or bundle is None or not result:
        manifest["reason"] = "Live job produced no verifiable evidence bundle"
        return manifest
    if snapshot.get("mode") != "live":
        raise ValueError("Live validation rejects a non-live snapshot")
    verification = verify_bundle(bundle, trusted_fingerprint=trusted_fingerprint)
    if verification["mode"] != "live":
        raise ValueError("Bundle is not live evidence")
    # The bundle verifier checks itself; additionally bind it to the requested job and API snapshot.
    import io
    import zipfile
    with zipfile.ZipFile(io.BytesIO(bundle)) as archive:
        signed_manifest = json.loads(archive.read("manifest.json"))
        signed_snapshot = json.loads(archive.read("snapshot.json"))
        signed_analysis = json.loads(archive.read("analysis.json"))
        signed_metrics = json.loads(archive.read("acquisition-metrics.json"))
    if signed_manifest["job_id"] != job["id"] or signed_snapshot != snapshot:
        raise ValueError("Bundle and API snapshot/job disagree")
    if signed_analysis != result.get("analysis") or signed_metrics != metrics:
        raise ValueError("Bundle and API analysis/accounting disagree")
    if signed_analysis["certificate"]["specification"] != check.spec.model_dump():
        raise ValueError("Evidence scope differs from validation plan")
    events = snapshot.get("events", [])
    expected = [{"reference": item.reference, "matched": any(
        all(event.get(key) == getattr(item, key) for key in ("txid", "recipient", "asset", "amount"))
        for event in events)} for item in check.expected_transfers]
    manifest.update(
        bundle_sha256=hashlib.sha256(bundle).hexdigest(), verification=verification,
        event_count=len(events), raw_evidence=result.get("raw_evidence", []),
        coverage=snapshot.get("coverage", []), limitations=snapshot.get("limitations", []),
        reference_checks=expected,
    )
    if manifest["successful_http_responses"] == 0:
        manifest.update(status="unavailable", reason="No successful provider response in this acquisition")
    elif not events:
        manifest.update(status="live_no_transfers", reason="Provider response retained; no transfer sample to validate")
    elif expected and not all(item["matched"] for item in expected):
        manifest.update(status="reference_mismatch", reason="One or more supplied expected transfers were not found")
    else:
        manifest.update(status="bounded_transfer_sample_verified",
            reason="Live transfer evidence, exact supplied references where present, and signed replay checked")
    return manifest


def run_check(client, check, output, *, timeout_seconds=240, trusted_fingerprint=None):
    folder = Path(output) / check.name
    folder.mkdir(parents=True, exist_ok=False)
    case = client.post("/api/cases", json={"title": "Live connector validation · " + check.spec.chain,
        "reference": "VALIDATION-" + uuid.uuid4().hex[:12], "members": [],
        "description": "Public read-only connector validation. No suspicion or ownership is asserted."})
    case.raise_for_status()
    response = client.post("/api/cases/" + case.json()["id"] + "/analyses",
        json={"mode": "live", "spec": check.spec.model_dump()}, headers={"Idempotency-Key": uuid.uuid4().hex})
    response.raise_for_status()
    job_id = response.json()["id"]
    deadline = time.monotonic() + timeout_seconds
    while True:
        response = client.get("/api/analyses/" + job_id)
        response.raise_for_status()
        job = response.json()
        if job["status"] not in ("QUEUED", "RUNNING"):
            break
        if time.monotonic() >= deadline:
            manifest = {"check": check.name, "chain": check.spec.chain, "job_id": job_id,
                "status": "timed_out", "job_may_still_be_running": True,
                "ownership_validated": False, "full_chain_validated": False}
            (folder / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            return manifest
        time.sleep(1)
    (folder / "job.json").write_text(json.dumps(job, indent=2), encoding="utf-8")
    snapshot, bundle = None, None
    if job.get("result"):
        response = client.get("/api/analyses/" + job_id + "/snapshot")
        response.raise_for_status()
        snapshot = response.json()
        (folder / "snapshot.json").write_bytes(response.content)
        response = client.get("/api/analyses/" + job_id + "/bundle.zip")
        response.raise_for_status()
        bundle = response.content
        (folder / "evidence.zip").write_bytes(bundle)
    manifest = assess(check, job, snapshot, bundle, trusted_fingerprint)
    (folder / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest
