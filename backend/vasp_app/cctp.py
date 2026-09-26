"""Read-only CCTP V2 correlation under explicit provider/key trust assumptions.

Protocol references and registry provenance: docs/cctp.md. No mint or send methods.
"""

from eth_utils import keccak
from eth_keys import keys
from eth_keys.constants import SECPK1_N
from eth_keys.exceptions import BadSignature
from .domain import Transfer
from .evm_receipts import data, quantity, erc20_transfers

REGISTRY_VERSION = "circle-cctp-evm-2026-09-24"
TRANSMITTER = "0x81d40f21f12a8f0e3252bccb954d722d4c464b64"
MESSENGER = "0x28b5a0e9c621a5badaa536219b3a228c8168cf5d"
REGISTRY = {
    "ethereum": {"domain": 0, "chainid": 1, "usdc": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"},
    "polygon": {"domain": 7, "chainid": 137, "usdc": "0x3c499c542cef5e3811e1192ce70d8cc03d5c3359"},
}
SENT_TOPIC = "0x" + keccak(text="MessageSent(bytes)").hex()
RECEIVED_TOPIC = "0x" + keccak(text="MessageReceived(address,uint32,bytes32,bytes32,uint32,bytes)").hex()
ZERO = "0x" + "0" * 40


def blob(value, maximum=16384):
    if (
        not isinstance(value, str)
        or not value.startswith("0x")
        or len(value) % 2
        or len(value) > maximum * 2 + 2
    ):
        raise ValueError("Malformed or oversized protocol bytes")
    return bytes.fromhex(value[2:])


def address_word(value):
    if len(value) != 32 or value[:12] != bytes(12):
        raise ValueError("Non-EVM or malformed address word")
    return "0x" + value[12:].hex()


def dynamic_bytes(encoded, offset_word, expected_offset):
    offset = int.from_bytes(encoded[offset_word * 32 : (offset_word + 1) * 32], "big")
    if offset != expected_offset or len(encoded) < offset + 32:
        raise ValueError("Invalid ABI bytes offset")
    length = int.from_bytes(encoded[offset : offset + 32], "big")
    end = offset + 32 + length
    padded = offset + 32 + ((length + 31) // 32) * 32
    if end > len(encoded) or len(encoded) != padded or any(encoded[end:padded]):
        raise ValueError("Invalid ABI bytes length or padding")
    return encoded[offset + 32 : end]


def parse_message(raw):
    if len(raw) < 376 or len(raw) > 16384:
        raise ValueError("Unsupported CCTP V2 message length")

    def u(a, b):
        return int.from_bytes(raw[a:b], "big")

    if u(0, 4) != 1 or u(148, 152) != 1:
        raise ValueError("Only CCTP V2 header/body version 1 is supported")
    return {
        "source_domain": u(4, 8),
        "destination_domain": u(8, 12),
        "nonce": "0x" + raw[12:44].hex(),
        "sender": address_word(raw[44:76]),
        "recipient": address_word(raw[76:108]),
        "destination_caller": address_word(raw[108:140]),
        "minimum_finality": u(140, 144),
        "executed_finality": u(144, 148),
        "burn_token": address_word(raw[152:184]),
        "mint_recipient": address_word(raw[184:216]),
        "amount": u(216, 248),
        "message_sender": address_word(raw[248:280]),
        "max_fee": u(280, 312),
        "fee": u(312, 344),
        "expiration_block": u(344, 376),
        "hook_data": "0x" + raw[376:].hex(),
    }


def emitted_form(raw):
    result = bytearray(raw)
    for start, end in [(12, 44), (144, 148), (312, 344), (344, 376)]:
        result[start:end] = bytes(end - start)
    return bytes(result)


def verify_signatures(message, attestation, public_keys):
    signature = blob(attestation, 65 * 16)
    if not signature or len(signature) % 65:
        raise ValueError("Invalid CCTP attestation length")
    supplied = public_keys.get("publicKeys")
    if not isinstance(supplied, list) or not 1 <= len(supplied) <= 32:
        raise ValueError("CCTP key evidence unavailable")
    allowed = set()
    for item in supplied:
        if not isinstance(item, dict):
            raise ValueError("Malformed CCTP key entry")
        if item.get("cctpVersion") == 2:
            raw = blob(item.get("publicKey"), 65)
            if len(raw) != 65 or raw[0] != 4:
                raise ValueError("Malformed CCTP uncompressed public key")
            allowed.add(keys.PublicKey(raw[1:]).to_canonical_address())
    recovered = []
    for i in range(0, len(signature), 65):
        sig = signature[i : i + 65]
        r, s, v = int.from_bytes(sig[:32], "big"), int.from_bytes(sig[32:64], "big"), sig[64]
        if v not in (27, 28) or not 0 < r < SECPK1_N or not 0 < s <= SECPK1_N // 2:
            raise ValueError("Invalid or noncanonical CCTP signature")
        try:
            signer = (
                keys.Signature(vrs=(v - 27, r, s))
                .recover_public_key_from_msg_hash(keccak(message))
                .to_canonical_address()
            )
        except BadSignature as exc:
            raise ValueError("Invalid CCTP signature recovery") from exc
        if signer not in allowed or (recovered and signer <= recovered[-1]):
            raise ValueError("Unrecognised, duplicated or unsorted CCTP attester")
        recovered.append(signer)
    return ["0x" + signer.hex() for signer in recovered]


def receipt_context(receipt, block, txhash):
    txhash = data(txhash, 32)
    if receipt.get("status") != "0x1" or data(receipt.get("transactionHash"), 32) != txhash:
        raise ValueError("Successful transaction receipt required")
    number, index = quantity(receipt.get("blockNumber")), quantity(receipt.get("transactionIndex"))
    block_hash = data(receipt.get("blockHash"), 32)
    if block_hash != data(block.get("hash"), 32) or number != quantity(block.get("number")):
        raise ValueError("Receipt/block disagreement or reorganisation")
    transactions = block.get("transactions", [])
    if (
        not isinstance(transactions, list)
        or index >= len(transactions)
        or data(transactions[index], 32) != txhash
    ):
        raise ValueError("Receipt transaction not at its claimed block position")
    logs = receipt.get("logs")
    if not isinstance(logs, list) or len(logs) > 10000:
        raise ValueError("Receipt log evidence unavailable or oversized")
    indexes = set()
    for log in logs:
        if not isinstance(log, dict):
            raise ValueError("Malformed receipt log")
        log_index = qualified_log(log, receipt)
        if log_index in indexes:
            raise ValueError("Duplicate receipt log position is ambiguous")
        indexes.add(log_index)
    return number, index, quantity(block.get("timestamp"))


def qualified_log(log, receipt):
    if log.get("removed") is not False:
        raise ValueError("Removed or unqualified bridge log")
    for field in ("transactionHash", "blockHash"):
        if data(log.get(field), 32) != data(receipt.get(field), 32):
            raise ValueError("Bridge log identity mismatch")
    for field in ("blockNumber", "transactionIndex"):
        if quantity(log.get(field)) != quantity(receipt.get(field)):
            raise ValueError("Bridge log position mismatch")
    return quantity(log.get("logIndex"))


def sent_messages(receipt):
    result = []
    for log in receipt.get("logs", []):
        if not isinstance(log, dict):
            raise ValueError("Malformed source log")
        if str(log.get("address", "")).lower() == TRANSMITTER and log.get("topics") == [SENT_TOPIC]:
            index = qualified_log(log, receipt)
            result.append((index, dynamic_bytes(blob(log["data"]), 0, 32)))
    return result


def verify_bridge(proof):
    if proof.registry_version != REGISTRY_VERSION or proof.source_chain == proof.destination_chain:
        raise ValueError("Unsupported bridge registry or same-domain transfer")
    src, dst = REGISTRY[proof.source_chain], REGISTRY[proof.destination_chain]
    source_position = receipt_context(proof.source_receipt, proof.source_block, proof.source_txhash)
    destination_position = receipt_context(
        proof.destination_receipt, proof.destination_block, proof.destination_txhash
    )
    if destination_position[2] < source_position[2]:
        raise ValueError("Cross-chain block time order is ambiguous; manual review required")
    iris = proof.iris_response
    if data(iris.get("sourceTxHash"), 32) != data(proof.source_txhash, 32):
        raise ValueError("Circle response belongs to a different source transaction")
    nonce = data(proof.nonce, 32)
    matches = []
    messages = iris.get("messages")
    if not isinstance(messages, list) or len(messages) > 100:
        raise ValueError("Message evidence unavailable or exceeds the supported bound")
    for row in messages:
        if not isinstance(row, dict):
            raise ValueError("Malformed message entry")
        if row.get("cctpVersion") == 2 and row.get("status") == "complete":
            message = blob(row.get("message"))
            if len(message) >= 44 and "0x" + message[12:44].hex() == nonce:
                matches.append((row, message))
    if len(matches) != 1:
        raise ValueError("Exactly one complete attested message must match the nonce")
    row, message = matches[0]
    m = parse_message(message)
    if (m["source_domain"], m["destination_domain"], m["sender"], m["recipient"], m["burn_token"]) != (
        src["domain"],
        dst["domain"],
        MESSENGER,
        MESSENGER,
        src["usdc"],
    ):
        raise ValueError("Message does not match the supported CCTP token/domain contracts")
    required_finality = 1000 if m["minimum_finality"] <= 1000 else 2000
    if (
        int(nonce, 16) == 0
        or m["executed_finality"] not in (1000, 2000)
        or m["executed_finality"] < required_finality
    ):
        raise ValueError("Invalid message nonce or attested finality")
    if not 0 <= m["fee"] <= m["max_fee"] < m["amount"]:
        raise ValueError("Invalid CCTP fee or amount")
    if m["mint_recipient"] == ZERO or (
        m["expiration_block"] and destination_position[0] >= m["expiration_block"]
    ):
        raise ValueError("Zero mint recipient or expired destination message")
    signers = verify_signatures(message, row.get("attestation"), proof.public_keys)
    sent = [
        (index, raw) for index, raw in sent_messages(proof.source_receipt) if raw == emitted_form(message)
    ]
    if len(sent) != 1:
        raise ValueError("Source MessageSent is missing or ambiguous")
    received, prior_indexes = [], []
    for log in proof.destination_receipt["logs"]:
        topics = log.get("topics", [])
        if str(log.get("address", "")).lower() != TRANSMITTER or not topics or topics[0] != RECEIVED_TOPIC:
            continue
        index = qualified_log(log, proof.destination_receipt)
        prior_indexes.append(index)
        if len(topics) != 4 or data(topics[2], 32) != nonce:
            continue
        encoded = blob(log.get("data"))
        if len(encoded) < 128:
            raise ValueError("Malformed MessageReceived ABI")
        if int.from_bytes(encoded[:32], "big") != src["domain"] or address_word(encoded[32:64]) != MESSENGER:
            raise ValueError("MessageReceived source mismatch")
        if (
            int(data(topics[3], 32), 16) != m["executed_finality"]
            or dynamic_bytes(encoded, 2, 96) != message[148:]
        ):
            raise ValueError("MessageReceived finality/body mismatch")
        if (
            m["destination_caller"] != ZERO
            and address_word(bytes.fromhex(data(topics[1], 32)[2:])) != m["destination_caller"]
        ):
            raise ValueError("Destination caller restriction violated")
        received.append(index)
    if len(received) != 1:
        raise ValueError("Destination MessageReceived is missing or ambiguous")
    before = max((i for i in prior_indexes if i < received[0]), default=-1)
    net = m["amount"] - m["fee"]
    mints = erc20_transfers(
        proof.destination_chain,
        proof.destination_txhash,
        ZERO,
        dst["usdc"],
        6,
        proof.destination_receipt,
        proof.destination_block,
        proof.evidence,
    )
    mints = [
        e
        for e in mints
        if e.recipient == m["mint_recipient"]
        and int(e.amount) == net
        and before < e.position[2] - 1 < received[0]
    ]
    if len(mints) != 1:
        raise ValueError("Exactly one matching net USDC mint must precede receipt acceptance")
    event = Transfer(
        id="cctp-v2:" + str(src["domain"]) + ":" + nonce,
        chain=proof.source_chain,
        txid=proof.source_txhash.lower(),
        senders=[m["message_sender"]],
        recipient=m["mint_recipient"],
        asset=proof.source_chain + ":" + src["usdc"],
        amount=str(net),
        decimals=6,
        timestamp=source_position[2],
        position=[source_position[0], source_position[1], sent[0][0] + 1],
        finality="confirmed",
        kind="bridge",
        evidence=proof.evidence,
        destination_chain=proof.destination_chain,
        destination_asset=proof.destination_chain + ":" + dst["usdc"],
        bridge_proof=proof.id,
    )
    return {
        "event": event,
        "destination_timestamp": destination_position[2],
        "destination_position": mints[0].position,
        "destination_txhash": proof.destination_txhash,
        "mint_event_id": mints[0].id,
        "burned_amount": str(m["amount"]),
        "fee_amount": str(m["fee"]),
        "minted_amount": str(net),
        "attestation_signers": signers,
        "attestation_finality": m["executed_finality"],
        "hook_data": m["hook_data"],
        "trust": "Protocol/receipt consistency and signatures against supplied key evidence; provider/key identity and chain consensus remain external trust assumptions. Destination receipt acceptance supplies the on-chain threshold check; no key-count quorum is invented.",
    }
