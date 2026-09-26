"""Deterministic, bounded first-custody analysis; no ownership oracle or taint claim."""

from __future__ import annotations

from collections import defaultdict, deque
from ..domain import Snapshot, TraceSpec
from ..store import digest

ENGINE_VERSION = "0.3.0"
CUSTODY = {"exchange", "custodian"}


def key(chain, address):
    return f"{chain}:{address}"


def analyze(snapshot: Snapshot, spec: TraceSpec, excluded: set[str] | None = None):
    excluded = excluded or set()
    if spec.start < snapshot.window_start or spec.end > snapshot.window_end:
        raise ValueError("Trace window exceeds the acquisition window")
    outgoing, labels = defaultdict(list), defaultdict(list)
    for event in snapshot.events:
        for sender in set(event.senders):
            outgoing[key(event.chain, sender)].append(event)
    for rows in outgoing.values():
        rows.sort(key=lambda e: (e.timestamp, e.position or [], e.id))
    for a in snapshot.assertions:
        if a.id not in excluded and a.source_family not in excluded:
            labels[key(a.chain, a.address)].append(a)
    coverage = {key(c.chain, c.address): c for c in snapshot.coverage}
    # A separate state for each causal path preserves splits and alternate asset histories.
    queue = deque([(spec.chain, spec.address, [], None, None, spec.asset)])
    candidates, frontiers, edges, nodes, visited_scopes = [], [], {}, {}, set()
    states = 0
    transitions = 0
    max_transitions = min(200000, spec.max_states * 20)

    def frontier(chain, address, hops, reason, path, **extra):
        frontiers.append(dict(chain=chain, address=address, hops=hops, reason=reason, path=path, **extra))

    while queue and states < spec.max_states and transitions < max_transitions:
        chain, address, path, previous, upper, asset = queue.popleft()
        states += 1
        scope, hops = key(chain, address), len(path)
        arrival = previous.timestamp if previous else spec.start
        active = [
            a
            for a in labels[scope]
            if a.valid_from <= arrival and (a.valid_to is None or arrival <= a.valid_to)
        ]
        nodes[scope] = dict(
            id=scope, chain=chain, address=address, labels=[a.model_dump() for a in active], seed=hops == 0
        )
        custody = [a for a in active if a.category in CUSTODY]
        # A contradictory category is relevant too: an exchange/bridge conflict is not consensus.
        credible = [a for a in active if a.grade != "hypothesis"]
        conflict = len({(a.entity, a.category) for a in credible}) > 1
        if custody:
            accepted = [a for a in custody if a.grade != "hypothesis"]
            state = "conflicted" if conflict else "evidenced" if accepted else "hypothesis"
            candidates.append(
                dict(
                    chain=chain,
                    address=address,
                    entity=accepted[0].entity if accepted and not conflict else custody[0].entity,
                    hops=hops,
                    path=path,
                    status=state,
                    assertions=[a.model_dump() for a in active],
                    deposit_role="deposit"
                    if any(a.role == "deposit" for a in accepted)
                    else "not_established",
                    amount_bounds={
                        "lower": "0",
                        "upper": str(upper) if upper is not None else None,
                        "asset": asset,
                        "meaning": "Per-path possible exposure only; not attributable customer funds. Do not sum overlapping paths.",
                    },
                )
            )
            frontier(
                chain,
                address,
                hops,
                "custody_boundary" if state == "evidenced" else f"{state}_custody_boundary",
                path,
            )
            continue
        if conflict:
            frontier(chain, address, hops, "conflicting_service_labels", path)
            continue
        if any(a.category == "mixer" for a in active):
            frontier(chain, address, hops, "mixer_boundary_no_deterministic_link", path)
            continue
        if hops >= spec.max_hops:
            frontier(chain, address, hops, "hop_limit", path)
            continue
        visited_scopes.add(scope)
        c = coverage.get(scope)
        if not c or c.status != "complete":
            frontier(
                chain,
                address,
                hops,
                "requires_expansion" if excluded else "incomplete_coverage",
                path,
                detail=c.reason if c else "No acquired history for this address",
            )
        found = False
        for e in outgoing[scope]:
            if transitions >= max_transitions:
                frontier(chain, address, hops, "transition_budget", path)
                break
            transitions += 1
            if (
                not e.success
                or e.finality in ("pending", "orphaned")
                or not spec.start <= e.timestamp <= spec.end
            ):
                continue
            if e.id in path or (previous and e.txid == previous.txid and e.kind == "utxo"):
                continue
            if previous:
                utxo_link = (
                    e.kind == "utxo"
                    and previous.kind == "utxo"
                    and previous.output_index is not None
                    and f"{previous.txid}:{previous.output_index}" in e.input_outpoints
                )
                if e.kind == "utxo" and previous.kind == "utxo" and not utxo_link:
                    frontier(chain, address, hops, "utxo_outpoint_link_not_established", path, event=e.id)
                    continue
                if e.timestamp < previous.timestamp and not utxo_link:
                    continue
                if e.timestamp == previous.timestamp and not utxo_link:
                    if chain != previous.chain or e.position is None or previous.position is None:
                        frontier(chain, address, hops, "ambiguous_event_order", path, event=e.id)
                        continue
                    if e.position <= previous.position:
                        continue
            if asset and e.asset != asset:
                frontier(chain, address, hops, "asset_transition_unresolved", path, event=e.id)
                continue
            if int(e.amount) < int(spec.minimum_amount):
                frontier(chain, address, hops, "amount_filter", path, event=e.id)
                continue
            target_chain = e.destination_chain or chain
            target_asset = e.destination_asset or e.asset
            if e.kind == "bridge":
                # Imported bridge proof is an assertion; this engine does not independently verify a protocol.
                frontier(chain, address, hops, "bridge_proof_requires_protocol_verifier", path, event=e.id)
                continue
            edges[e.id] = e.model_dump()
            amount = int(e.amount)
            capacity = amount if upper is None else min(upper, amount)
            if states + len(queue) < spec.max_states:
                queue.append((target_chain, e.recipient, path + [e.id], e, capacity, target_asset))
            else:
                frontier(target_chain, e.recipient, hops + 1, "state_budget", path + [e.id])
            found = True
        if not found and c and c.status == "complete":
            frontier(chain, address, hops, "no_eligible_outflow_in_window", path)
    if queue:
        for chain, address, path, *_ in queue:
            frontier(
                chain,
                address,
                len(path),
                "transition_budget" if transitions >= max_transitions else "state_budget",
                path,
            )
    candidates.sort(key=lambda c: (c["hops"], c["status"] != "evidenced", c["entity"], c["path"]))
    nearest = min((c["hops"] for c in candidates if c["status"] == "evidenced"), default=None)
    unresolved = [
        f for f in frontiers if f["reason"] not in {"custody_boundary", "no_eligible_outflow_in_window"}
    ]
    # All paths shallower than the closest answer must be settled. Unknown identity is a separate claim.
    shallow_gaps = [f for f in unresolved if nearest is None or f["hops"] < nearest]
    known_proven = nearest is not None and not shallow_gaps
    risk = []
    for node in nodes.values():
        for a in node["labels"]:
            for tag in a["risk_tags"]:
                risk.append({"tag": tag, "node": node["id"], "assertion_id": a["id"], "grade": a["grade"]})
    query_plan = []
    for f in unresolved:
        q = {
            "chain": f["chain"],
            "address": f["address"],
            "hops": f["hops"],
            "reason": f["reason"],
            "action": "acquire_history"
            if f["reason"] in ("incomplete_coverage", "requires_expansion", "state_budget")
            else "review_evidence",
            "priority_rule": "Shallower unresolved frontiers first; lexical tie-break. Not a probability.",
            "estimated_calls": None,
        }
        if not any(
            (p["chain"], p["address"], p["reason"]) == (q["chain"], q["address"], q["reason"])
            for p in query_plan
        ):
            query_plan.append(q)
    query_plan.sort(key=lambda q: (q["hops"], q["chain"], q["address"], q["reason"]))
    certificate = dict(
        engine_version=ENGINE_VERSION,
        snapshot_sha256=digest(snapshot.model_dump()),
        specification=spec.model_dump(),
        excluded=sorted(excluded),
        nearest_evidenced_hops=nearest,
        nearest_known_target_in_snapshot_proven=known_proven,
        nearest_real_vasp_proven=False,
        identity_coverage="Unknown wallets may be unlabelled custodial services.",
        missing_shallow_frontiers=shallow_gaps,
        examined_states=states,
        complete=not unresolved,
        examined_transitions=transitions,
        max_transitions=max_transitions,
        scope="Directed chronological observed transfers in this asset/window/hop bound; ownership and incident allocation are not proven.",
    )
    return dict(
        candidates=candidates,
        frontiers=frontiers,
        graph={"nodes": list(nodes.values()), "events": list(edges.values())},
        certificate=certificate,
        query_plan=query_plan,
        risk={"classification": "tagged_exposure" if risk else "unassessed", "signals": risk},
        limitations=snapshot.limitations
        + [
            "Integer upper bounds describe possible per-path exposure; no allocation model or customer attribution is implied.",
            "Source grades are evidence categories, not calibrated probabilities.",
            "An unknown label is not proof of self-custody or low risk.",
        ],
        mode=snapshot.mode,
    )


def challenge(snapshot, spec, excluded):
    original = analyze(snapshot, spec)
    changed = analyze(snapshot, spec, set(excluded))
    before = {(c["entity"], c["hops"], tuple(c["path"])) for c in original["candidates"]}
    after = {(c["entity"], c["hops"], tuple(c["path"])) for c in changed["candidates"]}
    return {
        "excluded": excluded,
        "removed_candidates": [list(c) for c in sorted(before - after)],
        "added_candidates": [list(c) for c in sorted(after - before)],
        "requires_expansion": any(f["reason"] == "requires_expansion" for f in changed["frontiers"]),
        "result": changed,
    }
