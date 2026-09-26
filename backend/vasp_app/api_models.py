from typing import Literal
from pydantic import Field
from .domain import Contract, TraceSpec, Snapshot, Assertion, BridgeProof


class Login(Contract):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=256)


class PasswordChange(Contract):
    current: str = Field(max_length=256)
    password: str = Field(min_length=14, max_length=256)


class CaseCreate(Contract):
    title: str = Field(min_length=3, max_length=160)
    reference: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=5000)
    classification: Literal["Restricted", "Confidential"] = "Restricted"
    members: list[str] = Field(default_factory=list, max_length=100)


class CaseUpdate(Contract):
    version: int
    status: Literal["Open", "Under review", "Closed"]
    title: str | None = Field(default=None, min_length=3, max_length=160)
    reference: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=5000)
    classification: Literal["Restricted", "Confidential"] | None = None
    members: list[str] | None = Field(default=None, max_length=100)


class AnalyzeRequest(Contract):
    mode: Literal["live", "imported", "fixture"]
    spec: TraceSpec
    snapshot_id: str | None = None
    fixture_scenario: Literal["custody", "cctp-review"] = "custody"


class SnapshotImport(Contract):
    snapshot: Snapshot
    provenance: str = Field(min_length=10, max_length=2000)


class AssertionCreate(Contract):
    assertion: Assertion
    rationale: str = Field(min_length=10, max_length=3000)


class BridgeCreate(Contract):
    proof: BridgeProof
    mode: Literal["operational", "training"] = "operational"
    rationale: str = Field(min_length=10, max_length=3000)


class Decision(Contract):
    version: int
    decision: Literal["approve", "reject"]
    rationale: str = Field(min_length=10, max_length=3000)


class ChallengeRequest(Contract):
    excluded: list[str] = Field(min_length=1, max_length=100)


class PlanRequest(Contract):
    budget_requests: int = Field(ge=1, le=200)


class PlanExecutionRequest(Contract):
    version: int = Field(ge=1)
    plan_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")


class RecipientCreate(Contract):
    mode: Literal["operational", "training"] = "operational"
    entity: str = Field(min_length=2, max_length=160)
    jurisdiction: str = Field(min_length=2, max_length=100)
    channel: str = Field(min_length=3, max_length=500)
    verification_source: str = Field(min_length=10, max_length=2000)
    signing_public_key: str | None = None
    expires_at: int = Field(gt=0)


class RequestCreate(Contract):
    job_id: str
    candidate_index: int = Field(ge=0)
    recipient_id: str
    type: Literal["disclosure", "preservation", "freezing_review"]
    legal_basis: str = Field(min_length=10, max_length=5000)
    scope: str = Field(min_length=10, max_length=5000)


class FeedbackCreate(Contract):
    request_id: str
    payload: dict
    signature: str = Field(max_length=256)


class WithdrawalCreate(Contract):
    version: int
    rationale: str = Field(min_length=10, max_length=3000)


class WatchCreate(Contract):
    spec: TraceSpec
    interval_minutes: int = Field(default=60, ge=15, le=10080)
    enabled: bool = True


class UserCreate(Contract):
    username: str = Field(pattern=r"^[a-zA-Z0-9_.-]{3,100}$")
    display_name: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=14, max_length=256)
    role: Literal["investigator", "reviewer", "admin"]
