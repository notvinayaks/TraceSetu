from __future__ import annotations
import base64
import hashlib
import secrets
import threading
from collections import defaultdict
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Request, Response, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature
from .config import settings, ROOT
from .store import (
    engine,
    SessionLocal,
    User,
    Session,
    Record,
    Job,
    Audit,
    now,
    uid,
    canonical,
    digest,
    artifact,
    read_artifact,
    record,
    patch_record,
    as_dict,
    audit,
)
from .security import (
    principal,
    get_db,
    password_hash,
    check_password,
    session_hash,
    require_role,
    case_access,
    object_access,
    bootstrap,
)
from .api_models import (
    Login,
    PasswordChange,
    UserCreate,
    CaseCreate,
    CaseUpdate,
    SnapshotImport,
    AnalyzeRequest,
    ChallengeRequest,
    PlanRequest,
    PlanExecutionRequest,
    AssertionCreate,
    BridgeCreate,
    RecipientCreate,
    RequestCreate,
    Decision,
    FeedbackCreate,
    WithdrawalCreate,
    WatchCreate,
)
from .domain import TraceSpec, Snapshot, BridgeProof
from .cctp import verify_bridge
from .addresses import validate_address
from .fixtures import training_snapshot
from .cctp_fixture import bridge_snapshot, SEED
from .providers import capabilities
from .engine import challenge
from .reports import make_bundle, verify_bundle, pdf_report, signing_key
from .feedback import verify_response, promoted_assertion
from .planner import plan_queries, POLICY_VERSION
from . import worker
from .migrations import upgrade, require_current
from .observability import configure_logging, OperationalMiddleware, readiness, tenant_operations


@asynccontextmanager
async def lifespan(app):
    configure_logging()
    if settings.auto_migrate:
        upgrade(engine)
    require_current(engine)
    with SessionLocal() as db:
        bootstrap(db)
    signing_key()
    thread = worker.start() if settings.worker_enabled else None
    yield
    worker.stop_event.set()
    if thread:
        thread.join(timeout=2)


app = FastAPI(
    title="TraceSetu API",
    version="0.3.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url="/api/openapi.json",
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts.split(","))
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "X-CSRF-Token", "Idempotency-Key"],
)
app.add_middleware(OperationalMiddleware)


@app.middleware("http")
async def boundary(request, call_next):
    if request.method in ("POST", "PUT", "PATCH", "DELETE"):
        origin = request.headers.get("origin")
        if origin and origin not in settings.allowed_origins.split(","):
            return Response("Untrusted origin", status_code=403)
        try:
            length = int(request.headers.get("content-length", "0"))
        except ValueError:
            return Response("Invalid Content-Length", status_code=400)
        if length > settings.max_body_bytes:
            return Response("Payload too large", status_code=413)
        if request.headers.get("transfer-encoding"):
            return Response("Chunked uploads are not accepted", status_code=411)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; font-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    )
    return response


@app.exception_handler(ValueError)
async def invalid_value(request, exc):
    from fastapi.responses import JSONResponse

    return JSONResponse(status_code=422, content={"detail": str(exc)[:500]})


def public_user(u):
    return {"id": u.id, "username": u.username, "name": u.display_name, "role": u.role}


_attempts = defaultdict(list)
_login_lock = threading.Lock()


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "product": "TraceSetu",
        "deployment": "independent installation",
        "sahyog": "not connected",
    }


@app.get("/api/ready")
def ready(response: Response):
    report = readiness()
    response.status_code = 200 if report["ready"] else 503
    return {"ready": report["ready"]}


@app.get("/api/operations")
def operations(user=Depends(principal)):
    require_role(user, "admin")
    return {"readiness": readiness(), "tenant": tenant_operations(user.tenant)}


@app.post("/api/auth/login")
def login(data: Login, request: Request, response: Response, db=Depends(get_db)):
    host = request.client.host if request.client else "unknown"
    with _login_lock:
        _attempts[host] = [x for x in _attempts[host] if x > now() - 900]
        if len(_attempts[host]) >= 15:
            raise HTTPException(429, "Too many sign-in attempts. Retry in 15 minutes.")
        _attempts[host].append(now())
    user = db.scalar(select(User).where(User.username == data.username))
    if not user or not user.active or not check_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials.")
    token = secrets.token_urlsafe(32)
    csrf = secrets.token_urlsafe(32)
    db.add(
        Session(
            token_hash=session_hash(token),
            user_id=user.id,
            csrf=csrf,
            expires=now() + 3600 * settings.session_hours,
        )
    )
    audit(db, user, "session.login", user.id)
    db.commit()
    response.set_cookie(
        "atlas_session",
        token,
        httponly=True,
        secure=settings.secure_cookie,
        samesite="strict",
        max_age=settings.session_hours * 3600,
        path="/",
    )
    return {"user": public_user(user), "csrf": csrf}


@app.get("/api/auth/me")
def me(request: Request, user=Depends(principal)):
    return {"user": public_user(user), "csrf": request.state.session.csrf}


@app.post("/api/auth/logout")
def logout(request: Request, response: Response, user=Depends(principal), db=Depends(get_db)):
    db.delete(db.get(Session, request.state.session.token_hash))
    audit(db, user, "session.logout", user.id)
    db.commit()
    response.delete_cookie("atlas_session", path="/")
    return {"ok": True}


@app.post("/api/auth/password")
def change_password(data: PasswordChange, user=Depends(principal), db=Depends(get_db)):
    if not check_password(data.current, user.password_hash):
        raise HTTPException(400, "Current password is incorrect")
    user.password_hash = password_hash(data.password)
    db.execute(delete(Session).where(Session.user_id == user.id))
    audit(db, user, "user.password_changed", user.id)
    db.commit()
    return {"ok": True, "sign_in_required": True}


@app.get("/api/users")
def users(user=Depends(principal), db=Depends(get_db)):
    return [
        public_user(u) for u in db.scalars(select(User).where(User.tenant == user.tenant, User.active == 1))
    ]


