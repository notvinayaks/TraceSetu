"""Receipt/block reconciliation for standard ERC-20 logs, not an ownership proof."""

import re
from .domain import Transfer

TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"


def quantity(value):
    if not isinstance(value, str) or not re.fullmatch(r"0x(?:0|[1-9a-fA-F][0-9a-fA-F]*)", value):
        raise ValueError("Invalid RPC quantity")
    return int(value, 16)


def data(value, size):
    if not isinstance(value, str) or not re.fullmatch("0x[0-9a-fA-F]{" + str(size * 2) + "}", value):
        raise ValueError("Invalid RPC data")
    return value.lower()


def erc20_transfers(chain, txhash, sender, contract, decimals, receipt, block, evidence):
    txhash = data(txhash, 32)
    sender, contract = data(sender, 20), data(contract, 20)
    if not isinstance(receipt, dict) or not isinstance(block, dict):
        raise ValueError("Receipt or block is unavailable; token flow is unverified")
    block_hash = data(receipt.get("blockHash"), 32)
    block_number = quantity(receipt.get("blockNumber"))
    tx_index = quantity(receipt.get("transactionIndex"))
    if data(receipt.get("transactionHash"), 32) != txhash:
        raise ValueError("Receipt belongs to a different transaction")
    if data(block.get("hash"), 32) != block_hash or quantity(block.get("number")) != block_number:
        raise ValueError("Receipt and current block disagree; possible reorganisation")
    transactions = block.get("transactions")
    if (
        not isinstance(transactions, list)
        or tx_index >= len(transactions)
        or data(transactions[tx_index], 32) != txhash
    ):
        raise ValueError("Transaction index does not match the acquired block")
    stamp = quantity(block.get("timestamp"))
    if receipt.get("status") == "0x0":
        return []
    if receipt.get("status") != "0x1":
        raise ValueError("Receipt success status is not established")
    logs = receipt.get("logs")
    if not isinstance(logs, list):
        raise ValueError("Receipt logs unavailable")
    result = {}
    for log in logs:
        if not isinstance(log, dict):
            raise ValueError("Malformed receipt log")
        topics = log.get("topics", [])
        if not isinstance(topics, list) or len(topics) != 3 or str(topics[0]).lower() != TRANSFER_TOPIC:
            continue  # ERC-721 and nonstandard events are outside this decoder.
        if data(log.get("address"), 20) != contract:
            continue
        source_word, destination_word = data(topics[1], 32), data(topics[2], 32)
        if source_word[2:26] != "0" * 24 or destination_word[2:26] != "0" * 24:
            raise ValueError("Indexed ERC-20 address is not correctly padded")
        if "0x" + source_word[-40:] != sender:
            continue
        if log.get("removed") is not False:
            raise ValueError("Removed or unqualified log cannot establish a token transfer")
        if (
            data(log.get("transactionHash"), 32) != txhash
            or data(log.get("blockHash"), 32) != block_hash
            or quantity(log.get("blockNumber")) != block_number
            or quantity(log.get("transactionIndex")) != tx_index
        ):
            raise ValueError("Log position disagrees with its receipt")
        index = quantity(log.get("logIndex"))
        event = Transfer(
            id=f"{chain}:{txhash}:log:{index}",
            chain=chain,
            txid=txhash,
            senders=[sender],
            recipient="0x" + destination_word[-40:],
            asset=chain + ":" + contract,
            amount=str(int(data(log.get("data"), 32), 16)),
            decimals=decimals,
            timestamp=stamp,
            position=[block_number, tx_index, index + 1],
            finality="confirmed",
            kind="token",
            evidence=evidence,
        )
        if index in result and result[index] != event:
            raise ValueError("Contradictory duplicate log index")
        result[index] = event
    return list(result.values())
