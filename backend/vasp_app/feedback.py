"""Narrow service attestations: signatures bind claims, never establish their truth."""

import base64
import hashlib
from typing import Literal
from pydantic import Field, model_validator
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from .domain import Contract, Chain, Assertion
from .store import canonical, digest


class ServiceAttestation(Contract):
    chain: Chain
    address: str
    entity: str = Field(min_length=1, max_length=160)
    category: Literal["exchange", "custodian"]
    role: Literal["deposit", "hot", "unknown"]
    valid_from: int = Field(ge=0)
    valid_to: int = Field(ge=0)

    @model_validator(mode="after")
    def interval(self):
        if self.valid_to < self.valid_from:
            raise ValueError("Attestation validity interval is reversed")
        return self


def verify_response(payload, signature, public, request):
    if (
        digest(request["body"]) != request["body_sha256"]
        or request.get("reviewed_body_sha256") != request["body_sha256"]
    ):
        raise ValueError("Request approval or integrity is no longer valid")
    if payload.get("request_sha256") != request["body_sha256"]:
        raise ValueError("Response is not bound to the reviewed request")
    pinned_key = request["body"]["recipient"].get("signing_public_key")
    if pinned_key != public:
        raise ValueError("Response key differs from the key bound to the request")
    Ed25519PublicKey.from_public_bytes(base64.b64decode(public, validate=True)).verify(
        base64.b64decode(signature, validate=True), canonical(payload)
    )
    # Unstructured signed findings can be reviewed, but never become wallet labels.
    if "attestation" not in payload:
        return None
    if payload.get("schema") != "atlas.service-response.v1":
        raise ValueError("Structured attestation requires atlas.service-response.v1")
    attestation = ServiceAttestation.model_validate(payload["attestation"])
    candidate = request["body"]["candidate"]
    if (attestation.chain, attestation.address, attestation.entity) != (
        candidate["chain"],
        candidate["address"],
        candidate["entity"],
    ):
        raise ValueError("Attestation must match exactly the requested wallet and entity")
    return attestation


def promoted_assertion(feedback_id, attestation, public, evidence_hash):
    # The same signing key is one provenance family, even across directory entries.
    fingerprint = hashlib.sha256(base64.b64decode(public, validate=True)).hexdigest()
    return Assertion(
        id="service:" + feedback_id,
        **attestation.model_dump(),
        grade="reviewed",
        source_family="service-key:" + fingerprint,
        source="Independently reviewed service attestation; signature proves origin from the reviewed key, not ownership truth",
        evidence=[evidence_hash],
    )