@app.post("/api/users", status_code=201)
def add_user(data: UserCreate, user=Depends(principal), db=Depends(get_db)):
    require_role(user, "admin")
    u = User(
        id=uid("usr_"),
        tenant=user.tenant,
        username=data.username,
        display_name=data.display_name,
        role=data.role,
        password_hash=password_hash(data.password),
    )
    db.add(u)
    audit(db, user, "user.created", u.id)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Username already exists")
    return public_user(u)


@app.get("/api/capabilities")
def capability_list(user=Depends(principal)):
    return {
        "chains": capabilities(),
        "sahyog": {
            "connected": False,
            "status": "Official API contract and access required. Only request packages can be exported.",
        },
        "identity_data": (
            "Etherscan metadata adapter enabled; entitlement and live validation pending. Current tags remain hypotheses until reviewed."
            if settings.etherscan_metadata_enabled
            else "Case-scoped, reviewed assertions. No commercial attribution provider is connected."
        ),
        "runtime": "Single-node durable worker; PostgreSQL-compatible store. Production hardening remains required.",
        "cross_chain": {
            "protocol": "CCTP V2",
            "scope": "Native USDC: Ethereum and Polygon",
            "implemented": True,
            "configured": settings.cctp_enabled and bool(settings.etherscan_api_key),
            "live_validated": False,
            "status": "Protocol verification, reviewed imports and read-only acquisition implemented; live validation pending. Other bridge protocols remain unresolved.",
        },
    }


@app.get("/api/cases")
def cases(user=Depends(principal), db=Depends(get_db)):
    return [
        as_dict(r)
        for r in db.scalars(
            select(Record)
            .where(Record.kind == "case", Record.tenant == user.tenant)
            .order_by(Record.updated.desc())
        )
        if user.role == "admin" or user.id in r.payload.get("members", [])
    ]


@app.post("/api/cases", status_code=201)
def new_case(data: CaseCreate, user=Depends(principal), db=Depends(get_db)):
    require_role(user, "admin", "investigator")
    members = list(dict.fromkeys([user.id] + data.members))
    for member in members:
        u = db.get(User, member)
        if not u or u.tenant != user.tenant or not u.active:
            raise HTTPException(422, "Invalid case member")
    r = record(
        db,
        "case",
        user.tenant,
        {**data.model_dump(), "members": members, "status": "Open", "created_by": user.id},
    )
    audit(db, user, "case.created", r.id)
    db.commit()
    return as_dict(r)


@app.get("/api/cases/{case_id}")
def read_case(case_id: str, user=Depends(principal), db=Depends(get_db)):
    c = case_access(db, user, case_id)
    audit(db, user, "case.viewed", case_id)
    db.commit()
    return as_dict(c)


@app.patch("/api/cases/{case_id}")
def edit_case(case_id: str, data: CaseUpdate, user=Depends(principal), db=Depends(get_db)):
    require_role(user, "admin", "investigator")
    c = case_access(db, user, case_id)
    changes = data.model_dump(exclude_none=True, exclude={"version"})
    if data.members is not None:
        changes["members"] = list(dict.fromkeys([user.id] + data.members))
        for member in changes["members"]:
            u = db.get(User, member)
            if not u or u.tenant != user.tenant or not u.active:
                raise HTTPException(422, "Invalid case member")
    n = db.execute(
        update(Record)
        .where(Record.id == c.id, Record.version == data.version)
        .values(payload={**c.payload, **changes}, version=Record.version + 1, updated=now())
    )
    if n.rowcount != 1:
        raise HTTPException(409, "Case changed. Reload before editing.")
    audit(db, user, "case.updated", case_id, {"fields": list(changes), "status": data.status})
    db.commit()
    db.refresh(c)
    return as_dict(c)


@app.get("/api/cases/{case_id}/records")
def records(case_id: str, user=Depends(principal), db=Depends(get_db)):
    case_access(db, user, case_id)
    return [
        as_dict(r)
        for r in db.scalars(
            select(Record)
            .where(Record.case_id == case_id, Record.tenant == user.tenant)
            .order_by(Record.created.desc())
        )
    ]


@app.post("/api/cases/{case_id}/snapshots", status_code=201)
def import_snapshot(case_id: str, data: SnapshotImport, user=Depends(principal), db=Depends(get_db)):
    require_role(user, "admin", "investigator")
    case_access(db, user, case_id)
    if data.snapshot.mode == "fixture":
        raise HTTPException(422, "Use the dedicated synthetic training workflow")
    snap = data.snapshot.model_copy(deep=True)
    snap.mode = "imported"
    for a in snap.assertions:
        a.grade = "hypothesis"
    for proof in snap.bridge_proofs:
        proof.grade = "hypothesis"
    snap.limitations.append(
        "Imported assertions and bridge proofs are hypotheses until independently reviewed. Imported completeness is a submitter claim."
    )
    h = artifact(canonical(snap.model_dump()))
    r = record(
        db,
        "snapshot",
        user.tenant,
        {
            "sha256": h,
            "provenance": data.provenance,
            "origin": snap.origin,
            "event_count": len(snap.events),
            "imported_by": user.id,
            "window_start": snap.window_start,
            "window_end": snap.window_end,
        },
        case_id,
    )
    audit(db, user, "snapshot.imported", case_id, {"record_id": r.id, "sha256": h})
    db.commit()
    return as_dict(r)


def job_access(db, user, job_id):
    j = db.get(Job, job_id)
    if not j or j.tenant != user.tenant:
        raise HTTPException(404, "Analysis not found")
    case_access(db, user, j.case_id)
    check_result_integrity(j)
    j.evidence_changes = evidence_changes(db, j)
    return j


