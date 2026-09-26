import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
(ROOT / "tmp" / "tests").mkdir(parents=True, exist_ok=True)
DATA = Path(tempfile.mkdtemp(prefix="atlas-", dir=ROOT / "tmp" / "tests"))
os.environ["ATLAS_DATA_DIR"] = str(DATA)
test_url = os.environ.get("ATLAS_TEST_DATABASE_URL")
if test_url:
    from sqlalchemy.engine import make_url
    parsed = make_url(test_url)
    if parsed.drivername != "postgresql+psycopg" or not (parsed.database or "").startswith("tracesetu_test"):
        raise RuntimeError("Full-suite PostgreSQL tests require an explicitly named tracesetu_test database")
os.environ["ATLAS_DATABASE_URL"] = test_url or "sqlite:///" + str(DATA / "tests.sqlite3")
os.environ["ATLAS_LOCAL_BOOTSTRAP"] = "false"
os.environ["ATLAS_WORKER_ENABLED"] = "false"
os.environ["ATLAS_BITCOIN_PROVIDER"] = "esplora"
os.environ["ATLAS_ENVIRONMENT"] = "test"
os.environ["ATLAS_AUTO_MIGRATE"] = "true"
os.environ["ATLAS_READINESS_REQUIRES_WORKER"] = "false"

import pytest
from fastapi.testclient import TestClient
from vasp_app.store import Base, engine, SessionLocal, User
from vasp_app.security import password_hash
from vasp_app.main import app, _attempts
from vasp_app.migrations import upgrade


@pytest.fixture
def clients():
    Base.metadata.drop_all(engine)
    with engine.begin() as connection:
        connection.exec_driver_sql("DROP TABLE IF EXISTS alembic_version")
    upgrade(engine)
    _attempts.clear()
    with SessionLocal() as db:
        for name, role, tenant in [
            ("investigator", "investigator", "one"),
            ("reviewer", "reviewer", "one"),
            ("admin", "admin", "one"),
            ("outsider", "investigator", "two"),
            ("unassigned", "investigator", "one"),
        ]:
            db.add(
                User(
                    id=name,
                    tenant=tenant,
                    username=name,
                    display_name=name.title(),
                    role=role,
                    password_hash=password_hash("test-password-123456"),
                )
            )
        db.commit()
    result = {}
    with TestClient(app):
        for name in ["investigator", "reviewer", "admin", "outsider", "unassigned"]:
            client = TestClient(app)
            response = client.post(
                "/api/auth/login", json={"username": name, "password": "test-password-123456"}
            )
            assert response.status_code == 200, response.text
            client.headers["X-CSRF-Token"] = response.json()["csrf"]
            result[name] = client
        yield result
        for client in result.values():
            client.close()
