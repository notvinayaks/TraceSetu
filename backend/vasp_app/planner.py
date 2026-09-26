"""Auditable acquisition estimates, kept separate from immutable attribution results."""

from fractions import Fraction
from .store import digest

POLICY_VERSION = "frontier-budget-1.1"
BASE_CALLS = {"bitcoin": 1, "ethereum": 3, "bnb": 3, "polygon": 3, "tron": 2, "solana": 1}
HISTORY_GAPS = {"incomplete_coverage", "requires_expansion"}


def plan_queries(snapshot, analysis, budget, available):
    """Budget is HTTP requests, not vendor credits. Estimates never certify coverage."""
    if not 1 <= budget <= 200:
        raise ValueError("Planning budget must be between 1 and 200 requests")
    coverage = {(c.chain, c.address): c for c in snapshot.coverage}
    grouped = {}
    nearest = analysis["certificate"]["nearest_evidenced_hops"]
    for f in analysis["frontiers"]:
        if f["reason"] in {"custody_boundary", "no_eligible_outflow_in_window"}:
            continue
        k = (f["chain"], f["address"], "history" if f["reason"] in HISTORY_GAPS else f["reason"])
        row = grouped.setdefault(
            k,
            {
                "chain": f["chain"],
                "address": f["address"],
                "hops": f["hops"],
                "reasons": set(),
                "paths": set(),
                "history": f["reason"] in HISTORY_GAPS,
            },
        )
        row["hops"] = min(row["hops"], f["hops"])
        row["reasons"].add(f["reason"])
        row["paths"].add(tuple(f["path"]))
    rows = []
    for row in grouped.values():
        c = coverage.get((row["chain"], row["address"]))
        is_history = row.pop("history")
        path_count = len(row.pop("paths"))
        row["reasons"] = sorted(row["reasons"])
        row["distinct_observed_paths"] = path_count
        row["can_precede_current_candidate"] = nearest is None or row["hops"] < nearest
        row["action"] = "reacquire_history" if is_history else "review_evidence"
        row["estimated_calls"] = (
            max(BASE_CALLS[row["chain"]], c.pages + (1 if c.cursor else 0) if c else 0)
            if is_history
            else None
        )
        row["estimate_basis"] = (
            "Maximum of adapter endpoint floor and previously acquired pages plus one if a cursor remains. Fresh reacquisition repeats pages; this is not a completion bound."
            if is_history
            else "Human or decoder/compute review; no API-cost estimate applies."
        )
        row["observed_prior_pages"] = c.pages if c else 0
        row["completion_calls_upper_bound"] = None
        row["status"] = (
            "pending"
            if is_history and available.get(row["chain"], False)
            else "provider_unavailable"
            if is_history
            else "review_required"
        )
        row["priority_reason"] = (
            "This shallower gap may change which evidenced receiving service is nearest."
            if row["can_precede_current_candidate"]
            else "This gap affects another bounded branch; the current nearer candidate is retained."
        )
        rows.append(row)
    # Protect depth before optimising local utility per estimated call. Integer fractions are exact.
    rows.sort(
        key=lambda r: (
            r["hops"],
            not r["can_precede_current_candidate"],
            -Fraction(r["distinct_observed_paths"], r["estimated_calls"] or 1),
            r["estimated_calls"] or 0,
            r["chain"],
            r["address"],
            r["reasons"],
        )
    )
    remaining = budget
    barrier = None
    for row in rows:
        if row["status"] != "pending":
            continue
        if barrier is not None and row["hops"] > barrier:
            row["status"] = "deferred_shallower_gap"
        elif row["estimated_calls"] <= remaining:
            row["status"] = "selected_estimate"
            remaining -= row["estimated_calls"]
        else:
            row["status"] = "deferred_budget"
            barrier = row["hops"] if barrier is None else min(barrier, row["hops"])
    return {
        "policy_version": POLICY_VERSION,
        "snapshot_sha256": analysis["certificate"]["snapshot_sha256"],
        "analysis_sha256": digest(analysis),
        "mode": snapshot.mode,
        "budget_requests": budget,
        "selected_estimated_requests": budget - remaining,
        "unallocated_requests": remaining,
        "actions": rows,
        "execution": "ADVISORY_ONLY",
        "meaning": "Same-depth observed path coverage per estimated HTTP request. No probability, billing quote, accuracy gain or savings claim is implied.",
        "limitations": [
            "Pagination, hydration, retries and optional label endpoints can increase actual cost. Provider billing units may differ from HTTP requests.",
            "Selected estimates do not mean the frontier will be resolved. Actual acquisitions retain a hard request cap and report unfinished coverage.",
            "Unavailable providers and manual reviews remain explicit. This plan does not infer VASP ownership or send any request.",
            "This plan performs no acquisition. Explicit execution creates a separate budgeted job; held-out cost-matched performance evaluation remains outstanding.",
        ],
    }
