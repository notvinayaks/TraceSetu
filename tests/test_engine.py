import pytest
from vasp_app.fixtures import training_snapshot
from vasp_app.domain import TraceSpec, Assertion, Coverage, Transfer
from vasp_app.engine import analyze, challenge
from vasp_app.addresses import validate_address


def scenario():
    s = training_snapshot()
    return s, TraceSpec(chain="ethereum", address="fixture:suspect", start=s.window_start, end=s.window_end)


def test_first_custody_and_no_exchange_ledger_crossing():
    s, q = scenario()
    r = analyze(s, q)
    assert [(c["entity"], c["hops"]) for c in r["candidates"]] == [
        ("Example Exchange Alpha", 1),
        ("Example Custodian Beta", 2),
    ]
    assert all(e["recipient"] != "fixture:alpha-hot" for e in r["graph"]["events"])
    assert r["certificate"]["nearest_known_target_in_snapshot_proven"] is True
    assert r["certificate"]["nearest_real_vasp_proven"] is False
    assert r["certificate"]["complete"] is False
    assert r["risk"]["classification"] == "tagged_exposure"


def test_missing_shallow_pagination_invalidates_certificate():
    s, q = scenario()
    s.coverage[0].status = "partial"
    r = analyze(s, q)
    assert r["certificate"]["nearest_known_target_in_snapshot_proven"] is False
    assert r["certificate"]["missing_shallow_frontiers"][0]["hops"] == 0


def test_conflicting_entities_are_not_confident_attribution():
    s, q = scenario()
    a = s.assertions[0].model_copy(deep=True)
    a.id = "conflict"
    a.entity = "Contradictory service"
    a.source_family = "independent"
    s.assertions.append(a)
    r = analyze(s, q)
    assert r["candidates"][0]["status"] == "conflicted"
    assert r["certificate"]["nearest_known_target_in_snapshot_proven"] is False


def test_provenance_challenge_opens_unfetched_branch():
    s, q = scenario()
    r = challenge(s, q, ["fixture-directory"])
    assert r["requires_expansion"] is True
    assert r["removed_candidates"][0][0] == "Example Exchange Alpha"
    assert r["result"]["certificate"]["nearest_evidenced_hops"] == 2
    assert r["result"]["certificate"]["nearest_known_target_in_snapshot_proven"] is False


def test_time_travel_is_not_a_path():
    s, q = scenario()
    s.events[2].timestamp = s.events[1].timestamp - 1
    r = analyze(s, q)
    assert all(c["entity"] != "Example Custodian Beta" for c in r["candidates"])


def test_ambiguous_order_abstains():
    s, q = scenario()
    s.events[2].timestamp = s.events[1].timestamp
    s.events[2].position = None
    r = analyze(s, q)
    assert any(f["reason"] == "ambiguous_event_order" for f in r["frontiers"])
    assert all(c["entity"] != "Example Custodian Beta" for c in r["candidates"])


def test_pending_failed_and_orphaned_do_not_count():
    for state in ("pending", "orphaned", "failed"):
        s, q = scenario()
        if state == "failed":
            s.events[0].success = False
        else:
            s.events[0].finality = state
        assert all(c["entity"] != "Example Exchange Alpha" for c in analyze(s, q)["candidates"])


def test_chain_qualified_assertions_and_amounts():
    s, q = scenario()
    s.assertions[0].chain = "polygon"
    r = analyze(s, q)
    assert all(c["entity"] != "Example Exchange Alpha" for c in r["candidates"])
    c = next(c for c in r["candidates"] if c["entity"] == "Example Custodian Beta")
    assert c["amount_bounds"]["lower"] == "0"
    assert c["amount_bounds"]["upper"] == "5000000000000000000"


def test_asset_switch_not_inferred():
    s, q = scenario()
    s.events[2].asset = "ethereum:token"
    r = analyze(s, q)
    assert all(c["entity"] != "Example Custodian Beta" for c in r["candidates"])
    assert any(f["reason"] == "asset_transition_unresolved" for f in r["frontiers"])


def test_hop_limit_and_amount_filter_explicit():
    s, q = scenario()
    q.max_hops = 1
    q.minimum_amount = "1000000000000000000"
    r = analyze(s, q)
    assert any(f["reason"] == "amount_filter" for f in r["frontiers"])
    assert any(f["reason"] == "hop_limit" for f in r["frontiers"])
    assert r["certificate"]["nearest_known_target_in_snapshot_proven"] is False


