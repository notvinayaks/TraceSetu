"""Persist worker heartbeat without storing hostnames, credentials or case identifiers."""
import sqlalchemy as sa
from alembic import op

revision = "0002_worker_health"
down_revision = "0001_original"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("worker_heartbeats",
        sa.Column("id", sa.String(48), primary_key=True),
        sa.Column("started", sa.Float, nullable=False),
        sa.Column("last_seen", sa.Float, nullable=False),
        sa.Column("status", sa.String(24), nullable=False))
    op.create_index("ix_worker_heartbeats_last_seen", "worker_heartbeats", ["last_seen"])


def downgrade():
    op.drop_index("ix_worker_heartbeats_last_seen", table_name="worker_heartbeats")
    op.drop_table("worker_heartbeats")
