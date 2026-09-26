import copy
import pytest
from vasp_app.domain import Snapshot, Transfer, Coverage
from vasp_app.live_validation import ValidationCheck, ValidationPlan, assess
from vasp_app.providers import Acquisition
from vasp_app.store import artifact, canonical
from vasp_app.worker import claim_one, run_job
from test_workflow import setup_case

SEED = "13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94"
DESTINATION = "1BoatSLRHtKNngkdXEeobR76b53LETtpyT"
SPEC = {"chain": "bitcoin", "address": SEED, "start": 1750000000, "end": 1750001000,
        "max_requests": 3, "max_hops": 1}


def test_validation_plan_has_bounded_budget_and_safe_names():
    with pytest.raises(ValueError):
        ValidationCheck(name="../escape", spec=SPEC)
    with pytest.raises(ValueError, match="unique"):
        ValidationPlan(checks=[ValidationCheck(name="same", spec=SPEC)] * 2)
    with pytest.raises(ValueError, match="200 total"):
        ValidationPlan(checks=[ValidationCheck(name="one", spec={**SPEC, "max_requests": 200}),
                               ValidationCheck(name="two", spec=SPEC)])


def test_validation_never_accepts_fixture_or_imported_job():
    check = ValidationCheck(name="test", spec=SPEC)
    for mode in ("fixture", "imported"):
        with pytest.raises(ValueError, match="rejects"):
            assess(check, {"request": {"mode": mode}})
    failed = assess(check, {"id": "job-failed", "status": "FAILED", "request": {"mode": "live"}})
    assert failed["status"] == "failed"
    assert not failed["full_chain_validated"] and not failed["ownership_validated"]


@pytest.mark.parametrize("empty", [False, True])
def test_validation_binds_bundle_scope_job_and_exact_reference(clients, monkeypatch, empty):
    # Explicitly mocked transport for validator regression; not recorded as a real live check.
    raw = artifact(canonical({"synthetic_unit_test": True}))
    def mocked_collect(self, *_):
        self.calls = 1
        self.raw = [{"sha256": raw, "provider": "Synthetic unit-test transport", "retrieved_at": 1750000000}]
        return Snapshot(mode="live", origin="Mocked transport; unit test only", collected_at=1750001000,
            window_start=1750000000, window_end=1750001000,
            events=[] if empty else [Transfer(id="test-output", chain="bitcoin", txid="0" * 64,
                senders=[SEED], recipient=DESTINATION, asset="bitcoin:native", amount="1501", decimals=8,
                timestamp=1750000010, kind="utxo", evidence=[raw], output_index=0)],
            coverage=[Coverage(chain="bitcoin", address=SEED, status="partial", reason="Synthetic test scope", evidence=[raw])])
    monkeypatch.setattr(Acquisition, "collect", mocked_collect)
    client = clients["investigator"]
    case = setup_case(clients)
    created = client.post("/api/cases/" + case["id"] + "/analyses",
        json={"mode": "live", "spec": SPEC}, headers={"Idempotency-Key": "validation-test"})
    assert created.status_code == 202
    run_job(*claim_one(with_token=True))
    job = client.get("/api/analyses/" + created.json()["id"]).json()
    snapshot = client.get("/api/analyses/" + job["id"] + "/snapshot").json()
    bundle = client.get("/api/analyses/" + job["id"] + "/bundle.zip").content
    check = ValidationCheck(name="test", spec=SPEC, expected_transfers=[{
        "txid": "0" * 64, "recipient": DESTINATION, "asset": "bitcoin:native", "amount": "1501",
        "reference": "Explicitly synthetic test reference"}])
    report = assess(check, job, snapshot, bundle)
    assert report["status"] == ("live_no_transfers" if empty else "bounded_transfer_sample_verified")
    assert not report["ownership_validated"] and not report["independent_ground_truth_validated"]
    altered = copy.deepcopy(job)
    altered["id"] = "different-job"
    with pytest.raises(ValueError, match="disagree"):
        assess(check, altered, snapshot, bundle)
    altered = copy.deepcopy(job)
    altered["result"]["acquisition_metrics"]["successful_http_responses"] = 999
    with pytest.raises(ValueError, match="accounting"):
        assess(check, altered, snapshot, bundle)
    if not empty:
        check.expected_transfers[0].amount = "1502"
        assert assess(check, job, snapshot, bundle)["status"] == "reference_mismatch"
