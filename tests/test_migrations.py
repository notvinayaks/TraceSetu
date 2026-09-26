from concurrent.futures import ThreadPoolExecutor
import pytest
from sqlalchemy import create_engine, inspect, text
from alembic import command
from vasp_app.migrations import upgrade, revision, expected_revision, original_metadata, configuration


def database(tmp_path):
    return create_engine("sqlite:///" + str(tmp_path / "migration.sqlite3"), connect_args={"timeout": 30})


def test_fresh_migration_is_repeatable_and_heartbeat_can_roll_back(tmp_path):
    engine = database(tmp_path)
    assert upgrade(engine) == expected_revision()
    assert upgrade(engine) == expected_revision()
    assert "worker_heartbeats" in inspect(engine).get_table_names()
    with engine.begin() as conn:
        command.downgrade(configuration(conn), "0001_original")
        assert revision(conn) == "0001_original"
    assert "worker_heartbeats" not in inspect(engine).get_table_names()
    assert upgrade(engine) == expected_revision()
    engine.dispose()


def test_legacy_adoption_is_explicit_and_preserves_records(tmp_path):
    engine = database(tmp_path)
    original_metadata().create_all(engine)
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO records VALUES ('case-old', 'case', 'agency', NULL, :payload, 1, 1, 1)"),
            {"payload": '{"title":"Retain this case"}'})
    with pytest.raises(RuntimeError, match="Unversioned"):
        upgrade(engine)
    assert upgrade(engine, adopt_legacy=True) == expected_revision()
    with engine.connect() as conn:
        assert "Retain this case" in conn.execute(text("SELECT payload FROM records WHERE id='case-old'")).scalar_one()
    engine.dispose()


def test_mismatched_legacy_is_not_stamped_or_changed(tmp_path):
    engine = database(tmp_path)
    original_metadata().create_all(engine)
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE records ADD COLUMN unexpected TEXT"))
    with pytest.raises(RuntimeError, match="does not match"):
        upgrade(engine, adopt_legacy=True)
    assert "alembic_version" not in inspect(engine).get_table_names()
    assert "unexpected" in {c["name"] for c in inspect(engine).get_columns("records")}
    engine.dispose()


def test_concurrent_upgrade_serializes(tmp_path):
    engine = database(tmp_path)
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: upgrade(engine), range(4)))
    assert results == [expected_revision()] * 4
    engine.dispose()
