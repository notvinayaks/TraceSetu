"""Durable local worker with transactional claims, leases and bounded recovery."""

from __future__ import annotations
import json
import threading
from sqlalchemy import select, update, or_
from .store import (
    SessionLocal,
    Job,
    Record,
    User,
    now,
    artifact,
    canonical,
    audit,
    patch_record,
    record,
    digest,
    uid,
    WorkerHeartbeat,
)
from .config import settings
from .domain import Snapshot, TraceSpec, Assertion, BridgeProof
from .engine import analyze
from .fixtures import training_snapshot
from .cctp_fixture import bridge_snapshot
from .providers import Acquisition
from .store import read_artifact
from .execution import DurableBudget, execute_plan

stop_event = threading.Event()


def run_job(job_id, claimed_attempt=None):
    with SessionLocal() as db:
        j = db.get(Job, job_id)
        request = dict(j.request)
        tenant = j.tenant
        case_id = j.case_id
        attempt = j.attempts
        if claimed_attempt is not None and claimed_attempt != attempt:
            return
        assertion_records = list(
            db.scalars(
                select(Record).where(
                    Record.tenant == tenant, Record.case_id == case_id, Record.kind == "assertion"
                )
            )
        )
        assertion_mode = "training" if request["mode"] == "fixture" else "operational"
        withdrawn = {
            r.payload["assertion"]["id"] for r in assertion_records if r.payload.get("status") == "withdrawn"
        }
        assertions = [
            Assertion.model_validate(r.payload["assertion"])
            for r in assertion_records
            if r.payload.get("status") == "approved"
            and r.payload.get("mode", "operational") == assertion_mode
        ]
        bridge_records = list(
            db.scalars(
                select(Record).where(
                    Record.tenant == tenant, Record.case_id == case_id, Record.kind == "bridge"
                )
            )
        )
        withdrawn_bridges = {
            r.payload["proof"]["id"] for r in bridge_records if r.payload.get("status") == "withdrawn"
        }
        withdrawn_messages = {
            (r.payload["proof"]["source_chain"], r.payload["proof"]["nonce"].lower()): r.payload["summary"][
                "event"
            ]["senders"][0]
            for r in bridge_records
            if r.payload["status"] == "withdrawn" and r.payload["mode"] == assertion_mode
        }
        bridge_records = [
            r
            for r in bridge_records
            if r.payload["status"] == "approved" and r.payload["mode"] == assertion_mode
        ]
        bridge_proofs = [BridgeProof.model_validate(r.payload["proof"]) for r in bridge_records]
        prior = db.get(Job, request.get("supersedes_job_id")) if request.get("supersedes_job_id") else None
        inherited_raw = list(prior.result.get("raw_evidence", [])) if prior and prior.result else []
        feedback_raw = []
        for r in bridge_records:
            feedback_raw.append(
                {
                    "sha256": r.payload["proof_sha256"],
                    "provider": "Independently reviewed CCTP proof import",
                    "retrieved_at": int(r.created),
                }
            )
        for r in assertion_records:
            if (
                r.payload.get("status") == "approved"
                and r.payload.get("feedback_id")
                and r.payload.get("mode", "operational") == assertion_mode
            ):
                feedback = db.get(Record, r.payload["feedback_id"])
                feedback_raw.append(
                    {
                        "sha256": feedback.payload["envelope_sha256"],
                        "provider": "Reviewed signed service response",
                        "retrieved_at": int(feedback.created),
                    }
                )

    def progress(**values):
        with SessionLocal() as db:
            changed = db.execute(
                update(Job)
                .where(Job.id == job_id, Job.status == "RUNNING", Job.attempts == attempt)
                .values(**values, updated=now(), lease_until=now() + 120)
            )
            db.commit()
            if changed.rowcount != 1:
                raise RuntimeError("Job cancelled or lease ownership changed")

    try:
        spec = TraceSpec.model_validate(request["spec"])
        raw = inherited_raw
        metrics = {
            "attempted_http_requests": 0,
            "successful_http_responses": 0,
            "within_job_cache_hits": 0,
            "request_cap": spec.max_requests,
            "billing_units": "UNKNOWN",
            "scope": "This run only; inherited evidence is not counted as new acquisition",
        }
        execution_result = {}
        if request.get("reassessment_snapshot_sha256"):
            snapshot = Snapshot.model_validate(
                json.loads(read_artifact(request["reassessment_snapshot_sha256"]))
            )
        elif request.get("execution_plan_sha256"):
            plan_hash = request["execution_plan_sha256"]
            plan = json.loads(read_artifact(plan_hash))
            parent = Snapshot.model_validate_json(read_artifact(request["execution_parent_snapshot_sha256"]))
            if (
                plan["snapshot_sha256"] != digest(parent.model_dump())
                or plan["analysis_sha256"] != request["execution_parent_analysis_sha256"]
                or parent.mode != request["mode"]
            ):
                raise ValueError("Execution inputs no longer match the plan")
            parent_analysis = json.loads(read_artifact(request["execution_parent_analysis_sha256"]))
            if parent_analysis["certificate"]["specification"] != spec.model_dump():
                raise ValueError("Execution specification changed")
            budget = DurableBudget(job_id, attempt, plan_hash, plan["budget_requests"])
            snapshot, new_raw, execution, execution_hash = execute_plan(
                parent,
                spec,
                plan,
                budget,
                progress,
                [a for a in parent.assertions if a.id not in withdrawn] + assertions,
            )
            raw += new_raw + [
                {"sha256": h, "provider": label, "retrieved_at": int(now())}
                for h, label in [
                    (plan_hash, "Executed query plan"),
                    (request["execution_parent_snapshot_sha256"], "Preserved parent snapshot"),
                    (request["execution_parent_analysis_sha256"], "Preserved parent analysis"),
                    (execution_hash, "Query execution summary"),
                ]
            ]
            metrics.update(
                attempted_http_requests=execution["reserved_request_slots"],
                successful_http_responses=execution["successful_http_responses"],
                within_job_cache_hits=execution["cache_hits"],
                request_cap=plan["budget_requests"],
                request_count_kind="reserved_attempt_slots",
                scope="Durable request reservations across this execution's recovery attempts; a crash may consume an undispatched slot. Parent evidence is not counted as new acquisition.",
            )
            execution_result = {"execution": execution, "execution_sha256": execution_hash}
        elif request["mode"] == "fixture":
            snapshot = (
                bridge_snapshot() if request.get("fixture_scenario") == "cctp-review" else training_snapshot()
            )
        elif request["mode"] == "imported":
            snapshot = Snapshot.model_validate(json.loads(read_artifact(request["snapshot_sha256"])))
        else:
            acquisition = Acquisition(spec, progress)
            try:
                snapshot = acquisition.collect(assertions, bridge_proofs)
                raw = acquisition.raw
                metrics.update(
                    attempted_http_requests=acquisition.calls,
                    successful_http_responses=len(raw),
                    within_job_cache_hits=acquisition.cache_hits,
                )
            finally:
                acquisition.close()
        raw = list({r["sha256"]: r for r in raw + feedback_raw}.values())
        merged = {a.id: a for a in snapshot.assertions + assertions if a.id not in withdrawn}
        snapshot.assertions = list(merged.values())
        reviewed_messages = {(p.source_chain, p.nonce.lower()) for p in bridge_proofs}
        blocked_messages = set(withdrawn_messages) - reviewed_messages
        original_proof_ids = {p.id for p in snapshot.bridge_proofs}
        snapshot.bridge_proofs = [
            p
            for p in snapshot.bridge_proofs
            if p.id not in withdrawn_bridges
            and (p.source_chain, p.nonce.lower()) not in reviewed_messages
            and (p.source_chain, p.nonce.lower()) not in blocked_messages
        ] + bridge_proofs
        removed_proof_ids = original_proof_ids - {p.id for p in snapshot.bridge_proofs}
        snapshot.events = [
            e for e in snapshot.events if e.kind != "bridge" or e.bridge_proof not in removed_proof_ids
        ]
        blocked_scopes = {(chain, withdrawn_messages[(chain, nonce)]) for chain, nonce in blocked_messages}
        for coverage in snapshot.coverage:
            if (coverage.chain, coverage.address) in blocked_scopes:
                coverage.status = "partial"
                coverage.reason = "A reviewed bridge proof was withdrawn; the protocol transition requires new independent review"
        if snapshot.bridge_proofs:
            snapshot.schema_version = "1.2" if snapshot.reconciliation_gaps else "1.1"
        if withdrawn_bridges:
            snapshot.limitations.append(
                "Withdrawn bridge proofs are excluded: " + ", ".join(sorted(withdrawn_bridges))
            )
        if withdrawn:
            snapshot.limitations.append(
                "Case assertions withdrawn after review are excluded from this analysis: "
                + ", ".join(sorted(withdrawn))
            )
        progress(stage="Computing custody frontier and certificate")
        result = analyze(snapshot, spec)
        snapshot_hash = artifact(canonical(snapshot.model_dump()))
        result_hash = artifact(canonical(result))
        metrics_hash = artifact(canonical(metrics))
        with SessionLocal() as db:
            j = db.get(Job, job_id)
            if j.status != "RUNNING" or j.attempts != attempt:
                return
            status = "COMPLETED_WITH_GAPS" if not result["certificate"]["complete"] else "COMPLETED"
            changed = db.execute(
                update(Job)
                .where(Job.id == job_id, Job.status == "RUNNING", Job.attempts == attempt)
                .values(
                    result={
                        **execution_result,
                        "snapshot_sha256": snapshot_hash,
                        "result_sha256": result_hash,
                        "analysis": result,
                        "raw_evidence": raw,
                        "acquisition_metrics": metrics,
                        "acquisition_metrics_sha256": metrics_hash,
                    },
                    status=status,
                    stage="Analysis available",
                    updated=now(),
                    lease_until=0,
                )
            )
            if changed.rowcount != 1:
                db.rollback()
                return
            user = db.get(User, j.actor_id)
            if user:
                audit(
                    db,
                    user,
                    "analysis.completed",
                    case_id,
                    {"job_id": job_id, "snapshot_sha256": snapshot_hash, "status": status},
                )
            db.commit()
    except Exception as exc:
        with SessionLocal() as db:
            j = db.get(Job, job_id)
            if j.status != "RUNNING" or j.attempts != attempt:
                return
            db.execute(
                update(Job)
                .where(Job.id == job_id, Job.status == "RUNNING", Job.attempts == attempt)
                .values(
                    status="FAILED",
                    stage="Analysis failed",
                    error=f"{type(exc).__name__}: processing failed; no result was substituted.",
                    updated=now(),
                    lease_until=0,
                )
            )
            db.commit()
        import logging

        logging.getLogger("atlas.worker").error("Job %s failed (%s)", job_id, type(exc).__name__)


