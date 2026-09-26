"""Provider contract regression tests, separate from actual live verification."""

import pytest

from vasp_app.config import settings
from vasp_app.domain import TraceSpec
from vasp_app.providers import Acquisition, ProviderError


def transaction():
    return dict(
        hash="a" * 64,
        block_height=40,
        block_index=3,
        confirmations=10,
        confirmed="2017-08-03T03:10:00Z",
        vin_sz=2,
        vout_sz=2,
        inputs=[
            dict(prev_hash="b" * 64, output_index=2, addresses=["seed"]),
            dict(prev_hash="c" * 64, output_index=1, addresses=["other"]),
        ],
        outputs=[dict(value=123456789, addresses=["recipient"]), dict(value=1000, addresses=["seed"])],
    )


@pytest.fixture
def acquisition(monkeypatch):
    monkeypatch.setattr(settings, "bitcoin_provider", "blockcypher")
    a = Acquisition(
        TraceSpec(chain="bitcoin", address="seed", start=1501718400, end=1501804800, max_requests=3)
    )
    yield a
    a.close()


def test_exact_inputs_outputs_and_height_pagination(acquisition, monkeypatch):
    calls = []

    def fetch(*args, **kwargs):
        calls.append(kwargs["params"])
        assert kwargs["params"]["txlimit"] == 1000
        assert "confirmations" not in kwargs["params"]
        if len(calls) == 1:
            return dict(address="seed", txs=[transaction()], hasMore=True), "first-hash"
        assert kwargs["params"]["before"] == 40
        return dict(address="seed", txs=[], hasMore=False), "second-hash"

    monkeypatch.setattr(acquisition, "fetch", fetch)
    events, coverage = acquisition.bitcoin("seed")
    assert len(events) == 2 and coverage.pages == 2
    assert events[0].amount == "123456789" and events[0].position == [40, 3, 0]
    assert events[0].senders == ["seed", "other"]
    assert events[0].input_outpoints == ["b" * 64 + ":2", "c" * 64 + ":1"]
    assert coverage.evidence == ["first-hash", "second-hash"]


@pytest.mark.parametrize(
    "change,match",
    [
        ({"vin_sz": 3}, "truncated"),
        ({"vout_sz": 3}, "truncated"),
        ({"double_spend": True}, "double-spend"),
        ({"confirmed": "bad"}, "timestamp"),
    ],
)
def test_reject_unreliable_transaction(acquisition, monkeypatch, change, match):
    tx = transaction()
    tx.update(change)
    monkeypatch.setattr(acquisition, "fetch", lambda *a, **k: (dict(address="seed", txs=[tx]), "h"))
    with pytest.raises(ProviderError, match=match):
        acquisition.bitcoin("seed")


def test_unknown_script_marks_partial_without_fabricating_allocation(acquisition, monkeypatch):
    tx = transaction()
    tx["outputs"][1]["addresses"] = ["key-a", "key-b"]
    monkeypatch.setattr(acquisition, "fetch", lambda *a, **k: (dict(address="seed", txs=[tx]), "h"))
    events, coverage = acquisition.bitcoin("seed")
    assert len(events) == 1 and coverage.status == "partial"


def test_missing_pagination_signal_never_means_complete(acquisition, monkeypatch):
    monkeypatch.setattr(
        acquisition, "fetch", lambda *a, **k: (dict(address="seed", txs=[transaction()], n_tx=145), "h")
    )
    events, coverage = acquisition.bitcoin("seed")
    assert len(events) == 2 and coverage.status == "partial"
    assert "omitted" in coverage.reason


def test_stalled_cursor_keeps_checkpoint_and_fails(acquisition, monkeypatch):
    monkeypatch.setattr(
        acquisition, "fetch", lambda *a, **k: (dict(address="seed", txs=[transaction()], hasMore=True), "h")
    )
    with pytest.raises(ProviderError, match="cursor"):
        acquisition.bitcoin("seed")
    assert len(acquisition.partial_events) == 2


def test_foreign_address_response_fails(acquisition, monkeypatch):
    monkeypatch.setattr(acquisition, "fetch", lambda *a, **k: (dict(address="wrong", txs=[]), "h"))
    with pytest.raises(ProviderError, match="mismatched"):
        acquisition.bitcoin("seed")