def evidence_changes(db, j):
    if not j.result:
        return []
    used = {a["id"] for n in j.result["analysis"]["graph"]["nodes"] for a in n["labels"]}
    used_bridges = {
        e["bridge_proof"] for e in j.result["analysis"]["graph"]["events"] if e.get("bridge_proof")
    }
    return [
        {
            "record_id": r.id,
            "assertion_id": (r.payload.get("assertion") or r.payload.get("proof"))["id"],
            "reason": "Reviewed evidence was withdrawn; reassess before relying on this analysis",
        }
        for r in db.scalars(
            select(Record).where(
                Record.tenant == j.tenant,
                Record.case_id == j.case_id,
                Record.kind.in_(["assertion", "bridge"]),
            )
        )
        if r.payload.get("status") == "withdrawn"
        and (
            (r.kind == "assertion" and r.payload["assertion"]["id"] in used)
            or (r.kind == "bridge" and r.payload["proof"]["id"] in used_bridges)
        )
    ]


def require_current_evidence(db, j):
    if evidence_changes(db, j):
        raise HTTPException(
            409,
            "Supporting evidence has been withdrawn. Reassess this analysis before request or report export; the historical snapshot remains available.",
        )


def check_result_integrity(j):
    if not j.result:
        return
    result = j.result
    analysis = result["analysis"]
    if (
        digest(analysis) != result["result_sha256"]
        or analysis["certificate"]["snapshot_sha256"] != result["snapshot_sha256"]
    ):
        raise HTTPException(409, "Stored analysis integrity check failed; do not rely on this result")
    if analysis["mode"] != j.request["mode"] or analysis["certificate"]["specification"] != j.request["spec"]:
        raise HTTPException(409, "Analysis is not bound to this request")
    try:
        read_artifact(result["result_sha256"])
        read_artifact(result["snapshot_sha256"])
        if result.get("acquisition_metrics_sha256"):
            if read_artifact(result["acquisition_metrics_sha256"]) != canonical(
                result["acquisition_metrics"]
            ):
                raise ValueError("Acquisition metrics were changed")
        if result.get("execution_sha256") and read_artifact(result["execution_sha256"]) != canonical(
            result["execution"]
        ):
            raise ValueError("Query execution evidence was changed")
    except (ValueError, FileNotFoundError):
        raise HTTPException(409, "Evidence artifact is missing or failed integrity verification") from None


def job_dict(j, full=True):
    if full:
        check_result_integrity(j)
    return {
        "id": j.id,
        "case_id": j.case_id,
        "created": j.created,
        "updated": j.updated,
        "status": j.status,
        "stage": j.stage,
        "request": j.request,
        "error": j.error,
        "attempts": j.attempts,
        "result": j.result if full else None,
        "evidence_changes": getattr(j, "evidence_changes", []),
    }


@app.post("/api/cases/{case_id}/analyses", status_code=202)
def create_analysis(
    case_id: str, data: AnalyzeRequest, request: Request, user=Depends(principal), db=Depends(get_db)
):
    require_role(user, "admin", "investigator")
    case = case_access(db, user, case_id)
    if case.payload["status"] == "Closed":
        raise HTTPException(409, "Reopen the case before starting analysis")
    spec = data.spec.model_copy(deep=True)
    payload = {"mode": data.mode}
    if data.mode == "fixture":
        payload["fixture_scenario"] = data.fixture_scenario
        snap = bridge_snapshot() if data.fixture_scenario == "cctp-review" else training_snapshot()
        spec = TraceSpec(
            chain="ethereum",
            address=SEED if data.fixture_scenario == "cctp-review" else "fixture:suspect",
            start=snap.window_start,
            end=snap.window_end,
            max_hops=spec.max_hops,
            max_states=spec.max_states,
            max_requests=spec.max_requests,
        )
    elif data.mode == "live":
        spec.address = validate_address(spec.chain, spec.address)
        if spec.end > int(now()):
            raise HTTPException(422, "Live acquisition cannot establish coverage in the future")
    elif data.mode == "imported":
        spec.address = validate_address(spec.chain, spec.address)
        r = object_access(db, user, data.snapshot_id, "snapshot")
        if r.case_id != case_id:
            raise HTTPException(422, "Snapshot belongs to a different case")
        payload["snapshot_sha256"] = r.payload["sha256"]
    payload["spec"] = spec.model_dump()
    h = digest({"case_id": case_id, **payload})
    idem = request.headers.get("Idempotency-Key", "")
    if not 8 <= len(idem) <= 128:
        raise HTTPException(422, "Idempotency-Key header must have 8-128 characters")
    previous = db.scalar(select(Job).where(Job.tenant == user.tenant, Job.idempotency == idem))
    if previous:
        case_access(db, user, previous.case_id)
        if previous.input_hash != h:
            raise HTTPException(409, "Idempotency key reused with different input")
        return job_dict(previous)
    j = Job(
        id=uid("job_"),
        tenant=user.tenant,
        case_id=case_id,
        actor_id=user.id,
        idempotency=idem,
        input_hash=h,
        request=payload,
    )
    db.add(j)
    audit(db, user, "analysis.queued", case_id, {"job_id": j.id, "mode": data.mode})
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Concurrent duplicate request. Retry with the same key.")
    return job_dict(j)


@app.get("/api/cases/{case_id}/analyses")
def list_analyses(case_id: str, user=Depends(principal), db=Depends(get_db)):
    case_access(db, user, case_id)
    return [
        job_dict(j, False)
        for j in db.scalars(
            select(Job).where(Job.case_id == case_id, Job.tenant == user.tenant).order_by(Job.created.desc())
        )
    ]


@app.get("/api/analyses/{job_id}")
def analysis(job_id: str, user=Depends(principal), db=Depends(get_db)):
    return job_dict(job_access(db, user, job_id))


