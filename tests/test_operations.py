import io
import json
import logging
from vasp_app.config import Settings, settings
from vasp_app.store import SessionLocal, WorkerHeartbeat, Job, now
from vasp_app.observability import JsonFormatter


def test_production_configuration_rejects_development_defaults():
    import pytest
    with pytest.raises(ValueError, match="Production requires"):
        Settings(_env_file=None, environment="production", local_bootstrap=True)
    valid = Settings(_env_file=None, environment="production", auto_migrate=False,
        secure_cookie=True, local_bootstrap=False, allowed_hosts="tracesetu.example",
        allowed_origins="https://tracesetu.example")
    assert valid.secure_cookie
    with pytest.raises(ValueError, match="HTTPS"):
        Settings(_env_file=None, environment="production", auto_migrate=False,
            secure_cookie=True, local_bootstrap=False, allowed_hosts="tracesetu.example",
            allowed_origins="http://tracesetu.example")


def test_readiness_checks_stale_worker_without_exposing_details(clients, monkeypatch):
    client = clients["admin"]
    monkeypatch.setattr(settings, "readiness_requires_worker", True)
    assert client.get("/api/health").status_code == 200
    unavailable = client.get("/api/ready")
    assert unavailable.status_code == 503 and unavailable.json() == {"ready": False}
    with SessionLocal() as db:
        row = WorkerHeartbeat(id="worker-test", started=now(), last_seen=now(), status="running")
        db.add(row)
        db.commit()
    assert client.get("/api/ready").json() == {"ready": True}
    with SessionLocal() as db:
        db.get(WorkerHeartbeat, "worker-test").last_seen = now() - settings.worker_stale_seconds - 1
        db.commit()
    assert client.get("/api/ready").status_code == 503


def test_operations_is_admin_only_and_tenant_scoped(clients):
    assert clients["investigator"].get("/api/operations").status_code == 403
    assert clients["reviewer"].get("/api/operations").status_code == 403
    with SessionLocal() as db:
        for tenant in ("one", "two"):
            db.add(Job(id="job_" + tenant, tenant=tenant, case_id="private-case-" + tenant,
                actor_id="admin", idempotency=tenant, input_hash="h", request={}, status="QUEUED"))
        db.commit()
    result = clients["admin"].get("/api/operations")
    assert result.status_code == 200
    assert result.json()["tenant"]["jobs"] == {"QUEUED": 1}
    assert "private-case" not in result.text and "job_two" not in result.text


def test_logs_omit_secrets_literal_paths_and_untrusted_request_id(clients, caplog):
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())
    logger = logging.getLogger("tracesetu.operations")
    logger.addHandler(handler)
    try:
        response = clients["admin"].get("/api/analyses/private-wallet?apikey=secret-test-value",
            headers={"X-Request-ID": "attacker-secret", "Authorization": "Bearer secret-test-value"})
        assert response.status_code == 404
        assert len(response.headers["X-Request-ID"]) == 32
        line = json.loads(stream.getvalue().splitlines()[-1])
        assert line["route"] == "/api/analyses/{job_id}"
        assert "secret" not in stream.getvalue() and "private-wallet" not in stream.getvalue()
        record = logging.LogRecord("test", logging.ERROR, "", 0, "secret-test-value", (), None)
        record.operational = {"event": "failure", "password": "secret-test-value"}
        assert "secret" not in JsonFormatter().format(record)
    finally:
        logger.removeHandler(handler)
