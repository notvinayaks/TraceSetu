"""Versioned evidence contract. Amounts are integer strings, never floats."""

from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

Chain = Literal["bitcoin", "ethereum", "tron", "bnb", "solana", "polygon"]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Transfer(Contract):
    id: str = Field(min_length=1, max_length=240)
    chain: Chain
    txid: str = Field(min_length=1, max_length=160)
    senders: list[str] = Field(min_length=1, max_length=1000)
    recipient: str
    asset: str
    amount: str = Field(pattern=r"^\d{1,80}$")
    decimals: int = Field(ge=0, le=36)
    timestamp: int = Field(ge=0)
    # Canonical ledger order, where available. Missing order cannot establish same-second causality.
    position: list[int] | None = None
    finality: Literal["finalized", "confirmed", "pending", "orphaned"] = "confirmed"
    success: bool = True
    kind: Literal["native", "token", "internal", "utxo", "bridge"] = "native"
    evidence: list[str] = Field(min_length=1)
    input_outpoints: list[str] = []
    output_index: int | None = Field(default=None, ge=0)
    destination_chain: Chain | None = None
    destination_asset: str | None = None
    bridge_proof: str | None = None

    @model_validator(mode="after")
    def structure(self):
        if self.kind == "utxo" and self.chain != "bitcoin":
            raise ValueError("UTXO records require the Bitcoin chain")
        if len(self.senders) > 1 and self.kind != "utxo":
            raise ValueError("Account transfers have one sender")
        if self.kind == "bridge" and not (
            self.destination_chain and self.destination_asset and self.bridge_proof
        ):
            raise ValueError("Cross-chain links require destination and explicit reviewed proof")
        if self.position is not None and (len(self.position) != 3 or min(self.position) < 0):
            raise ValueError("Position must be [block, transaction index, event index]")
        return self


class Assertion(Contract):
    id: str
    chain: Chain
    address: str
    entity: str = Field(min_length=1, max_length=160)
    category: Literal["exchange", "custodian", "mixer", "bridge", "defi", "unknown"]
    role: Literal["deposit", "hot", "cluster", "contract", "unknown"] = "unknown"
    grade: Literal["reviewed", "provider", "hypothesis"] = "hypothesis"
    source_family: str = Field(min_length=1, max_length=160)
    source: str = Field(min_length=1, max_length=500)
    evidence: list[str] = Field(min_length=1)
    valid_from: int = Field(default=0, ge=0)
    valid_to: int | None = Field(default=None, ge=0)
    risk_tags: list[str] = []

    @model_validator(mode="after")
    def interval(self):
        if self.valid_to is not None and self.valid_to < self.valid_from:
            raise ValueError("Assertion validity interval is reversed")
        return self


class Coverage(Contract):
    chain: Chain
    address: str
    status: Literal["complete", "partial", "unavailable", "not_fetched"]
    reason: str
    pages: int = Field(default=0, ge=0)
    evidence: list[str] = []
    cursor: str | None = None


class BridgeProof(Contract):
    id: str = Field(min_length=1, max_length=160)
    protocol: Literal["cctp-v2"] = "cctp-v2"
    registry_version: Literal["circle-cctp-evm-2026-09-24"] = "circle-cctp-evm-2026-09-24"
    source_chain: Literal["ethereum", "polygon"]
    destination_chain: Literal["ethereum", "polygon"]
    source_txhash: str
    destination_txhash: str
    nonce: str
    source_receipt: dict
    source_block: dict
    destination_receipt: dict
    destination_block: dict
    iris_response: dict
    public_keys: dict
    evidence: list[str] = Field(min_length=1, max_length=20)
    grade: Literal["reviewed", "provider", "hypothesis"] = "hypothesis"
    source_family: str = Field(default="circle-cctp-v2", min_length=1, max_length=160)


class ReconciliationGap(Contract):
    chain: Chain
    address: str
    event_id: str = Field(min_length=1, max_length=240)
    reason: str = Field(min_length=1, max_length=500)
    evidence: list[str] = Field(min_length=1, max_length=40)


class Snapshot(Contract):
    schema_version: Literal["1.0", "1.1", "1.2"] = "1.0"
    mode: Literal["live", "imported", "fixture"]
    origin: str
    collected_at: int
    events: list[Transfer] = Field(default_factory=list, max_length=20000)
    assertions: list[Assertion] = Field(default_factory=list, max_length=20000)
    coverage: list[Coverage] = Field(default_factory=list, max_length=5000)
    # Omitting the empty extension preserves canonical 1.0 snapshots for old bundle replay.
    bridge_proofs: list[BridgeProof] = Field(default_factory=list, max_length=100, exclude_if=lambda v: not v)
    reconciliation_gaps: list[ReconciliationGap] = Field(
        default_factory=list, max_length=20000, exclude_if=lambda v: not v
    )
    limitations: list[str] = []
    # The acquisition window is part of the evidence and cannot silently be extended.
    window_start: int = 0
    window_end: int = Field(ge=1)

    @model_validator(mode="after")
    def unique(self):
        if self.bridge_proofs and self.schema_version not in ("1.1", "1.2"):
            raise ValueError("Bridge proofs require snapshot schema 1.1 or later")
        if self.reconciliation_gaps and self.schema_version != "1.2":
            raise ValueError("Reconciliation gaps require snapshot schema 1.2")
        if self.window_start >= self.window_end:
            raise ValueError("Snapshot window must be increasing")
        for rows in (self.events, self.assertions, self.bridge_proofs):
            if len({r.id for r in rows}) != len(rows):
                raise ValueError("Duplicate evidence identifiers")
        if len({(c.chain, c.address) for c in self.coverage}) != len(self.coverage):
            raise ValueError("Duplicate coverage scope")
        if self.mode != "fixture":
            from .addresses import validate_address

            for e in self.events:
                e.senders = [validate_address(e.chain, a) for a in e.senders]
                e.recipient = validate_address(e.destination_chain or e.chain, e.recipient)
            for a in self.assertions:
                a.address = validate_address(a.chain, a.address)
            for c in self.coverage:
                c.address = validate_address(c.chain, c.address)
            for gap in self.reconciliation_gaps:
                gap.address = validate_address(gap.chain, gap.address)
            if len({(c.chain, c.address) for c in self.coverage}) != len(self.coverage):
                raise ValueError("Duplicate normalised coverage scope")
        return self


class TraceSpec(Contract):
    chain: Chain
    address: str = Field(min_length=1, max_length=160)
    start: int = Field(ge=0)
    end: int = Field(ge=1)
    max_hops: int = Field(default=3, ge=1, le=8)
    max_states: int = Field(default=2000, ge=10, le=10000)
    max_requests: int = Field(default=30, ge=1, le=200)
    asset: str | None = None
    minimum_amount: str = Field(default="0", pattern=r"^\d{1,80}$")

    @model_validator(mode="after")
    def window(self):
        if self.start >= self.end:
            raise ValueError("Start must precede end")
        return self
