import copy
import pytest
from vasp_app.evm_receipts import erc20_transfers, TRANSFER_TOPIC

TX = "0x" + "a" * 64
BLOCK = "0x" + "b" * 64
SENDER = "0x" + "1" * 40
CONTRACT = "0x" + "3" * 40


def sample():
    log = {
        "address": CONTRACT,
        "topics": [TRANSFER_TOPIC, "0x" + "0" * 24 + "1" * 40, "0x" + "0" * 24 + "2" * 40],
        "data": "0x" + format(2**255 + 17, "064x"),
        "blockHash": BLOCK,
        "blockNumber": "0x5",
        "transactionHash": TX,
        "transactionIndex": "0x0",
        "logIndex": "0x2",
        "removed": False,
    }
    receipt = {
        "transactionHash": TX,
        "blockHash": BLOCK,
        "blockNumber": "0x5",
        "transactionIndex": "0x0",
        "status": "0x1",
        "logs": [log],
    }
    block = {"hash": BLOCK, "number": "0x5", "timestamp": "0x6e", "transactions": [TX]}
    return receipt, block


def decode(receipt, block):
    return erc20_transfers(
        "ethereum", TX, SENDER, CONTRACT, 6, receipt, block, ["synthetic-receipt", "synthetic-block"]
    )


def test_exact_receipt_amount_position_and_stable_identity():
    receipt, block = sample()
    result = decode(receipt, block)
    assert result[0].amount == str(2**255 + 17)
    assert result[0].id == f"ethereum:{TX}:log:2"
    assert result[0].position == [5, 0, 3]
    assert result[0].timestamp == 110
    receipt["logs"].append(copy.deepcopy(receipt["logs"][0]))
    assert len(decode(receipt, block)) == 1


@pytest.mark.parametrize(
    "mutation",
    [
        "reorg",
        "wrong_tx",
        "wrong_position",
        "removed",
        "missing_removed",
        "bad_padding",
        "conflicting_log",
        "status_missing",
    ],
)
def test_inconsistent_or_unqualified_receipts_cannot_become_transfers(mutation):
    receipt, block = sample()
    if mutation == "reorg":
        block["hash"] = "0x" + "c" * 64
    elif mutation == "wrong_tx":
        receipt["transactionHash"] = "0x" + "c" * 64
    elif mutation == "wrong_position":
        block["transactions"] = []
    elif mutation == "removed":
        receipt["logs"][0]["removed"] = True
    elif mutation == "missing_removed":
        receipt["logs"][0].pop("removed")
    elif mutation == "bad_padding":
        receipt["logs"][0]["topics"][1] = "0x" + "f" * 24 + "1" * 40
    elif mutation == "conflicting_log":
        row = copy.deepcopy(receipt["logs"][0])
        row["data"] = "0x" + "1" * 64
        receipt["logs"].append(row)
    elif mutation == "status_missing":
        receipt.pop("status")
    with pytest.raises(ValueError):
        decode(receipt, block)


def test_failed_transactions_and_nft_event_shape_do_not_create_erc20_flow():
    receipt, block = sample()
    receipt["status"] = "0x0"
    assert decode(receipt, block) == []
    receipt["status"] = "0x1"
    receipt["logs"][0]["topics"].append("0x" + "0" * 64)
    receipt["logs"][0]["data"] = "0x"
    assert decode(receipt, block) == []
