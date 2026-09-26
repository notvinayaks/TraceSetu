"""Explicit plan execution with lease-fenced, durable per-job request reservations."""

import copy
import json
from sqlalchemy import update
from .store import SessionLocal, Job, Record, User, now, canonical, artifact, read_artifact, digest
from .domain import Snapshot, Coverage, Transfer, ReconciliationGap
from .providers import Acquisition, ProviderError, BudgetExhausted


class ExecutionStopped(RuntimeError):
    pass


class DurableBudget:
    """Each reserved slot survives a process loss, even if no response was saved."""

    def __init__(self, job_id, attempt, plan_sha256, cap):
        self.job_id, self.attempt = job_id, attempt
        self.plan_sha256, self.cap = plan_sha256, cap
        self.record_id = "qcp_" + job_id.removeprefix("job_")
        self.state = self.change(lambda state: None)

    def change(self, mutate):
        with SessionLocal() as db:
            job = db.get(Job, self.job_id)
            if not job:
                raise ExecutionStopped("Execution job is unavailable")
            actor, case = db.get(User, job.actor_id), db.get(Record, job.case_id)
            if (
                not actor
                or not actor.active
                or actor.role not in ("admin", "investigator")
                or not case
                or case.payload["status"] == "Closed"
                or actor.tenant != job.tenant
                or (actor.role != "admin" and actor.id not in case.payload.get("members", []))
            ):
                raise ExecutionStopped("Case or acquisition permission changed")
            fenced = db.execute(
                update(Job)
                .where(Job.id == job.id, Job.status == "RUNNING", Job.attempts == self.attempt)
                .values(lease_until=now() + 120, updated=now())
            )
            if fenced.rowcount != 1:
                raise ExecutionStopped("Job cancelled or lease ownership changed")
            checkpoint = db.get(Record, self.record_id)
            if checkpoint is None:
                checkpoint = Record(
                    id=self.record_id,
                    kind="query_checkpoint",
                    tenant=job.tenant,
                    case_id=job.case_id,
                    payload={
                        "plan_sha256": self.plan_sha256,
                        "cap": self.cap,
                        "calls": 0,
                        "cache_hits": 0,
                        "cache": {},
                        "raw": [],
                    },
                )
                db.add(checkpoint)
            state = copy.deepcopy(checkpoint.payload)
            if (
                state["plan_sha256"] != self.plan_sha256
                or state["cap"] != self.cap
                or not 0 <= state["calls"] <= self.cap
            ):
                raise ExecutionStopped("Execution checkpoint does not match the approved scope")
            mutate(state)
            checkpoint.payload = state
            if checkpoint.version is not None:
                checkpoint.version += 1
            checkpoint.updated = now()
            db.commit()
            self.state = state
            return copy.deepcopy(state)

    def reserve(self):
        def increment(state):
            if state["calls"] >= self.cap:
                raise BudgetExhausted("Durable execution request budget exhausted")
            state["calls"] += 1

        return self.change(increment)["calls"]

    def cache_hit(self):
        def increment(state):
            state["cache_hits"] += 1

        return self.change(increment)["cache_hits"]

    def response(self, cache_key, sha256, metadata):
        def save(state):
            if cache_key:
                state["cache"][cache_key] = sha256
            state["raw"].append(metadata)

        self.change(save)

    def attach(self, acquisition):
        acquisition.durable_budget = self
        acquisition.calls, acquisition.cache_hits = self.state["calls"], self.state["cache_hits"]
        acquisition.raw = list(self.state["raw"])
        acquisition.cache = {key: (json.loads(read_artifact(h)), h) for key, h in self.state["cache"].items()}