def claim_one(with_token=False):
    with SessionLocal() as db:
        query = (
            select(Job)
            .where(or_(Job.status == "QUEUED", (Job.status == "RUNNING") & (Job.lease_until < now())))
            .order_by(Job.created)
            .limit(1)
        )
        if db.bind.dialect.name == "postgresql":
            query = query.with_for_update(skip_locked=True)
        candidate = db.scalar(query)
        if not candidate:
            return None
        if candidate.attempts >= 3:
            db.execute(update(Job).where(Job.id == candidate.id, Job.status == candidate.status,
                Job.lease_until == candidate.lease_until, Job.attempts == candidate.attempts).values(
                    status="FAILED", error="Worker recovery limit reached", updated=now()))
            db.commit()
            return None
        old_status = candidate.status
        old_lease = candidate.lease_until
        next_attempt = candidate.attempts + 1
        result = db.execute(
            update(Job)
            .where(Job.id == candidate.id, Job.status == old_status, Job.lease_until == old_lease)
            .values(
                status="RUNNING",
                stage="Acquiring evidence",
                attempts=Job.attempts + 1,
                lease_until=now() + 120,
                updated=now(),
            )
        )
        db.commit()
        return (
            ((candidate.id, next_attempt) if with_token else candidate.id) if result.rowcount == 1 else None
        )


