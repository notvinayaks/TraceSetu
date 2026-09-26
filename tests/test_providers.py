"""Parser/transport tests use explicit fixtures. They do not constitute live API validation."""

import json
import httpx
import pytest
from vasp_app.domain import TraceSpec
from vasp_app.providers import Acquisition, ProviderError, BudgetExhausted
from vasp_app.config import settings
from vasp_app.store import read_artifact


def spec(chain, address="0x" + "1" * 40):
    return TraceSpec(chain=chain, address=address, start=100, end=200, max_requests=20)


def transport(acquisition, payload, status=200):
    acquisition.client.close()
    acquisition.client = httpx.Client(
        transport=httpx.MockTransport(lambda req: httpx.Response(status, json=payload))
    )


def test_transport_exact_evidence_budget_and_within_job_cache():
    a = Acquisition(spec("ethereum"))
    a.spec.max_requests = 1
    transport(a, {"integer": "10000000000000000001"})
    payload, h = a.fetch("test", "https://example.invalid/read")
    assert read_artifact(h) == json.dumps(payload, separators=(",", ":")).encode()
    assert a.fetch("test", "https://example.invalid/read")[1] == h
    assert a.calls == 1
    assert a.cache_hits == 1
    with pytest.raises(BudgetExhausted):
        a.fetch("test", "https://example.invalid/other")
    a.close()


def test_provider_http_failure_explicit():
    a = Acquisition(spec("ethereum"))
    transport(a, {"error": "rate limited"}, 429)
    with pytest.raises(ProviderError, match="HTTP 429"):
        a.fetch("test", "https://example.invalid/read")
    a.close()


def test_bitcoin_preserves_input_set_outpoints_outputs_and_exact_values(monkeypatch):
    a = Acquisition(spec("bitcoin", "sender"))
    tx = {
        "txid": "tx1",
        "status": {"confirmed": True, "block_time": 110},
        "vin": [
            {"txid": "prior", "vout": 2, "prevout": {"scriptpubkey_address": "sender", "value": 800}},
            {"txid": "other", "vout": 1, "prevout": {"scriptpubkey_address": "other-owner", "value": 500}},
        ],
        "vout": [
            {"scriptpubkey_address": "target", "value": 1200},
            {"scriptpubkey_address": "change-unknown", "value": 90},
        ],
    }
    monkeypatch.setattr(a, "fetch", lambda *args, **kwargs: ([tx], "rawhash"))
    events, c = a.bitcoin("sender")
    assert len(events) == 2
    assert events[0].amount == "1200"
    assert events[0].output_index == 0
    assert events[0].senders == ["sender", "other-owner"]
    assert events[0].input_outpoints == ["prior:2", "other:1"]
    assert c.status == "complete"
    a.close()


@pytest.mark.parametrize("chain", ["ethereum", "bnb", "polygon"])
def test_evm_native_internal_token_are_separate_and_partial(monkeypatch, chain):
    monkeypatch.setattr(settings, "etherscan_api_key", "test-not-a-real-key")
    a = Acquisition(spec(chain))
    actions = []

    def fetch(*args, **kwargs):
        action = kwargs["params"]["action"]
        actions.append(action)
        txhash = "0x" + "a" * 64
        blockhash = "0x" + "b" * 64
        if action == "eth_getTransactionReceipt":
            from vasp_app.evm_receipts import TRANSFER_TOPIC

            return {
                "result": {
                    "transactionHash": txhash,
                    "blockHash": blockhash,
                    "blockNumber": "0x5",
                    "transactionIndex": "0x0",
                    "status": "0x1",
                    "logs": [
                        {
                            "address": "0x" + "3" * 40,
                            "topics": [
                                TRANSFER_TOPIC,
                                "0x" + "0" * 24 + "1" * 40,
                                "0x" + "0" * 24 + "2" * 40,
                            ],
                            "data": "0x" + format(12345678901234567890, "064x"),
                            "blockNumber": "0x5",
                            "transactionIndex": "0x0",
                            "transactionHash": txhash,
                            "blockHash": blockhash,
                            "logIndex": "0x2",
                            "removed": False,
                        }
                    ],
                }
            }, "receipt-evidence"
        if action == "eth_getBlockByNumber":
            assert kwargs["params"]["boolean"] == "false"
            return {
                "result": {"hash": blockhash, "number": "0x5", "timestamp": "0x6e", "transactions": [txhash]}
            }, "block-evidence"
        row = {
            "hash": txhash,
            "from": a.spec.address,
            "to": "0x" + "2" * 40,
            "timeStamp": "110",
            "blockNumber": "5",
            "value": "12345678901234567890",
            "transactionIndex": "0",
            "isError": "0",
        }
        if action == "tokentx":
            row.update(contractAddress="0x" + "3" * 40, tokenDecimal="6")
        if action == "txlistinternal":
            row.update(traceId="0_1")
        return {"status": "1", "result": [row]}, "raw-" + action

    monkeypatch.setattr(a, "fetch", fetch)
    events, c = a.evm(chain, a.spec.address)
    assert {e.kind for e in events} == {"native", "internal", "token"}
    assert len({e.id for e in events}) == 3
    assert events[2].decimals == 6
    assert events[2].amount == "12345678901234567890"
    assert events[2].position == [5, 0, 3]
    assert events[2].evidence == ["raw-tokentx", "receipt-evidence", "block-evidence"]
    assert c.status == "partial"
    a.close()


