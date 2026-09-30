"""Proposed, deliberately narrow research reference; not production attribution.

All identity anchors and coverage assertions are external inputs.  No graph
pattern in this module establishes ownership, beneficiary identity or guilt.
"""

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Iterable

CONTROL_ROLES = {"hot_wallet", "gas_feeder", "deposit_address"}


@dataclass(frozen=True)
class Event:
    event_id: str
    tx_id: str
    chain: str
    asset: str
    sender: str
    recipient: str
    units: int
    at: int
    order: int
    success: bool = True
    tx_sender: str = ""
    gas_payer: str = ""
    fee_units: int = 0
    receipt_ref: str = ""
    execution_kind: str = "transfer"


@dataclass(frozen=True)
class Anchor:
    anchor_id: str
    chain: str
    address: str
    service: str
    role: str
    valid_from: int
    valid_until: int
    learned_at: int
    source_family: str
    evidence_ref: str
    withdrawn_at: int | None = None


@dataclass(frozen=True)
class Coverage:
    chain: str
    address: str
    start: int
    end: int
    complete: bool
    all_native_token_receipts: bool
    plain_token_semantics: bool
    opening_balances: dict[str, int]
    closing_balances: dict[str, int]
    evidence_ref: str


@dataclass
class Detection:
    chain: str
    address: str
    asset: str
    window: tuple[int, int]
    as_of: int
    excluded_sources: tuple[str, ...]
    evidence_snapshot_sha256: str = ""
    status: str = "abstain"
    service: str | None = None
    reasons: list[str] = field(default_factory=list)
    cycles: list[dict] = field(default_factory=list)
    ignored_events: list[dict] = field(default_factory=list)
    calibrated_probability: None = None
    ownership_proven: bool = False
    independent_confirmation_required: bool = True

    def to_dict(self) -> dict:
        return asdict(self)


def exact_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def evidence_snapshot_sha256(events: Iterable[Event], anchors: Iterable[Anchor]) -> str:
    """Bind a report to every supplied event and anchor, ignoring input order.

    Duplicate records remain represented; scope/configuration are also checked
    separately when consuming an assessment. This is change detection, not an
    authentication signature or a proof that observations are true.
    """
    def records(values: Iterable) -> list[str]:
        return sorted(json.dumps(asdict(value), sort_keys=True, separators=(",", ":"),
                                 ensure_ascii=False) for value in values)

    payload = {"schema": "tracesetu-reference-evidence-v1",
               "events": records(events), "anchors": records(anchors)}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def active_anchors(
    anchors: Iterable[Anchor], chain: str, address: str, roles: set[str],
    at: int, as_of: int, excluded_sources: set[str],
) -> list[Anchor]:
    """A source-qualified assertion, not a claim that the source is correct."""
    return [a for a in anchors if (
        a.chain == chain and a.address == address and a.role in roles
        and a.valid_from <= at < a.valid_until and a.learned_at <= as_of
        and (a.withdrawn_at is None or a.withdrawn_at > as_of)
        and a.source_family and a.evidence_ref and a.service
        and a.source_family not in excluded_sources
    )]


