"""Synthetic protocol exercise. The key, receipts and wallets are NOT live evidence.

Uses real wire layouts with a deliberately local, deterministic test attester.
Never called by live acquisition or substituted when a provider fails.
"""

from eth_keys import keys
from eth_utils import keccak
from .domain import BridgeProof, Snapshot
from .cctp import MESSENGER, TRANSMITTER, REGISTRY, SENT_TOPIC, RECEIVED_TOPIC, ZERO
from .evm_receipts import TRANSFER_TOPIC

SEED = "0x" + "11" * 20
RECIPIENT = "0x" + "22" * 20
DEPOSIT = "0x" + "33" * 20
START = 1750000000


def word(n):
    return n.to_bytes(32, "big")


def addr(a):
    return bytes(12) + bytes.fromhex(a[2:])


def hx(value):
    return "0x" + value.hex()


def dynamic(value):
    return word(len(value)) + value + bytes((-len(value)) % 32)


def synthetic_proof(source="ethereum", fee=10000):
    destination = "polygon" if source == "ethereum" else "ethereum"
    src, dst = REGISTRY[source], REGISTRY[destination]
    nonce = bytes.fromhex("42" * 32)
    header = (1).to_bytes(4, "big") + src["domain"].to_bytes(4, "big") + dst["domain"].to_bytes(4, "big")
    header += bytes(32) + addr(MESSENGER) + addr(MESSENGER) + addr(ZERO)
    header += (1000).to_bytes(4, "big") + bytes(4)
    body = (1).to_bytes(4, "big") + addr(src["usdc"]) + addr(RECIPIENT) + word(1000000)
    body += addr(SEED) + word(20000) + word(0) + word(0)
    emitted = header + body
    message = bytearray(emitted)
    message[12:44] = nonce
    message[144:148] = (1000).to_bytes(4, "big")
    message[312:344] = word(fee)
    message[344:376] = word(1000)
    message = bytes(message)
    # Publicly known synthetic key; it authenticates no real Circle identity.
    signer = keys.PrivateKey(bytes.fromhex("01" * 32))
    sig = signer.sign_msg_hash(keccak(message))
    attestation = sig.r.to_bytes(32, "big") + sig.s.to_bytes(32, "big") + bytes([sig.v + 27])

    def receipt(n, stamp, tx, logs):
        blockhash = "0x" + ("aa" if n == 100 else "bb") * 32
        base = dict(transactionHash=tx, blockHash=blockhash, blockNumber=hex(n), transactionIndex="0x0")
        return {
            **base,
            "status": "0x1",
            "logs": [{**base, "logIndex": hex(i), "removed": False, **log} for i, log in enumerate(logs)],
        }, dict(hash=blockhash, number=hex(n), timestamp=hex(stamp), transactions=[tx])

    source_tx, destination_tx = "0x" + "ab" * 32, "0x" + "cd" * 32
    source_receipt, source_block = receipt(
        100,
        START + 10,
        source_tx,
        [
            dict(
                address=src["usdc"],
                topics=[TRANSFER_TOPIC, hx(addr(SEED)), hx(addr(ZERO))],
                data=hx(word(1000000)),
            ),
            dict(address=TRANSMITTER, topics=[SENT_TOPIC], data=hx(word(32) + dynamic(emitted))),
        ],
    )
    destination_receipt, destination_block = receipt(
        200,
        START + 30,
        destination_tx,
        [
            dict(
                address=dst["usdc"],
                topics=[TRANSFER_TOPIC, hx(addr(ZERO)), hx(addr(RECIPIENT))],
                data=hx(word(1000000 - fee)),
            ),
            dict(
                address=TRANSMITTER,
                topics=[RECEIVED_TOPIC, hx(addr(SEED)), hx(nonce), hx(word(1000))],
                data=hx(word(src["domain"]) + addr(MESSENGER) + word(96) + dynamic(message[148:])),
            ),
        ],
    )
    return BridgeProof(
        id="fixture-cctp-proof",
        source_chain=source,
        destination_chain=destination,
        source_txhash=source_tx,
        destination_txhash=destination_tx,
        nonce=hx(nonce),
        source_receipt=source_receipt,
        source_block=source_block,
        destination_receipt=destination_receipt,
        destination_block=destination_block,
        iris_response={
            "sourceTxHash": source_tx,
            "messages": [
                {
                    "cctpVersion": 2,
                    "status": "complete",
                    "message": hx(message),
                    "attestation": hx(attestation),
                    "forwardTxHash": destination_tx,
                }
            ],
        },
        public_keys={
            "publicKeys": [{"cctpVersion": 2, "publicKey": hx(b"\x04" + signer.public_key.to_bytes())}]
        },
        evidence=["SYNTHETIC-CCTP-V2-NOT-LIVE-EVIDENCE"],
        grade="hypothesis",
        source_family="synthetic-cctp-v2",
    )


def bridge_snapshot():
    proof = synthetic_proof()
    return Snapshot.model_validate(
        dict(
            schema_version="1.1",
            mode="fixture",
            origin="Synthetic CCTP V2 review exercise; local test attester, invented receipts and service label",
            collected_at=START + 1000,
            window_start=START,
            window_end=START + 1000,
            bridge_proofs=[proof.model_dump()],
            events=[
                dict(
                    id="fixture-polygon-deposit",
                    chain="polygon",
                    txid="0x" + "ef" * 32,
                    senders=[RECIPIENT],
                    recipient=DEPOSIT,
                    asset="polygon:" + REGISTRY["polygon"]["usdc"],
                    amount="900000",
                    decimals=6,
                    timestamp=START + 40,
                    position=[201, 0, 1],
                    kind="token",
                    evidence=["synthetic-deposit-event"],
                )
            ],
            assertions=[
                dict(
                    id="fixture-cctp-custody",
                    chain="polygon",
                    address=DEPOSIT,
                    entity="Example Cross-chain Exchange",
                    category="exchange",
                    role="deposit",
                    grade="reviewed",
                    source_family="fixture-directory",
                    source="Synthetic training label",
                    evidence=["synthetic-label"],
                )
            ],
            coverage=[
                dict(
                    chain=c,
                    address=a,
                    status="complete",
                    reason="Complete within this invented exercise only",
                )
                for c, a in [("ethereum", SEED), ("polygon", RECIPIENT)]
            ],
            limitations=[
                "All receipts, signatures and labels in this exercise are synthetic. Protocol consistency does not authenticate the synthetic key as Circle. Review is for training only."
            ],
        )
    )