@app.post("/api/analyses/{job_id}/query-plan")
def query_plan(job_id: str, data: PlanRequest, user=Depends(principal), db=Depends(get_db)):
    j = job_access(db, user, job_id)
    if not j.result:
        raise HTTPException(409, "Analysis is not available")
    snap = Snapshot.model_validate_json(read_artifact(j.result["snapshot_sha256"]))
    available = {c["chain"]: c["configured"] for c in capabilities()}
    if snap.mode == "fixture":
        available = {c: True for c in available}
    plan = plan_queries(snap, j.result["analysis"], data.budget_requests, available)
    plan["parent_job_id"] = j.id
    plan["evidence_changes"] = evidence_changes(db, j)
    plan["availability_basis"] = (
        "Simulated availability for synthetic planning exercise"
        if snap.mode == "fixture"
        else "Local configuration only; provider entitlement and live availability are unverified"
    )
    h = artifact(canonical(plan))
    r = record(db, "query_plan", user.tenant, {"plan": plan, "sha256": h, "created_by": user.id}, j.case_id)
    audit(db, user, "query_plan.prepared", j.case_id, {"record_id": r.id, "job_id": j.id, "sha256": h})
    db.commit()
    return as_dict(r)


@app.post("/api/analyses/{job_id}/query-plans/{record_id}/execute", status_code=202)
def execute_query_plan(
    job_id: str,
    record_id: str,
    data: PlanExecutionRequest,
    request: Request,
    user=Depends(principal),
    db=Depends(get_db),
):
    require_role(user, "admin", "investigator")
    parent = job_access(db, user, job_id)
    case = case_access(db, user, parent.case_id)
    require_current_evidence(db, parent)
    plan_record = object_access(db, user, record_id, "query_plan")
    if case.payload["status"] == "Closed" or not parent.result or plan_record.case_id != parent.case_id:
        raise HTTPException(409, "An open case and its completed analysis/plan are required")
    plan = plan_record.payload["plan"]
    try:
        if (
            read_artifact(data.plan_sha256) != canonical(plan)
            or plan_record.payload["sha256"] != data.plan_sha256
        ):
            raise ValueError("Plan hash mismatch")
    except (ValueError, FileNotFoundError):
        raise HTTPException(409, "Query plan integrity check failed") from None
    if (
        plan["policy_version"] != POLICY_VERSION
        or plan.get("parent_job_id") != parent.id
        or plan["analysis_sha256"] != parent.result["result_sha256"]
        or plan["snapshot_sha256"] != parent.result["snapshot_sha256"]
        or plan["mode"] != parent.request["mode"]
    ):
        raise HTTPException(409, "Plan is not bound to this analysis and supported policy; create a new plan")
    selected = [
        a
        for a in plan["actions"]
        if a["status"] == "selected_estimate" and a["action"] == "reacquire_history"
    ]
    if not selected:
        raise HTTPException(
            422, "No history-acquisition action fits this plan; manual reviews are not provider queries"
        )
    if parent.request["mode"] != "fixture":
        available = {c["chain"]: c["configured"] for c in capabilities()}
        if any(not available.get(a["chain"]) for a in selected):
            raise HTTPException(409, "A selected provider is no longer configured; prepare a new plan")
    payload = {
        "mode": parent.request["mode"],
        "spec": parent.request["spec"],
        "fixture_scenario": parent.request.get("fixture_scenario", "custody"),
        "supersedes_job_id": parent.id,
        "execution_plan_id": record_id,
        "execution_plan_version": data.version,
        "execution_plan_sha256": data.plan_sha256,
        "execution_parent_snapshot_sha256": parent.result["snapshot_sha256"],
        "execution_parent_analysis_sha256": parent.result["result_sha256"],
    }
    h = digest({"case_id": parent.case_id, **payload})
    idem = request.headers.get("Idempotency-Key", "")
    if not 8 <= len(idem) <= 128:
        raise HTTPException(422, "Idempotency-Key header must have 8-128 characters")
    previous = db.scalar(select(Job).where(Job.tenant == user.tenant, Job.idempotency == idem))
    if previous:
        case_access(db, user, previous.case_id)
        if previous.input_hash != h:
            raise HTTPException(409, "Idempotency key reused with different input")
        return job_dict(previous)
    if plan_record.version != data.version or plan_record.payload.get("execution_job_id"):
        raise HTTPException(
            409, "Plan changed or was already executed; prepare a new plan for additional acquisition"
        )
    j = Job(
        id=uid("job_"),
        tenant=user.tenant,
        case_id=parent.case_id,
        actor_id=user.id,
        idempotency=idem,
        input_hash=h,
        request=payload,
    )
    consumed = db.execute(
        update(Record)
        .where(Record.id == record_id, Record.version == data.version)
        .values(
            payload={**plan_record.payload, "execution_job_id": j.id},
            version=Record.version + 1,
            updated=now(),
        )
    )
    if consumed.rowcount != 1:
        raise HTTPException(409, "Concurrent plan execution; reload the plan")
    db.add(j)
    audit(
        db,
        user,
        "query_plan.execution_queued",
        parent.case_id,
        {
            "job_id": j.id,
            "parent_job_id": parent.id,
            "plan_sha256": data.plan_sha256,
            "budget": plan["budget_requests"],
        },
    )
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Concurrent duplicate execution; retry with the same key") from None
    return job_dict(j)


@app.post("/api/analyses/{job_id}/reassess", status_code=202)
def reassess(job_id: str, request: Request, user=Depends(principal), db=Depends(get_db)):
    require_role(user, "admin", "investigator")
    previous = job_access(db, user, job_id)
    case = case_access(db, user, previous.case_id)
    if not previous.result or case.payload["status"] == "Closed":
        raise HTTPException(409, "A completed analysis and an open case are required")
    idem = request.headers.get("Idempotency-Key", "")
    if not 8 <= len(idem) <= 128:
        raise HTTPException(422, "Idempotency-Key header must have 8-128 characters")
    payload = {
        **{k: v for k, v in previous.request.items() if not k.startswith("execution_")},
        "reassessment_snapshot_sha256": previous.result["snapshot_sha256"],
        "supersedes_job_id": previous.id,
    }
    h = digest({"case_id": previous.case_id, **payload})
    existing = db.scalar(select(Job).where(Job.tenant == user.tenant, Job.idempotency == idem))
    if existing:
        case_access(db, user, existing.case_id)
        if existing.input_hash != h:
            raise HTTPException(409, "Idempotency key reused with different input")
        return job_dict(existing)
    j = Job(
        id=uid("job_"),
        tenant=user.tenant,
        case_id=previous.case_id,
        actor_id=user.id,
        idempotency=idem,
        input_hash=h,
        request=payload,
    )
    db.add(j)
    audit(db, user, "analysis.reassessment_queued", j.case_id, {"job_id": j.id, "prior_job_id": previous.id})
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Concurrent duplicate request. Retry with the same key.") from None
    return job_dict(j)