def detect_candidate(
    events: Iterable[Event], anchors: Iterable[Anchor], coverage: Coverage,
    *, chain: str, address: str, token: str, native: str,
    window: tuple[int, int], as_of: int, excluded_sources: Iterable[str] = (),
    minimum_cycles: int = 3, minimum_incoming_units: int = 100,
) -> Detection:
    """Recognise isolated deposit/top-up/sweep cycles as a hypothesis only.

    Minimum units and three cycles are arbitrary synthetic-demo policy inputs,
    not calibrated thresholds.  Unknown history or semantics cause abstention.
    """
    excluded = set(excluded_sources)
    result = Detection(chain, address, token, window, as_of, tuple(sorted(excluded)))
    event_list = list(events)
    anchor_list = list(anchors)
    result.evidence_snapshot_sha256 = evidence_snapshot_sha256(event_list, anchor_list)

    def reject(reason: str) -> Detection:
        result.reasons.append(reason)
        return result

    start, end = window
    if (start >= end or end > as_of or not exact_integer(minimum_cycles) or minimum_cycles < 1
            or not exact_integer(minimum_incoming_units) or minimum_incoming_units < 1
            or token == native):
        return reject("invalid_or_future_observation_window_or_policy")
    if (coverage.chain != chain or coverage.address != address
            or coverage.start > start or coverage.end < end
            or not coverage.complete or not coverage.all_native_token_receipts
            or not coverage.evidence_ref):
        return reject("complete_all_activity_window_not_attested")
    # Boundary balances must refer to these exact boundaries, not a wider page.
    if coverage.start != start or coverage.end != end:
        return reject("balance_boundaries_do_not_match_observation_window")
    if not coverage.plain_token_semantics:
        return reject("plain_nonrebasing_nonfee_token_semantics_not_established")
    if any(not exact_integer(x) or x != 0 for x in coverage.opening_balances.values()):
        return reject("nonzero_or_invalid_opening_balance")
    if token not in coverage.opening_balances or native not in coverage.opening_balances:
        return reject("opening_token_and_native_balances_missing")
    if token not in coverage.closing_balances or native not in coverage.closing_balances:
        return reject("closing_token_and_native_balances_missing")
    if any(not exact_integer(x) or x < 0 for x in coverage.closing_balances.values()):
        return reject("invalid_closing_balance")
    if any(value != 0 for asset, value in coverage.closing_balances.items()
           if asset not in {token, native}):
        return reject("other_asset_balance_present")

    relevant = [e for e in event_list if e.chain == chain
                and address in {e.sender, e.recipient} and start <= e.at <= end]
    if len({e.event_id for e in relevant}) != len(relevant):
        return reject("duplicate_or_ambiguous_event_id")
    if len({e.order for e in relevant}) != len(relevant):
        return reject("ambiguous_ledger_order")
    relevant.sort(key=lambda e: e.order)
    if any(a.at > b.at for a, b in zip(relevant, relevant[1:])):
        return reject("ledger_order_and_time_disagree")

    pending: Event | None = None
    gas: tuple[Event, list[Anchor]] | None = None
    native_balance = 0
    services: set[str] = set()
    successful_tx_ids: set[str] = set()
    for event in relevant:
        if not exact_integer(event.units) or event.units < 0:
            return reject("negative_or_noninteger_units")
        if not event.success:
            if event.sender == address:
                return reject("failed_outgoing_execution_not_supported")
            result.ignored_events.append({"id": event.event_id, "reason": "reverted_no_transfer"})
            continue
        if event.units == 0:
            if event.sender == address:
                return reject("zero_value_outgoing_execution_not_supported")
            result.ignored_events.append({"id": event.event_id, "reason": "zero_units_not_a_cycle"})
            continue
        if event.tx_id in successful_tx_ids:
            return reject("multiple_relevant_effects_in_one_transaction")
        successful_tx_ids.add(event.tx_id)
        if event.sender == event.recipient:
            return reject("self_transfer_not_supported")
        if event.asset not in {token, native}:
            return reject("mixed_assets_or_other_outflows")

        if event.asset == native:
            if event.recipient != address:
                return reject("native_outflow_not_supported")
            if pending is None or gas is not None:
                return reject("gas_funding_not_uniquely_paired_with_pending_deposit")
            feeders = active_anchors(anchor_list, chain, event.sender, {"gas_feeder"},
                                     event.at, as_of, excluded)
            if not feeders:
                return reject("source_qualified_service_gas_feeder_missing")
            feeder_control = active_anchors(anchor_list, chain, event.sender, CONTROL_ROLES,
                                            event.at, as_of, excluded)
            if len({a.service for a in feeder_control}) != 1:
                return reject("conflicting_gas_feeder_service_anchors")
            gas = (event, feeders)
            native_balance += event.units
            continue

        if event.recipient == address:
            # A positive dust transfer is real; silently dropping it would
            # manufacture isolation.  This toy policy therefore abstains.
            if event.units < minimum_incoming_units:
                return reject("small_positive_transfer_breaks_isolation_policy")
            if pending is not None:
                return reject("multiple_incomings_before_sweep")
            pending = event
            gas = None
            continue

        if pending is None:
            return reject("outgoing_without_isolated_incoming")
        if event.units != pending.units:
            return reject("sweep_not_exact_integer_deposit_amount")
        if (event.execution_kind != "direct_token_transfer"
                or event.tx_sender != address or event.gas_payer != address
                or not event.receipt_ref or not exact_integer(event.fee_units)
                or event.fee_units <= 0):
            return reject("direct_transfer_and_actual_gas_payment_not_established")
        if gas is None:
            return reject("cycle_gas_funding_missing")
        if event.fee_units > native_balance:
            return reject("observed_native_funding_cannot_cover_receipt_fee")
        hot = active_anchors(anchor_list, chain, event.recipient, {"hot_wallet"},
                             event.at, as_of, excluded)
        if not hot:
            return reject("source_qualified_hot_wallet_anchor_missing")
        hot_control = active_anchors(anchor_list, chain, event.recipient, CONTROL_ROLES,
                                     event.at, as_of, excluded)
        if len({a.service for a in hot_control}) != 1:
            return reject("conflicting_hot_wallet_service_anchors")
        service = hot[0].service
        if service != gas[1][0].service:
            return reject("hot_wallet_and_gas_feeder_services_disagree")
        services.add(service)
        if len(services) != 1:
            return reject("cycles_point_to_multiple_services")
        native_balance -= event.fee_units
        result.cycles.append({
            "deposit_event": pending.event_id, "deposit_at": pending.at,
            "gas_event": gas[0].event_id, "sweep_event": event.event_id,
            "sweep_at": event.at, "token_units": pending.units,
            "observed_receipt_fee_units": event.fee_units,
            "hot_wallet_anchor_ids": sorted(a.anchor_id for a in hot),
            "gas_feeder_anchor_ids": sorted(a.anchor_id for a in gas[1]),
            "source_families": sorted({a.source_family for a in hot + gas[1]}),
            "service_assertion": service,
        })
        pending = None
        gas = None

    if pending is not None:
        return reject("unswept_incoming_at_window_end")
    if coverage.closing_balances[token] != 0 or coverage.closing_balances[native] != native_balance:
        return reject("observed_effects_do_not_reconcile_to_closing_balances")
    if len(result.cycles) < minimum_cycles:
        return reject("insufficient_complete_cycles_for_toy_policy")
    result.status = "heuristic_candidate"
    result.service = next(iter(services))
    result.reasons.append("isolated_sweep_and_gas_pattern_requires_independent_confirmation")
    return result