def loop():
    from .observability import emit

    worker_id, started = uid("wrk_"), now()
    heartbeat_stop = threading.Event()

    def heartbeat(status="running"):
        with SessionLocal() as db:
            db.merge(WorkerHeartbeat(id=worker_id, started=started, last_seen=now(), status=status))
            db.commit()

    def pulse():
        while not heartbeat_stop.wait(settings.worker_heartbeat_seconds):
            try:
                heartbeat()
            except Exception as exc:
                emit("worker_heartbeat_failed", component="worker", error_type=type(exc).__name__)

    heartbeat()
    pulse_thread = threading.Thread(target=pulse, name="atlas-heartbeat", daemon=True)
    pulse_thread.start()
    emit("worker_started", component="worker")
    try:
        while not stop_event.is_set():
            try:
                schedule_watches()
                claim = claim_one(with_token=True)
                if claim:
                    run_job(*claim)
            except Exception as exc:
                emit("worker_loop_failed", component="worker", error_type=type(exc).__name__)
            stop_event.wait(0.75)
    finally:
        heartbeat_stop.set()
        pulse_thread.join(timeout=5)
        try:
            heartbeat("stopped")
        except Exception as exc:
            emit("worker_shutdown_heartbeat_failed", component="worker", error_type=type(exc).__name__)
        emit("worker_stopped", component="worker")


