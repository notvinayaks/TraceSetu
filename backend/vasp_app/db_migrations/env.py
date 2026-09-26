"""All online migrations use a caller-owned locked transaction, never a URL in an ini file."""
from alembic import context

connection = context.config.attributes.get("connection")
if connection is None:
    raise RuntimeError("Use python -m vasp_app.manage db-upgrade to run migrations")
context.configure(connection=connection, transactional_ddl=True, compare_type=True)
with context.begin_transaction():
    context.run_migrations()