def merge_scope(snapshot, chain, address, events, coverage):
    """Contradictory event identities become gaps, not a silently chosen flow."""
    old = {e.id: e for e in snapshot.events}
    fresh = {}
    conflicts = set()
    gaps = {(g.chain, g.address, g.event_id): g for g in snapshot.reconciliation_gaps}
    held_ids = {g.event_id for g in gaps.values()}
    conflict_raw = []
    for event in events:
        event_id = event.id
        previous = fresh.get(event_id) or old.get(event_id)
        if previous and previous.model_dump(exclude={"evidence"}) != event.model_dump(exclude={"evidence"}):
            conflicts.add(event_id)
            h = artifact(canonical({"prior": previous.model_dump(), "received": event.model_dump()}))
            conflict_raw.append(
                {"sha256": h, "provider": "Conflicting normalized observations", "retrieved_at": int(now())}
            )
            for observation in (previous, event):
                for sender in observation.senders:
                    k = (observation.chain, sender, event_id)
                    evidence = list(dict.fromkeys((gaps[k].evidence if k in gaps else []) + [h]))
                    gaps[k] = ReconciliationGap(
                        chain=observation.chain,
                        address=sender,
                        event_id=event_id,
                        reason="Provider observations disagree for this event identity; withheld until separately reconciled. Reacquisition alone cannot release this hold.",
                        evidence=evidence[-40:],
                    )
        elif previous:
            event = event.model_copy(
                update={"evidence": list(dict.fromkeys(previous.evidence + event.evidence))}
            )
        fresh[event_id] = event
    missing = set()
    if coverage.status == "complete":
        missing = {
            e.id
            for e in old.values()
            if e.chain == chain and address in e.senders and e.kind != "bridge" and e.id not in fresh
        }
    merged = {**old, **fresh}
    snapshot.events = [e for event_id, e in merged.items() if event_id not in conflicts | missing | held_ids]
    snapshot.reconciliation_gaps = list(gaps.values())
    if gaps:
        snapshot.schema_version = "1.2"
    if conflicts:
        coverage.status = "partial"
        coverage.reason = "Contradictory event identities excluded pending reconciliation: " + ", ".join(
            sorted(conflicts)
        )
        snapshot.limitations.append(coverage.reason)
    if missing:
        snapshot.limitations.append(
            "Prior outgoing observations absent from the newly completed provider history were excluded; the parent snapshot preserves them. Absence does not establish the cause: "
            + ", ".join(sorted(missing))
        )
        coverage.status = "partial"
        coverage.reason += "; missing historical observations require canonicality review"
    if coverage.status in ("unavailable", "not_fetched"):
        coverage.reason += "; historical observations remain and are not freshly confirmed"
    if any(g.chain == chain and g.address == address for g in gaps.values()):
        if coverage.status == "complete":
            coverage.status = "partial"
        coverage.reason += "; unresolved event reconciliation holds remain"
    scopes = {(c.chain, c.address): c for c in snapshot.coverage}
    scopes[(chain, address)] = coverage
    snapshot.coverage = list(scopes.values())
    return {
        "conflicting_event_ids": sorted(conflicts),
        "missing_prior_event_ids": sorted(missing),
        "conflict_evidence": conflict_raw,
    }


def training_expansion(chain, address):
    """A deliberately invented extra page, only called for fixture-mode executions."""
    if (chain, address) != ("ethereum", "fixture:unresolved"):
        return [], Coverage(
            chain=chain,
            address=address,
            status="not_fetched",
            reason="No synthetic expansion is defined for this scope; no HTTP call was made",
        )
    event = Transfer(
        id="fixture-expanded-deposit",
        chain=chain,
        txid="fixture-expanded-transaction",
        senders=[address],
        recipient="fixture:alpha-deposit",
        asset="ethereum:native",
        amount="1000000000000000",
        decimals=18,
        timestamp=1750000070,
        position=[107, 0, 0],
        evidence=["SYNTHETIC-EXPANSION-NOT-LIVE-EVIDENCE"],
    )
    return [event], Coverage(
        chain=chain,
        address=address,
        status="complete",
        pages=1,
        reason="Invented training expansion only; no real network data or completeness is asserted",
        evidence=event.evidence,
    )