@app.post("/api/analyses/{job_id}/cancel")
def cancel(job_id: str, user=Depends(principal), db=Depends(get_db)):
    require_role(user, "admin", "investigator")
    j = job_access(db, user, job_id)
    if j.status not in ("QUEUED", "RUNNING"):
        raise HTTPException(409, "Analysis is already complete")
    j.status = "CANCELLED"
    j.stage = "Cancelled by investigator"
    audit(db, user, "analysis.cancelled", j.case_id, {"job_id": j.id})
    db.commit()
    return job_dict(j)


@app.post("/api/analyses/{job_id}/challenge")
def challenge_analysis(job_id: str, data: ChallengeRequest, user=Depends(principal), db=Depends(get_db)):
    j = job_access(db, user, job_id)
    if not j.result:
        raise HTTPException(409, "Analysis is not available")
    snap = Snapshot.model_validate_json(read_artifact(j.result["snapshot_sha256"]))
    valid = {a.id for a in snap.assertions} | {a.source_family for a in snap.assertions}
    valid |= {p.id for p in snap.bridge_proofs} | {p.source_family for p in snap.bridge_proofs}
    if set(data.excluded) - valid:
        raise HTTPException(422, "Unknown assertion or provenance family")
    result = challenge(snap, TraceSpec.model_validate(j.request["spec"]), data.excluded)
    h = artifact(canonical(result))
    r = record(
        db,
        "challenge",
        user.tenant,
        {
            "job_id": j.id,
            "sha256": h,
            "excluded": data.excluded,
            "requires_expansion": result["requires_expansion"],
        },
        j.case_id,
    )
    audit(db, user, "analysis.challenged", j.case_id, {"job_id": j.id, "record_id": r.id, "sha256": h})
    db.commit()
    return result


@app.post("/api/cases/{case_id}/assertions", status_code=201)
def add_assertion(case_id: str, data: AssertionCreate, user=Depends(principal), db=Depends(get_db)):
    require_role(user, "admin", "investigator")
    case_access(db, user, case_id)
    a = data.assertion.model_copy(deep=True)
    a.address = validate_address(a.chain, a.address)
    a.grade = "hypothesis"
    a.id = uid("assert_")
    r = record(
        db,
        "assertion",
        user.tenant,
        {
            "assertion": a.model_dump(),
            "rationale": data.rationale,
            "created_by": user.id,
            "status": "pending",
        },
        case_id,
    )
    audit(db, user, "assertion.proposed", case_id, {"record_id": r.id})
    db.commit()
    return as_dict(r)


@app.post("/api/cases/{case_id}/bridges", status_code=201)
def add_bridge(case_id: str, data: BridgeCreate, user=Depends(principal), db=Depends(get_db)):
    require_role(user, "admin", "investigator")
    case_access(db, user, case_id)
    proof = data.proof.model_copy(deep=True)
    if data.mode == "operational" and (
        proof.source_family.startswith("synthetic-") or any("SYNTHETIC" in e for e in proof.evidence)
    ):
        raise HTTPException(422, "Explicit synthetic proof must use training purpose")
    proof.id = uid("bridge_")
    proof.grade = "hypothesis"
    try:
        link = verify_bridge(proof)
    except (ValueError, KeyError, TypeError):
        raise HTTPException(
            422, "Protocol, attestation or receipt validation failed; no bridge was accepted"
        ) from None
    for prior in db.scalars(
        select(Record).where(Record.tenant == user.tenant, Record.case_id == case_id, Record.kind == "bridge")
    ):
        p = prior.payload
        if (
            p["mode"] == data.mode
            and p["status"] in ("pending", "approved")
            and (p["proof"]["source_chain"], p["proof"]["nonce"].lower())
            == (proof.source_chain, proof.nonce.lower())
        ):
            raise HTTPException(
                409,
                "This protocol message already has a pending or approved proof; resolve it before proposing another",
            )
    h = artifact(canonical(proof.model_dump()))
    summary = {k: v for k, v in link.items() if k != "event"}
    summary["event"] = link["event"].model_dump()
    r = record(
        db,
        "bridge",
        user.tenant,
        {
            "proof": proof.model_dump(),
            "proof_sha256": h,
            "summary": summary,
            "mode": data.mode,
            "rationale": data.rationale,
            "created_by": user.id,
            "status": "pending",
        },
        case_id,
    )
    audit(db, user, "bridge.proposed", case_id, {"record_id": r.id, "sha256": h})
    db.commit()
    return as_dict(r)


@app.get("/api/recipients")
def recipients(user=Depends(principal), db=Depends(get_db)):
    return [
        as_dict(r)
        for r in db.scalars(select(Record).where(Record.tenant == user.tenant, Record.kind == "recipient"))
    ]


@app.post("/api/recipients", status_code=201)
def add_recipient(data: RecipientCreate, user=Depends(principal), db=Depends(get_db)):
    require_role(user, "admin", "investigator")
    if data.expires_at <= now():
        raise HTTPException(422, "Verification expiry must be in the future")
    if data.signing_public_key:
        try:
            Ed25519PublicKey.from_public_bytes(base64.b64decode(data.signing_public_key, validate=True))
        except Exception:
            raise HTTPException(422, "Expected a Base64 Ed25519 public key")
    r = record(
        db, "recipient", user.tenant, {**data.model_dump(), "created_by": user.id, "status": "pending"}
    )
    audit(db, user, "recipient.proposed", r.id)
    db.commit()
    return as_dict(r)


