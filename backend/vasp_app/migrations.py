"""Versioned, serialised schema changes with explicit legacy adoption."""
from pathlib import Path
import importlib.util
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import inspect, text

LOCATION = Path(__file__).parent / "db_migrations"


def configuration(connection=None):
    cfg = Config()
    cfg.set_main_option("script_location", str(LOCATION).replace("%", "%%"))
    cfg.attributes["connection"] = connection
    return cfg


def expected_revision():
    return ScriptDirectory.from_config(configuration()).get_current_head()


def revision(connection):
    if "alembic_version" not in inspect(connection).get_table_names():
        return None
    rows = connection.execute(text("SELECT version_num FROM alembic_version")).scalars().all()
    return rows[0] if len(rows) == 1 else None


def original_metadata():
    spec = importlib.util.spec_from_file_location("tracesetu_original_schema", LOCATION / "versions/0001_original.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.metadata()


def upgrade(engine, *, adopt_legacy=False, target="head"):
    """Caller must back up nonempty installations before enabling legacy adoption."""
    with engine.connect() as conn:
        try:
            if engine.dialect.name == "sqlite":
                conn.exec_driver_sql("BEGIN IMMEDIATE")
            elif engine.dialect.name == "postgresql":
                conn.execute(text("SELECT pg_advisory_xact_lock(8473926501)"))
            else:
                raise RuntimeError("Only SQLite and PostgreSQL migrations are supported")
            tables = set(inspect(conn).get_table_names()) - {"alembic_version"}
            current = revision(conn)
            if tables and current is None:
                if not adopt_legacy:
                    raise RuntimeError("Unversioned database: take a verified backup, then use db-upgrade --adopt-legacy")
                original = original_metadata()
                diff = compare_metadata(MigrationContext.configure(conn), original)
                if tables != set(original.tables) or diff:
                    raise RuntimeError("Legacy schema does not match the frozen baseline; no version was stamped")
                command.stamp(configuration(conn), "0001_original")
            command.upgrade(configuration(conn), target)
            current = revision(conn)
            conn.commit()
            return current
        except BaseException:
            conn.rollback()
            raise


def require_current(engine):
    with engine.connect() as conn:
        if revision(conn) != expected_revision():
            raise RuntimeError("Database migration required; run python -m vasp_app.manage db-upgrade")