def trace_frontier(
    events: Iterable[Event], anchors: Iterable[Anchor], *, chain: str, asset: str,
    start_address: str, window: tuple[int, int], as_of: int,
    detections: Iterable[Detection] = (), mode: str = "candidate_frontier",
    max_hops: int = 4, max_states: int = 1000,
    excluded_sources: Iterable[str] = (),
) -> dict:
    """Bounded chronological connectivity; not same-unit account tracing.

    known_labels_only exposes the farther label that a label lookup can find.
    candidate_frontier stops at assessed hypotheses/unresolved boundaries.
    Neither output proves globally nearest custody or transfer ownership.
    """
    if mode not in {"known_labels_only", "candidate_frontier"}:
        raise ValueError("Unsupported mode")
    if window[0] >= window[1] or window[1] > as_of or max_hops < 0 or max_states < 1:
        raise ValueError("Invalid search bounds")
    excluded = set(excluded_sources)
    anchor_list = list(anchors)
    event_list = list(events)
    current_snapshot = evidence_snapshot_sha256(event_list, anchor_list)
    relevant = sorted([e for e in event_list if e.chain == chain and e.asset == asset
                       and e.success and exact_integer(e.units) and e.units > 0
                       and window[0] <= e.at <= window[1]], key=lambda e: e.order)
    reports = {(r.chain, r.address): r for r in detections}
    queue = [(start_address, window[0], -1, [], [start_address])]
    stops: list[dict] = []
    explored = 0
    while queue and explored < max_states:
        address, last_at, last_order, path, visited = queue.pop(0)
        explored += 1
        base = {"address": address, "path_event_ids": path, "hops": len(path)}
        known = active_anchors(anchor_list, chain, address, {"hot_wallet", "deposit_address"},
                               last_at, as_of, excluded)
        if known:
            control = active_anchors(anchor_list, chain, address, CONTROL_ROLES,
                                      last_at, as_of, excluded)
            services = {a.service for a in control}
            if len(services) > 1:
                stops.append(dict(base, status="unresolved_conflicting_service_assertions"))
            else:
                stops.append(dict(base, status="known_service_assertion", service=next(iter(services)),
                                  anchor_ids=sorted(a.anchor_id for a in known),
                                  asserted_roles=sorted({a.role for a in known}),
                                  deposit_acceptance_asserted=any(a.role == "deposit_address" for a in known),
                                  unlabelled_predecessors=visited[1:-1], nearest_proven=False))
            continue  # Never connect service withdrawals as customer continuity.
        feeder_control = active_anchors(anchor_list, chain, address, {"gas_feeder"},
                                        last_at, as_of, excluded)
        if feeder_control:
            services = {a.service for a in feeder_control}
            if len(services) > 1:
                stops.append(dict(base, status="unresolved_conflicting_service_assertions"))
            else:
                stops.append(dict(base, status="unresolved_service_controlled_non_deposit_role",
                                  service=next(iter(services)),
                                  anchor_ids=sorted(a.anchor_id for a in feeder_control),
                                  asserted_roles=["gas_feeder"], deposit_acceptance_asserted=False))
            continue  # A service-controlled gas account is not proven to accept customer deposits.
        report = reports.get((chain, address)) if mode == "candidate_frontier" else None
        if report is not None:
            if (report.asset != asset or report.window != window or report.as_of != as_of
                    or report.excluded_sources != tuple(sorted(excluded))
                    or report.evidence_snapshot_sha256 != current_snapshot):
                stops.append(dict(base, status="unresolved_stale_or_mismatched_assessment"))
            elif report.status == "heuristic_candidate":
                observed_start = min(c["deposit_at"] for c in report.cycles)
                observed_end = max(c["sweep_at"] for c in report.cycles)
                if observed_start <= last_at <= observed_end:
                    stops.append(dict(base, status="provisional_custody_boundary", service=report.service,
                                      ownership_proven=False, independent_confirmation_required=True,
                                      nearest_proven=False))
                else:
                    stops.append(dict(base, status="unresolved_outside_candidate_pattern_period"))
            else:
                stops.append(dict(base, status="unresolved_assessed_boundary", reasons=report.reasons))
            continue  # Do not skip a possible/unknown boundary to claim a farther VASP.
        if len(path) >= max_hops:
            stops.append(dict(base, status="unresolved_hop_limit"))
            continue
        # Address identity alone is not a temporal state. Revisiting an address
        # can meet a service assertion that became valid after its first visit.
        # Strict event order and explicit hop/state bounds prevent infinite walks.
        outgoing = [e for e in relevant if e.sender == address and e.order > last_order
                    and e.at >= last_at]
        if not outgoing:
            stops.append(dict(base, status="unresolved_no_observed_continuation"))
        for event in outgoing:
            queue.append((event.recipient, event.at, event.order,
                          path + [event.event_id], visited + [event.recipient]))
    return {
        "mode": mode, "chain": chain, "asset": asset, "window": window,
        "evidence_snapshot_sha256": current_snapshot,
        "as_of": as_of, "max_hops": max_hops, "explored_states": explored,
        "truncated_by_state_budget": bool(queue), "unvisited_state_count": len(queue),
        "stops": stops, "globally_nearest_service_proven": False,
        "path_semantics": "chronological_transfer_connectivity_not_same_unit_provenance",
        "ownership_or_beneficiary_proven": False,
    }