@app.post("/api/cases/{case_id}/requests", status_code=201)
def new_request(case_id: str, data: RequestCreate, user=Depends(principal), db=Depends(get_db)):
    require_role(user, "admin", "investigator")
    case_access(db, user, case_id)
    j = job_access(db, user, data.job_id)
    require_current_evidence(db, j)
    if j.case_id != case_id or not j.result:
        raise HTTPException(422, "Choose a completed analysis from this case")
    candidates = j.result["analysis"]["candidates"]
    if data.candidate_index >= len(candidates):
        raise HTTPException(422, "Candidate does not exist")
    candidate = candidates[data.candidate_index]
    if candidate["status"] != "evidenced":
        raise HTTPException(409, "Resolve the attribution conflict before preparing a request")
    recipient = object_access(db, user, data.recipient_id, "recipient")
    expected_mode = "training" if j.request["mode"] == "fixture" else "operational"
    if recipient.payload.get("mode") != expected_mode:
        raise HTTPException(409, "Recipient purpose must match this analysis: " + expected_mode)
    if recipient.payload["status"] != "approved" or recipient.payload["expires_at"] <= now():
        raise HTTPException(409, "Recipient verification is missing or expired")
    if recipient.payload["entity"] != candidate["entity"]:
        raise HTTPException(422, "Recipient must match the selected entity exactly")
    payload = {
        **data.model_dump(),
        "candidate": candidate,
        "recipient": as_dict(recipient),
        "analysis_sha256": j.result["result_sha256"],
        "mode": j.request["mode"],
        "created_by": user.id,
        "created_at": now(),
    }
    r = record(
        db,
        "request",
        user.tenant,
        {"body": payload, "body_sha256": digest(payload), "created_by": user.id, "status": "pending"},
        case_id,
    )
    audit(db, user, "request.prepared", case_id, {"record_id": r.id, "body_sha256": r.payload["body_sha256"]})
    db.commit()
    return as_dict(r)


@app.post("/api/records/{record_id}/review")
def review(record_id: str, data: Decision, user=Depends(principal), db=Depends(get_db)):
    require_role(user, "reviewer", "admin")
    r = object_access(db, user, record_id)
    if r.kind not in ("assertion", "bridge", "recipient", "request", "feedback", "withdrawal"):
        raise HTTPException(422, "Record is not reviewable")
    if r.payload.get("created_by") == user.id:
        raise HTTPException(403, "A different authorised reviewer must review this record")
    if r.payload.get("status") != "pending":
        raise HTTPException(409, "Record was already reviewed")
    payload = {
        **r.payload,
        "status": "approved" if data.decision == "approve" else "rejected",
        "reviewed_by": user.id,
        "reviewed_at": now(),
        "review_rationale": data.rationale,
    }
    if r.kind == "assertion" and data.decision == "approve":
        payload["assertion"] = {**payload["assertion"], "grade": "reviewed"}
    if r.kind == "bridge" and data.decision == "approve":
        try:
            if read_artifact(payload["proof_sha256"]) != canonical(payload["proof"]):
                raise ValueError("Bridge proof changed")
            verify_bridge(BridgeProof.model_validate(payload["proof"]))
        except (ValueError, KeyError, TypeError, FileNotFoundError):
            raise HTTPException(409, "Bridge proof integrity or protocol validation failed") from None
        payload["proof"] = {**payload["proof"], "grade": "reviewed"}
    if r.kind == "request":
        require_current_evidence(db, job_access(db, user, payload["body"]["job_id"]))
        if digest(payload["body"]) != payload["body_sha256"]:
            raise HTTPException(409, "Request payload integrity check failed")
        recipient = object_access(db, user, payload["body"]["recipient_id"], "recipient")
        if recipient.payload["status"] != "approved" or recipient.payload["expires_at"] <= now():
            raise HTTPException(409, "Recipient verification is no longer current")
        payload["reviewed_body_sha256"] = payload["body_sha256"]
    if r.kind == "feedback" and data.decision == "approve":
        response = payload["response"]
        request_record = object_access(db, user, response["request_id"], "request")
        recipient = object_access(db, user, request_record.payload["body"]["recipient_id"], "recipient")
        if recipient.payload["status"] != "approved" or recipient.payload["expires_at"] <= now():
            raise HTTPException(409, "Recipient verification is no longer current")
        try:
            if digest(response) != payload["sha256"] or payload["signer"] != recipient.payload.get(
                "signing_public_key"
            ):
                raise ValueError("Response was changed")
            attestation = verify_response(
                response,
                payload["signature"],
                recipient.payload.get("signing_public_key"),
                request_record.payload,
            )
            envelope = canonical(
                {"payload": response, "signature": payload["signature"], "signer": payload["signer"]}
            )
            if read_artifact(payload["envelope_sha256"]) != envelope:
                raise ValueError("Response envelope was changed")
        except (ValueError, InvalidSignature, FileNotFoundError, TypeError):
            raise HTTPException(409, "Response integrity or request binding failed") from None
        if attestation:
            a = promoted_assertion(r.id, attestation, payload["signer"], payload["envelope_sha256"])
            out = record(
                db,
                "assertion",
                user.tenant,
                {
                    "assertion": a.model_dump(),
                    "mode": payload["mode"],
                    "created_by": payload["created_by"],
                    "status": "approved",
                    "reviewed_by": user.id,
                    "reviewed_at": now(),
                    "review_rationale": data.rationale,
                    "feedback_id": r.id,
                    "rationale": "Scoped signed service attestation, approved by a separate reviewer",
                },
                r.case_id,
            )
            payload["promoted_assertion_id"] = out.id
    if r.kind == "withdrawal" and data.decision == "approve":
        target = object_access(db, user, payload["target_id"], payload.get("target_kind", "assertion"))
        if target.payload["status"] != "approved" or target.version != payload["target_version"]:
            raise HTTPException(409, "Assertion changed; propose a new withdrawal")
        changed = db.execute(
            update(Record)
            .where(Record.id == target.id, Record.version == target.version)
            .values(
                payload={**target.payload, "status": "withdrawn", "withdrawal_id": r.id},
                version=Record.version + 1,
                updated=now(),
            )
        )
        if changed.rowcount != 1:
            raise HTTPException(409, "Assertion changed concurrently")
        db.flush()
        affected = [
            j.id
            for j in db.scalars(select(Job).where(Job.case_id == r.case_id, Job.tenant == user.tenant))
            if evidence_changes(db, j)
        ]
        payload["affected_jobs"] = affected
        record(
            db,
            "alert",
            user.tenant,
            {
                "status": "unread",
                "message": "Reviewed attribution evidence was withdrawn. Reassess affected analyses before relying on them.",
                "withdrawal_id": r.id,
                "job_ids": affected,
            },
            r.case_id,
        )
    result = db.execute(
        update(Record)
        .where(Record.id == r.id, Record.version == data.version)
        .values(payload=payload, version=Record.version + 1, updated=now())
    )
    if result.rowcount != 1:
        raise HTTPException(409, "Record changed; reload before reviewing")
    audit(
        db,
        user,
        r.kind + ".reviewed",
        r.case_id or r.id,
        {"record_id": r.id, "decision": data.decision, "payload_sha256": digest(payload)},
    )
    db.commit()
    db.refresh(r)
    return as_dict(r)