def test_tron_approvals_are_not_transfer_events(monkeypatch):
    a = Acquisition(spec("tron", "owner"))

    def fetch(*args, **kwargs):
        if args[1].endswith("/trc20"):
            return {
                "success": True,
                "data": [
                    {"type": "Approval", "from": "owner"},
                    {
                        "type": "Transfer",
                        "from": "owner",
                        "to": "recipient",
                        "value": "1234567890123456789",
                        "transaction_id": "tx",
                        "block_timestamp": 110000,
                        "token_info": {"address": "token", "decimals": 6},
                    },
                ],
                "meta": {},
            }, "trc20-evidence"
        return {"success": True, "data": [], "meta": {}}, "native-evidence"

    monkeypatch.setattr(a, "fetch", fetch)
    events, c = a.tron("owner")
    assert len(events) == 1
    assert events[0].kind == "token"
    assert events[0].amount == "1234567890123456789"
    assert c.status == "partial"
    a.close()


def test_solana_inner_instruction_and_historical_owner(monkeypatch):
    a = Acquisition(spec("solana", "wallet"))

    def fetch(*args, **kwargs):
        if kwargs["body"]["method"] == "getSignaturesForAddress":
            return {
                "result": [{"signature": "signature", "blockTime": 110, "err": None}]
            }, "signature-evidence"
        return {
            "result": {
                "transaction": {
                    "message": {
                        "accountKeys": [{"pubkey": "token-account"}, {"pubkey": "other-token-account"}],
                        "instructions": [],
                    }
                },
                "meta": {
                    "err": None,
                    "preTokenBalances": [
                        {
                            "accountIndex": 0,
                            "owner": "wallet",
                            "mint": "mint",
                            "uiTokenAmount": {"decimals": 6},
                        },
                        {
                            "accountIndex": 1,
                            "owner": "destination",
                            "mint": "mint",
                            "uiTokenAmount": {"decimals": 6},
                        },
                    ],
                    "innerInstructions": [
                        {
                            "index": 1,
                            "instructions": [
                                {
                                    "program": "spl-token",
                                    "parsed": {
                                        "type": "transfer",
                                        "info": {
                                            "source": "token-account",
                                            "destination": "other-token-account",
                                            "amount": "101",
                                        },
                                    },
                                }
                            ],
                        }
                    ],
                },
            }
        }, "tx-evidence"

    monkeypatch.setattr(a, "fetch", fetch)
    events, c = a.solana("wallet")
    assert len(events) == 1
    assert events[0].senders == ["wallet"]
    assert events[0].recipient == "destination"
    assert "inner:1:0" in events[0].id
    assert c.status == "partial"
    a.close()


def test_current_metadata_is_not_historical_ownership(monkeypatch):
    monkeypatch.setattr(settings, "etherscan_api_key", "test-not-a-real-key")
    a = Acquisition(spec("ethereum"))
    monkeypatch.setattr(
        a,
        "fetch",
        lambda *args, **kwargs: (
            {
                "status": "1",
                "result": [
                    {
                        "address": a.spec.address,
                        "nametag": "Provider Exchange 10",
                        "labels_slug": ["exchange"],
                        "lastupdatedtimestamp": 199,
                    }
                ],
            },
            "metadata-evidence",
        ),
    )
    rows = a.evm_metadata("ethereum", a.spec.address)
    assert rows[0].category == "exchange"
    assert rows[0].grade == "hypothesis"
    assert rows[0].role == "unknown"
    a.close()


def test_budget_failure_retains_previously_acquired_pages(monkeypatch):
    monkeypatch.setattr(settings, "etherscan_api_key", "test-not-a-real-key")
    a = Acquisition(spec("ethereum"))

    def fetch(*args, **kwargs):
        if kwargs["params"]["action"] != "txlist":
            raise BudgetExhausted("Request budget exhausted")
        return {
            "status": "1",
            "result": [
                {
                    "hash": "tx",
                    "from": a.spec.address,
                    "to": "0x" + "2" * 40,
                    "timeStamp": "110",
                    "blockNumber": "5",
                    "value": "100",
                    "transactionIndex": "0",
                    "isError": "0",
                }
            ],
        }, "first-page-evidence"

    monkeypatch.setattr(a, "fetch", fetch)
    snapshot = a.collect([])
    assert len(snapshot.events) == 1
    assert snapshot.events[0].amount == "100"
    assert snapshot.coverage[0].status == "partial"
    assert snapshot.coverage[0].cursor == "txlistinternal:1"
    assert "earlier pages retained" in snapshot.coverage[0].reason
    a.close()


@pytest.mark.parametrize("failure", ["unavailable", "budget"])
def test_unverified_indexed_token_is_never_substituted_for_missing_receipt(monkeypatch, failure):
    monkeypatch.setattr(settings, "etherscan_api_key", "synthetic-key")
    a = Acquisition(spec("ethereum"))

    def fetch(*args, **kwargs):
        action = kwargs["params"]["action"]
        if action == "eth_getTransactionReceipt":
            if failure == "budget":
                raise BudgetExhausted("Request budget exhausted")
            return {"result": None}, "missing-receipt"
        if action != "tokentx":
            return {"status": "1", "result": []}, "empty-index"
        return {
            "status": "1",
            "result": [
                {
                    "hash": "0x" + "a" * 64,
                    "from": a.spec.address,
                    "to": "0x" + "2" * 40,
                    "timeStamp": "110",
                    "blockNumber": "5",
                    "value": "99999",
                    "contractAddress": "0x" + "3" * 40,
                    "tokenDecimal": "6",
                }
            ],
        }, "index-only"

    monkeypatch.setattr(a, "fetch", fetch)
    snapshot = a.collect([])
    assert snapshot.events == []
    assert snapshot.coverage[0].status == "partial"
    assert snapshot.coverage[0].cursor.startswith("receipt:")
    a.close()
