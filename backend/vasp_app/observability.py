"""Strict allowlisted operational events: no request bodies, URLs, secrets or case data."""
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from sqlalchemy import func, select, text
from sqlalchemy.exc import SQLAlchemyError
from .config import settings
from .store import SessionLocal, Job, WorkerHeartbeat, engine, now
from .migrations import expected_revision, revision

LOGGER = logging.getLogger("tracesetu.operations")
FIELDS = {"event", "request_id", "method", "route", "status", "duration_ms", "error_type", "component"}


class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {"timestamp": datetime.now(timezone.utc).isoformat(), "level": record.levelname}
        event = getattr(record, "operational", {})
        payload.update({key: value for key, value in event.items() if key in FIELDS})
        # Message arguments/tracebacks may contain URL credentials; never render them.
        if "event" not in payload:
            payload["event"] = "operational_log"
        return json.dumps(payload, ensure_ascii=True, allow_nan=False)


def configure_logging():
    if not settings.json_logs:
        return
    if not LOGGER.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        LOGGER.addHandler(handler)
    LOGGER.setLevel(logging.INFO)
    LOGGER.propagate = False


def emit(event, **fields):
    LOGGER.info("", extra={"operational": {"event": event, **fields}})


class OperationalMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        started, request_id, status = time.monotonic(), uuid.uuid4().hex, 500
        error_type = None

        async def wrapped_send(message):
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
                message["headers"] = list(message.get("headers", [])) + [(b"x-request-id", request_id.encode())]
            await send(message)

        try:
            await self.app(scope, receive, wrapped_send)
        except Exception as exc:
            error_type = type(exc).__name__
            raise
        finally:
            route = getattr(scope.get("route"), "path", "unmatched")
            # Match route templates, not literal paths or query strings supplied by the caller.
            emit("http_request", request_id=request_id, method=scope.get("method"), route=route,
                 status=status, duration_ms=round((time.monotonic() - started) * 1000, 2), error_type=error_type)


def readiness():
    components = {"database": False, "schema": False, "evidence_storage": False, "worker": False}
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            components["database"] = True
            components["schema"] = revision(conn) == expected_revision()
        if components["schema"]:
            with SessionLocal() as db:
                components["worker"] = bool(db.scalar(select(func.count()).select_from(WorkerHeartbeat).where(
                    WorkerHeartbeat.status == "running",
                    WorkerHeartbeat.last_seen >= now() - settings.worker_stale_seconds)))
    except (SQLAlchemyError, OSError):
        pass
    try:
        import tempfile
        with tempfile.TemporaryFile(dir=settings.data_dir) as probe:
            probe.write(b"tracesetu-readiness")
            probe.flush()
        components["evidence_storage"] = True
    except OSError:
        pass
    required = ("database", "schema", "evidence_storage") + (("worker",) if settings.readiness_requires_worker else ())
    return {"ready": all(components[k] for k in required), "components": components,
            "worker_required": settings.readiness_requires_worker}


def tenant_operations(tenant):
    with SessionLocal() as db:
        statuses = dict(db.execute(select(Job.status, func.count()).where(Job.tenant == tenant).group_by(Job.status)).all())
        oldest = db.scalar(select(func.min(Job.created)).where(Job.tenant == tenant, Job.status == "QUEUED"))
        expired = db.scalar(select(func.count()).select_from(Job).where(
            Job.tenant == tenant, Job.status == "RUNNING", Job.lease_until < now()))
    return {"jobs": statuses, "oldest_queued_seconds": max(0, int(now() - oldest)) if oldest else 0,
            "expired_running_leases": expired}