@app.get("/api/requests/{record_id}/export")
def export_request(record_id: str, user=Depends(principal), db=Depends(get_db)):
    r = object_access(db, user, record_id, "request")
    p = r.payload
    require_current_evidence(db, job_access(db, user, p["body"]["job_id"]))
    if p["status"] != "approved" or p.get("reviewed_body_sha256") != digest(p["body"]):
        raise HTTPException(409, "Payload-bound approval required")
    recipient = object_access(db, user, p["body"]["recipient_id"], "recipient")
    if recipient.payload["status"] != "approved" or recipient.payload["expires_at"] <= now():
        raise HTTPException(409, "Recipient verification expired")
    data = canonical(
        {
            "schema": "atlas.reviewed-request.v1",
            "request_id": r.id,
            **p,
            "delivery_status": "NOT_SENT",
            "sahyog_status": "NOT_CONNECTED",
        }
    )
    h = artifact(data)
    audit(db, user, "request.exported", r.case_id, {"record_id": r.id, "sha256": h})
    db.commit()
    return Response(
        data,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{r.id}.json"'},
    )


@app.post("/api/assertions/{record_id}/withdrawal", status_code=201)
@app.post("/api/evidence/{record_id}/withdrawal", status_code=201)
def propose_withdrawal(record_id: str, data: WithdrawalCreate, user=Depends(principal), db=Depends(get_db)):
    require_role(user, "admin", "investigator")
    target = object_access(db, user, record_id)
    if target.kind not in ("assertion", "bridge"):
        raise HTTPException(422, "Choose a reviewed assertion or bridge proof")
    if target.payload["status"] != "approved" or target.version != data.version:
        raise HTTPException(409, "Choose the current approved assertion")
    r = record(
        db,
        "withdrawal",
        user.tenant,
        {
            "target_id": target.id,
            "target_kind": target.kind,
            "target_version": target.version,
            "rationale": data.rationale,
            "created_by": user.id,
            "status": "pending",
        },
        target.case_id,
    )
    audit(
        db,
        user,
        target.kind + ".withdrawal_proposed",
        target.case_id,
        {"record_id": r.id, "assertion_id": target.id},
    )
    db.commit()
    return as_dict(r)


@app.post("/api/cases/{case_id}/feedback", status_code=201)
def feedback(case_id: str, data: FeedbackCreate, user=Depends(principal), db=Depends(get_db)):
    require_role(user, "admin", "investigator")
    case_access(db, user, case_id)
    r = object_access(db, user, data.request_id, "request")
    if r.case_id != case_id or r.payload["status"] != "approved":
        raise HTTPException(422, "Choose an approved request from this case")
    recipient = object_access(db, user, r.payload["body"]["recipient_id"], "recipient")
    public = recipient.payload.get("signing_public_key")
    if not public or recipient.payload["status"] != "approved" or recipient.payload["expires_at"] <= now():
        raise HTTPException(409, "Verified, current recipient signing key required")
    if (
        data.payload.get("request_id") != r.id
        or data.payload.get("request_sha256") != r.payload["body_sha256"]
    ):
        raise HTTPException(422, "Response must bind to this exact request")
    try:
        attestation = verify_response(data.payload, data.signature, public, r.payload)
    except (ValueError, InvalidSignature):
        raise HTTPException(422, "Invalid response signature, schema or requested scope") from None
    h = digest(data.payload)
    identifier = "fb_" + hashlib.sha256((user.tenant + h).encode()).hexdigest()[:40]
    if db.get(Record, identifier):
        raise HTTPException(409, "Response was already imported")
    envelope_hash = artifact(
        canonical({"payload": data.payload, "signature": data.signature, "signer": public})
    )
    out = record(
        db,
        "feedback",
        user.tenant,
        {
            "response": data.payload,
            "signature": data.signature,
            "signer": public,
            "sha256": h,
            "envelope_sha256": envelope_hash,
            "mode": "training" if r.payload["body"]["mode"] == "fixture" else "operational",
            "attestation": attestation.model_dump() if attestation else None,
            "created_by": user.id,
            "status": "pending",
            "signature_verified": True,
            "meaning": "Cryptographic verification against a reviewed key; attribution promotion requires review.",
        },
        case_id,
        id=identifier,
    )
    audit(db, user, "feedback.imported", case_id, {"record_id": out.id, "sha256": h})
    db.commit()
    return as_dict(out)


@app.get("/api/analyses/{job_id}/snapshot")
def snapshot_download(job_id: str, user=Depends(principal), db=Depends(get_db)):
    j = job_access(db, user, job_id)
    if not j.result:
        raise HTTPException(409, "Analysis is not available")
    audit(db, user, "snapshot.exported", j.case_id, {"job_id": j.id})
    db.commit()
    return Response(
        read_artifact(j.result["snapshot_sha256"]),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{j.id}-snapshot.json"'},
    )