def start():
    stop_event.clear()
    thread = threading.Thread(target=loop, name="atlas-worker", daemon=True)
    thread.start()
    return thread


def schedule_watches():
    with SessionLocal() as db:
        query = select(Record).where(Record.kind == "watch")
        if db.bind.dialect.name == "postgresql":
            query = query.with_for_update(skip_locked=True)
        elif db.bind.dialect.name == "sqlite":
            db.connection().exec_driver_sql("BEGIN IMMEDIATE")
        for watch in db.scalars(query):
            p = watch.payload
            if not p.get("enabled"):
                continue
            case = db.get(Record, watch.case_id)
            actor = db.get(User, p["created_by"])
            if not case or case.payload["status"] == "Closed" or not actor or not actor.active:
                continue
            if actor.role != "admin" and actor.id not in case.payload.get("members", []):
                continue
            last = db.get(Job, p["last_job_id"]) if p.get("last_job_id") else None
            if last and last.status in ("QUEUED", "RUNNING"):
                continue
            if last and last.result and p.get("baseline_job_id") != last.id:
                a = last.result["analysis"]
                fingerprint = digest(
                    {
                        "candidates": [
                            (c["entity"], c["address"], c["status"], c["hops"]) for c in a["candidates"]
                        ],
                        "risk": a["risk"],
                        "frontiers": [(f["address"], f["reason"]) for f in a["frontiers"]],
                    }
                )
                if p.get("baseline") and fingerprint != p["baseline"]:
                    record(
                        db,
                        "alert",
                        watch.tenant,
                        {
                            "watch_id": watch.id,
                            "job_id": last.id,
                            "message": "Custody candidates, risk assertions, or acquisition coverage changed. Review the new evidence.",
                            "status": "unread",
                        },
                        watch.case_id,
                    )
                patch_record(watch, {"baseline": fingerprint, "baseline_job_id": last.id})
                p = watch.payload
            if p["next_run"] > now():
                continue
            spec = dict(p["spec"])
            spec["end"] = int(now())
            if spec["start"] >= spec["end"]:
                continue
            payload = {"mode": "live", "spec": spec}
            job_id = uid("job_")
            idem = f"watch:{watch.id}:{int(p['next_run'])}"
            claimed = db.execute(
                update(Record)
                .where(Record.id == watch.id, Record.version == watch.version)
                .values(
                    payload={**p, "last_job_id": job_id, "next_run": now() + p["interval_minutes"] * 60},
                    version=Record.version + 1,
                    updated=now(),
                )
            )
            if claimed.rowcount != 1:
                continue
            db.add(
                Job(
                    id=job_id,
                    tenant=watch.tenant,
                    case_id=watch.case_id,
                    actor_id=actor.id,
                    idempotency=idem,
                    input_hash=digest(payload),
                    request=payload,
                )
            )
            audit(db, actor, "watch.analysis_queued", watch.case_id, {"watch_id": watch.id, "job_id": job_id})
        db.commit()
