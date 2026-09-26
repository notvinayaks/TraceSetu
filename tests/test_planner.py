from vasp_app.domain import Coverage
from vasp_app.fixtures import training_snapshot
from vasp_app.planner import plan_queries


def planning_example():
    s = training_snapshot()
    s.coverage = [
        Coverage(
            chain="ethereum",
            address="fixture:expensive",
            status="partial",
            reason="pages missing",
            pages=8,
            cursor="page9",
        ),
        Coverage(
            chain="ethereum", address="fixture:cheap", status="partial", reason="pages missing", pages=1
        ),
    ]
    a = {
        "certificate": {"nearest_evidenced_hops": 3, "snapshot_sha256": "synthetic-hash"},
        "frontiers": [
            {
                "chain": "ethereum",
                "address": address,
                "hops": hops,
                "path": [address],
                "reason": "incomplete_coverage",
            }
            for address, hops in [("fixture:expensive", 1), ("fixture:cheap", 1), ("fixture:deeper", 2)]
        ],
    }
    return s, a


def test_budget_chooses_cheaper_same_depth_and_preserves_shallow_barrier():
    s, a = planning_example()
    p = plan_queries(s, a, 6, {"ethereum": True})
    selected = [r["address"] for r in p["actions"] if r["status"] == "selected_estimate"]
    assert selected == ["fixture:cheap"]
    assert p["selected_estimated_requests"] == 3
    expensive = next(r for r in p["actions"] if r["address"] == "fixture:expensive")
    assert expensive["estimated_calls"] == 9
    assert expensive["status"] == "deferred_budget"
    assert p["actions"][-1]["status"] == "deferred_shallower_gap"
    assert p["execution"] == "ADVISORY_ONLY"
    assert all(r["completion_calls_upper_bound"] is None for r in p["actions"])


def test_unavailable_provider_is_not_selected_and_manual_review_is_not_free_api_work():
    s, a = planning_example()
    a["frontiers"].append(
        {
            "chain": "ethereum",
            "address": "fixture:conflict",
            "hops": 1,
            "path": ["test"],
            "reason": "conflicted_custody_boundary",
        }
    )
    p = plan_queries(s, a, 200, {"ethereum": False})
    assert p["selected_estimated_requests"] == 0
    assert {r["status"] for r in p["actions"]} == {"provider_unavailable", "review_required"}
    manual = next(r for r in p["actions"] if r["address"] == "fixture:conflict")
    assert manual["estimated_calls"] is None


def test_duplicate_frontiers_do_not_duplicate_budget_and_order_is_stable():
    s, a = planning_example()
    a["frontiers"].append(dict(a["frontiers"][0]))
    first = plan_queries(s, a, 15, {"ethereum": True})
    assert len(first["actions"]) == 3
    a["frontiers"].reverse()
    second = plan_queries(s, a, 15, {"ethereum": True})
    assert first["actions"] == second["actions"]
    assert first["selected_estimated_requests"] == 15