@app.get("/api/analyses/{job_id}/evidence/{sha256}")
def raw_evidence(job_id: str, sha256: str, user=Depends(principal), db=Depends(get_db)):
    j = job_access(db, user, job_id)
    if not j.result or sha256 not in {x["sha256"] for x in j.result.get("raw_evidence", [])}:
        raise HTTPException(404, "Evidence not found in this analysis")
    audit(db, user, "evidence.viewed", j.case_id, {"job_id": j.id, "sha256": sha256})
    db.commit()
    return Response(read_artifact(sha256), media_type="application/json")


@app.get("/api/analyses/{job_id}/report.pdf")
def report_download(job_id: str, user=Depends(principal), db=Depends(get_db)):
    j = job_access(db, user, job_id)
    require_current_evidence(db, j)
    c = case_access(db, user, j.case_id)
    if not j.result:
        raise HTTPException(409, "Analysis is not available")
    data = pdf_report(as_dict(c), j, j.result["analysis"])
    h = artifact(data)
    audit(db, user, "report.exported", c.id, {"job_id": j.id, "sha256": h})
    db.commit()
    return Response(
        data,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{j.id}-report.pdf"'},
    )


@app.get("/api/analyses/{job_id}/bundle.zip")
def bundle_download(job_id: str, user=Depends(principal), db=Depends(get_db)):
    j = job_access(db, user, job_id)
    require_current_evidence(db, j)
    c = case_access(db, user, j.case_id)
    if not j.result:
        raise HTTPException(409, "Analysis is not available")
    rows = [
        {"id": a.id, "actor": a.actor, "action": a.action, "details": a.details, "created": a.created}
        for a in db.scalars(
            select(Audit).where(Audit.tenant == user.tenant, Audit.target == j.case_id).order_by(Audit.id)
        )
    ]
    data, fp = make_bundle(as_dict(c), j, rows)
    h = artifact(data)
    audit(db, user, "bundle.exported", c.id, {"job_id": j.id, "sha256": h, "signer_sha256": fp})
    db.commit()
    return Response(
        data,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{j.id}-evidence.zip"', "X-Signer-SHA256": fp},
    )


@app.post("/api/evidence/verify")
async def verify(file: UploadFile = File(...), user=Depends(principal)):
    data = await file.read(settings.max_body_bytes + 1)
    if len(data) > settings.max_body_bytes:
        raise HTTPException(413, "Bundle too large")
    try:
        return verify_bundle(data)
    except ValueError as exc:
        raise HTTPException(422, "Bundle verification failed: " + str(exc)[:300])
    except Exception:
        raise HTTPException(
            422, "Bundle verification failed: signature, member hashes, schema, or replay mismatch"
        )


@app.get("/api/cases/{case_id}/audit")
def case_audit(case_id: str, user=Depends(principal), db=Depends(get_db)):
    case_access(db, user, case_id)
    return [
        {
            "id": a.id,
            "actor": a.actor,
            "action": a.action,
            "target": a.target,
            "details": a.details,
            "created": a.created,
        }
        for a in db.scalars(
            select(Audit)
            .where(Audit.tenant == user.tenant, Audit.target == case_id)
            .order_by(Audit.id.desc())
            .limit(1000)
        )
    ]


@app.get("/api/fixtures/training")
def fixture(user=Depends(principal)):
    return training_snapshot().model_dump()


@app.get("/api/fixtures/cctp-review")
def cctp_fixture(user=Depends(principal)):
    return bridge_snapshot().model_dump()


@app.get("/api/docs", include_in_schema=False)
def api_docs():
    from fastapi.responses import HTMLResponse

    return HTMLResponse(
        '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>TraceSetu API</title></head><body><h1>TraceSetu API</h1><p>Independent investigation API. <a href="/api/openapi.json">Download the OpenAPI schema</a>.</p><p>Sign in using POST /api/auth/login. Cookies carry the session; authenticated writes require X-CSRF-Token returned by sign-in. Analysis creation requires an Idempotency-Key header.</p><p>Versioned evidence contracts and operational instructions are included in the project README and documentation. This page uses no external scripts or services.</p><p><a href="/">Return to the investigation workspace</a></p></body></html>'
    )


@app.post("/api/cases/{case_id}/watches", status_code=201)
def add_watch(case_id: str, data: WatchCreate, user=Depends(principal), db=Depends(get_db)):
    require_role(user, "admin", "investigator")
    c = case_access(db, user, case_id)
    if c.payload["status"] == "Closed":
        raise HTTPException(409, "Reopen case to add a watch")
    data.spec.address = validate_address(data.spec.chain, data.spec.address)
    r = record(
        db,
        "watch",
        user.tenant,
        {
            **data.model_dump(),
            "created_by": user.id,
            "next_run": now(),
            "last_job_id": None,
            "baseline": None,
        },
        case_id,
    )
    audit(db, user, "watch.created", case_id, {"record_id": r.id})
    db.commit()
    return as_dict(r)


@app.post("/api/watches/{record_id}/toggle")
def toggle_watch(record_id: str, user=Depends(principal), db=Depends(get_db)):
    require_role(user, "admin", "investigator")
    r = object_access(db, user, record_id, "watch")
    patch_record(r, {"enabled": not r.payload["enabled"]})
    audit(db, user, "watch.toggled", r.case_id, {"record_id": r.id, "enabled": r.payload["enabled"]})
    db.commit()
    return as_dict(r)


dist = ROOT / "frontend" / "dist"
if (dist / "assets").exists():
    app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")


@app.get("/favicon.svg", include_in_schema=False)
def favicon():
    return FileResponse(ROOT / "frontend" / "public" / "favicon.svg")


@app.get("/", include_in_schema=False)
def index():
    if (dist / "index.html").exists():
        return FileResponse(dist / "index.html")
    return {"message": "Build the frontend or start Vite on port 5173. API is running.", "docs": "/api/docs"}