def test_unknown_risk_is_unassessed():
    s, q = scenario()
    s.assertions = []
    assert analyze(s, q)["risk"]["classification"] == "unassessed"


def test_dense_frontier_has_an_explicit_memory_bound():
    s, q = scenario()
    q.max_states = 10
    s.events = []
    s.assertions = []
    for n in range(100):
        s.events.append(
            Transfer(
                id=str(n),
                chain="ethereum",
                txid=str(n),
                senders=["fixture:suspect"],
                recipient=f"fixture:{n}",
                asset="ethereum:native",
                amount="1",
                decimals=18,
                timestamp=q.start + 1,
                evidence=["synthetic"],
            )
        )
    r = analyze(s, q)
    assert r["certificate"]["examined_states"] <= 10
    assert any(f["reason"] == "state_budget" for f in r["frontiers"])
    assert r["certificate"]["complete"] is False


def test_snapshot_window_enforced():
    s, q = scenario()
    q.start -= 1
    with pytest.raises(ValueError):
        analyze(s, q)


def test_utxo_does_not_assert_exact_input_output_allocation():
    s, q = scenario()
    s.assertions = []
    s.events = [
        Transfer(
            id="out:0",
            chain="bitcoin",
            txid="tx",
            senders=["fixture:sender", "fixture:other"],
            recipient="fixture:deposit",
            asset="bitcoin:native",
            amount="900",
            decimals=8,
            timestamp=q.start + 1,
            kind="utxo",
            input_outpoints=["prior:0", "other:1"],
            evidence=["raw"],
        )
    ]
    s.coverage = [Coverage(chain="bitcoin", address="fixture:sender", status="complete", reason="fixture")]
    s.assertions = [
        Assertion(
            id="label",
            chain="bitcoin",
            address="fixture:deposit",
            entity="Custodian",
            category="custodian",
            grade="reviewed",
            source="fixture",
            source_family="fixture",
            evidence=["fixture"],
        )
    ]
    q.chain = "bitcoin"
    q.address = "fixture:sender"
    r = analyze(s, q)
    assert r["candidates"][0]["amount_bounds"]["lower"] == "0"
    assert r["graph"]["events"][0]["senders"] == ["fixture:sender", "fixture:other"]


def test_bitcoin_follows_spent_outpoint_not_unrelated_wallet_balance():
    s, q = scenario()
    q.chain = "bitcoin"
    q.address = "seed"
    s.assertions = []
    s.coverage = []
    first = Transfer(
        id="a:0",
        chain="bitcoin",
        txid="a",
        senders=["seed"],
        recipient="middle",
        asset="bitcoin:native",
        amount="100",
        decimals=8,
        timestamp=110,
        kind="utxo",
        output_index=0,
        input_outpoints=["old:1"],
        evidence=["raw"],
    )
    second = Transfer(
        id="b:0",
        chain="bitcoin",
        txid="b",
        senders=["middle"],
        recipient="deposit",
        asset="bitcoin:native",
        amount="90",
        decimals=8,
        timestamp=110,
        kind="utxo",
        output_index=0,
        input_outpoints=["unrelated:1"],
        evidence=["raw"],
    )
    s.events = [first, second]
    s.window_start = 100
    s.window_end = 200
    q.start = 100
    q.end = 200
    assert len(analyze(s, q)["graph"]["events"]) == 1
    second.input_outpoints = ["a:0"]
    assert len(analyze(s, q)["graph"]["events"]) == 2


@pytest.mark.parametrize(
    "chain,address",
    [
        ("ethereum", "0x52908400098527886E0F7030069857D2E4169EE7"),
        ("bitcoin", "1BoatSLRHtKNngkdXEeobR76b53LETtpyT"),
        ("tron", "TLa2f6VPqDgRE67v1736s7bJ8Ray5wYjU7"),
        ("solana", "11111111111111111111111111111111"),
    ],
)
def test_valid_mainnet_syntax(chain, address):
    assert validate_address(chain, address)


@pytest.mark.parametrize(
    "chain,address",
    [
        ("ethereum", "0x1234"),
        ("ethereum", "0x52908400098527886E0F7030069857D2E4169Ee7"),
        ("bitcoin", "1BoatSLRHtKNngkdXEeobR76b53LETtpyU"),
        ("solana", "fixture:seed"),
        ("tron", "0x1234"),
    ],
)
def test_invalid_address_rejected(chain, address):
    with pytest.raises(ValueError):
        validate_address(chain, address)
