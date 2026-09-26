"""Runs only against an explicitly configured disposable PostgreSQL test database."""
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
import pytest
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from alembic import command
from vasp_app.migrations import upgrade, expected_revision, original_metadata, configuration, revision
from vasp_app.store import Job
from vasp_app import worker


@pytest.fixture
def postgres():
    url = os.environ.get("ATLAS_TEST_POSTGRES_URL")
    if not url:
        pytest.skip("Disposable PostgreSQL URL not configured")
    parsed = make_url(url)
    if parsed.drivername != "postgresql+psycopg" or not parsed.database.startswith("tracesetu_test"):
        pytest.fail("Refusing a non-test PostgreSQL database; use tracesetu_test* and psycopg")
    schema = "atlas_test_" + uuid.uuid4().hex
    admin = create_engine(url, hide_parameters=True)
    with admin.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA "{schema}"'))
    engine = create_engine(url, hide_parameters=True, pool_size=12,
        connect_args={"options": "-c search_path=" + schema})
    try:
        yield engine
    finally:
        engine.dispose()
        with admin.begin() as conn:
            conn.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        admin.dispose()


def test_postgres_migration_and_non_destructive_rollback(postgres):
    original_metadata().create_all(postgres)
    with postgres.begin() as conn:
        conn.execute(text("INSERT INTO records VALUES ('retained', 'case', 'agency', NULL, :payload, 1, 1, 1)"),
            {"payload": '{"title":"Preserve investigation"}'})
    assert upgrade(postgres, adopt_legacy=True) == expected_revision()
    with postgres.begin() as conn:
        assert conn.execute(text("SELECT payload FROM records WHERE id='retained'")).scalar_one()["title"] == "Preserve investigation"
        command.downgrade(configuration(conn), "0001_original")
        assert revision(conn) == "0001_original"
    assert "worker_heartbeats" not in inspect(postgres).get_table_names()
    assert upgrade(postgres) == expected_revision()


def test_postgres_concurrent_migration_and_claims(postgres, monkeypatch):
    with ThreadPoolExecutor(max_workers=4) as pool:
        revisions = list(pool.map(lambda _: upgrade(postgres), range(4)))
    assert revisions == [expected_revision()] * 4
    sessions = sessionmaker(bind=postgres, expire_on_commit=False)
    with sessions() as db:
        for n in range(12):
            db.add(Job(id=f"job_pg_{n}", tenant="one", case_id="case", actor_id="actor",
                idempotency=f"key-{n}", input_hash="h", request={}, status="QUEUED"))
        db.commit()
    monkeypatch.setattr(worker, "SessionLocal", sessions)
    with ThreadPoolExecutor(max_workers=12) as pool:
        claims = list(pool.map(lambda _: worker.claim_one(with_token=True), range(12)))
    assert all(claims)
    assert len({c[0] for c in claims}) == 12
    assert all(c[1] == 1 for c in claims)
    assert worker.claim_one() is None