def execute_plan(parent, spec, plan, budget, progress, assertions, acquisition_factory=None):
    snapshot = parent.model_copy(deep=True)
    acquisition = (acquisition_factory or Acquisition)(
        spec.model_copy(update={"max_requests": plan["budget_requests"]}), progress
    )
    outcomes = []
    reconciliation_raw = []
    try:
        budget.attach(acquisition)
        for action in plan["actions"]:
            if action["status"] != "selected_estimate" or action["action"] != "reacquire_history":
                continue
            chain, address = action["chain"], action["address"]
            before_calls, before_hits = acquisition.calls, acquisition.cache_hits
            progress(stage="Expanding selected frontier: " + chain)
            # New labels may have arrived since the plan; do not fetch through a now-known boundary.
            boundary = any(
                a.chain == chain
                and a.address == address
                and a.category in ("exchange", "custodian", "mixer")
                and a.valid_from <= spec.end
                and (a.valid_to is None or a.valid_to >= spec.start)
                for a in assertions
            )
            if boundary:
                outcomes.append(
                    {
                        "chain": chain,
                        "address": address,
                        "status": "skipped_new_boundary",
                        "reserved_requests": 0,
                    }
                )
                continue
            if parent.mode == "fixture":
                events, coverage = training_expansion(chain, address)
            elif acquisition.calls >= budget.cap and not acquisition.cache:
                events, coverage = (
                    [],
                    Coverage(
                        chain=chain,
                        address=address,
                        status="not_fetched",
                        reason="Execution budget exhausted before this scope",
                    ),
                )
            else:
                acquisition.partial_events, acquisition.partial_scope = [], None
                try:
                    events, coverage = (
                        acquisition.evm(chain, address)
                        if chain in ("ethereum", "bnb", "polygon")
                        else getattr(acquisition, chain)(address)
                    )
                except ProviderError as exc:
                    events = acquisition.partial_events
                    coverage = acquisition.partial_scope or Coverage(
                        chain=chain, address=address, status="unavailable", reason=str(exc)
                    )
                    coverage = coverage.model_copy(
                        update={
                            "status": "partial" if events or coverage.evidence else "unavailable",
                            "reason": str(exc) + "; earlier observations retained",
                        }
                    )
                if budget.attempt > 1 and coverage.status == "complete":
                    coverage.status = "partial"
                    coverage.reason += (
                        "; recovery replayed cached responses; pinned-head consistency is not established"
                    )
            changes = merge_scope(snapshot, chain, address, events, coverage)
            reconciliation_raw += changes.pop("conflict_evidence")
            outcomes.append(
                {
                    "chain": chain,
                    "address": address,
                    "status": coverage.status,
                    "reserved_requests": acquisition.calls - before_calls,
                    "cache_hits": acquisition.cache_hits - before_hits,
                    "acquired_events": len(events),
                    "reason": coverage.reason,
                    **changes,
                }
            )
        proofs = {p.id: p for p in snapshot.bridge_proofs}
        for proof_id, proof in acquisition.bridge_proofs.items():
            if proof_id in proofs and proofs[proof_id] != proof:
                raise ValueError("Conflicting bridge proof identity; preserved parent must be reviewed")
            proofs[proof_id] = proof
        snapshot.bridge_proofs = list(proofs.values())
        if snapshot.bridge_proofs:
            snapshot.schema_version = "1.2" if snapshot.reconciliation_gaps else "1.1"
        snapshot.limitations += acquisition.bridge_limitations + [
            "Selected-plan execution combines preserved parent observations with explicitly acquired scopes; it does not certify current chain completeness or unknown identity coverage.",
            "Request reservations survive recovery. A crash after reservation may consume a slot without dispatch or a preserved response; the hard cap is not reset.",
        ]
        if snapshot.mode == "fixture":
            snapshot.limitations.append(
                "This query execution used an explicitly invented training expansion and made zero HTTP calls."
            )
        snapshot.origin = "Selected query-plan execution over preserved parent evidence; " + parent.origin
        snapshot.collected_at = int(now())
        snapshot = Snapshot.model_validate(snapshot.model_dump())
        execution = {
            "schema": "atlas.query-execution.v1",
            "plan_sha256": budget.plan_sha256,
            "parent_snapshot_sha256": digest(parent.model_dump()),
            "budget_requests": budget.cap,
            "reserved_request_slots": acquisition.calls,
            "successful_http_responses": len(acquisition.raw),
            "cache_hits": acquisition.cache_hits,
            "recovery_attempt": budget.attempt,
            "mode": snapshot.mode,
            "actions": outcomes,
            "automatic_recursive_expansion": False,
        }
        h = artifact(canonical(execution))
        return snapshot, acquisition.raw + reconciliation_raw, execution, h
    finally:
        acquisition.close()
