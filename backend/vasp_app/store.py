from __future__ import annotations
import hashlib
import json
import uuid
from datetime import datetime, timezone
from sqlalchemy import create_engine, String, Text, Integer, Float, JSON, UniqueConstraint, event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from .config import settings


def now() -> float:
    return datetime.now(timezone.utc).timestamp()


def uid(prefix: str = "") -> str:
    return prefix + uuid.uuid4().hex


def canonical(value) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode()


def digest(value) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    tenant: Mapped[str] = mapped_column(String(80), index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    display_name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(String(24))
    active: Mapped[int] = mapped_column(Integer, default=1)


class Session(Base):
    __tablename__ = "sessions"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(48), index=True)
    csrf: Mapped[str] = mapped_column(String(100))
    expires: Mapped[float] = mapped_column(Float)


class Record(Base):
    __tablename__ = "records"
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    kind: Mapped[str] = mapped_column(String(30), index=True)
    tenant: Mapped[str] = mapped_column(String(80), index=True)
    case_id: Mapped[str | None] = mapped_column(String(48), nullable=True, index=True)
    payload: Mapped[dict] = mapped_column(JSON)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created: Mapped[float] = mapped_column(Float, default=now)
    updated: Mapped[float] = mapped_column(Float, default=now)


class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    tenant: Mapped[str] = mapped_column(String(80), index=True)
    case_id: Mapped[str] = mapped_column(String(48), index=True)
    actor_id: Mapped[str] = mapped_column(String(48))
    idempotency: Mapped[str] = mapped_column(String(128))
    input_hash: Mapped[str] = mapped_column(String(64))
    request: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(32), default="QUEUED", index=True)
    stage: Mapped[str] = mapped_column(String(80), default="Waiting for worker")
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    lease_until: Mapped[float] = mapped_column(Float, default=0)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    created: Mapped[float] = mapped_column(Float, default=now)
    updated: Mapped[float] = mapped_column(Float, default=now)
    __table_args__ = (UniqueConstraint("tenant", "idempotency", name="job_idempotency"),)


class Audit(Base):
    __tablename__ = "audit"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant: Mapped[str] = mapped_column(String(80), index=True)
    actor: Mapped[str] = mapped_column(String(48))
    action: Mapped[str] = mapped_column(String(100))
    target: Mapped[str] = mapped_column(String(80))
    details: Mapped[dict] = mapped_column(JSON)
    created: Mapped[float] = mapped_column(Float, default=now)


settings.data_dir.mkdir(parents=True, exist_ok=True)
kwargs = (
    {"connect_args": {"check_same_thread": False, "timeout": 30}}
    if settings.database_url.startswith("sqlite")
    else {}
)
engine = create_engine(settings.database_url, pool_pre_ping=True, **kwargs)
if settings.database_url.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def sqlite_setup(conn, _):
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")


SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def audit(db, user, action, target, details=None):
    db.add(Audit(tenant=user.tenant, actor=user.id, action=action, target=target, details=details or {}))


def record(db, kind, tenant, payload, case_id=None, id=None):
    r = Record(id=id or uid(kind[:3] + "_"), kind=kind, tenant=tenant, case_id=case_id, payload=payload)
    db.add(r)
    return r


def patch_record(r, payload):
    r.payload = {**r.payload, **payload}
    r.version += 1
    r.updated = now()


def artifact(data: bytes) -> str:
    h = hashlib.sha256(data).hexdigest()
    folder = settings.data_dir / "objects" / h[:2]
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / h
    if not path.exists():
        tmp = folder / (h + "." + uuid.uuid4().hex + ".tmp")
        tmp.write_bytes(data)
        tmp.replace(path)
    return h


def read_artifact(h: str) -> bytes:
    if len(h) != 64 or any(ch not in "0123456789abcdef" for ch in h):
        raise ValueError("Invalid artifact hash")
    data = (settings.data_dir / "objects" / h[:2] / h).read_bytes()
    if hashlib.sha256(data).hexdigest() != h:
        raise ValueError("Artifact failed integrity verification")
    return data


def as_dict(r):
    return {
        **r.payload,
        "id": r.id,
        "kind": r.kind,
        "case_id": r.case_id,
        "version": r.version,
        "created": r.created,
        "updated": r.updated,
    }
