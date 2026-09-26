"""Frozen original schema; do not replace with the evolving application metadata."""
import sqlalchemy as sa
from alembic import op

revision = "0001_original"
down_revision = None
branch_labels = None
depends_on = None


def metadata():
    m = sa.MetaData()
    sa.Table("users", m,
        sa.Column("id", sa.String(48), primary_key=True),
        sa.Column("tenant", sa.String(80), nullable=False, index=True),
        sa.Column("username", sa.String(100), nullable=False, unique=True),
        sa.Column("display_name", sa.String(120), nullable=False),
        sa.Column("password_hash", sa.Text, nullable=False),
        sa.Column("role", sa.String(24), nullable=False),
        sa.Column("active", sa.Integer, nullable=False))
    sa.Table("sessions", m,
        sa.Column("token_hash", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.String(48), nullable=False, index=True),
        sa.Column("csrf", sa.String(100), nullable=False),
        sa.Column("expires", sa.Float, nullable=False))
    sa.Table("records", m,
        sa.Column("id", sa.String(48), primary_key=True),
        sa.Column("kind", sa.String(30), nullable=False, index=True),
        sa.Column("tenant", sa.String(80), nullable=False, index=True),
        sa.Column("case_id", sa.String(48), nullable=True, index=True),
        sa.Column("payload", sa.JSON, nullable=False),
        sa.Column("version", sa.Integer, nullable=False),
        sa.Column("created", sa.Float, nullable=False),
        sa.Column("updated", sa.Float, nullable=False))
    sa.Table("jobs", m,
        sa.Column("id", sa.String(48), primary_key=True),
        sa.Column("tenant", sa.String(80), nullable=False, index=True),
        sa.Column("case_id", sa.String(48), nullable=False, index=True),
        sa.Column("actor_id", sa.String(48), nullable=False),
        sa.Column("idempotency", sa.String(128), nullable=False),
        sa.Column("input_hash", sa.String(64), nullable=False),
        sa.Column("request", sa.JSON, nullable=False),
        sa.Column("status", sa.String(32), nullable=False, index=True),
        sa.Column("stage", sa.String(80), nullable=False),
        sa.Column("result", sa.JSON, nullable=True),
        sa.Column("error", sa.Text, nullable=True),
        sa.Column("lease_until", sa.Float, nullable=False),
        sa.Column("attempts", sa.Integer, nullable=False),
        sa.Column("created", sa.Float, nullable=False),
        sa.Column("updated", sa.Float, nullable=False),
        sa.UniqueConstraint("tenant", "idempotency", name="job_idempotency"))
    sa.Table("audit", m,
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("tenant", sa.String(80), nullable=False, index=True),
        sa.Column("actor", sa.String(48), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("target", sa.String(80), nullable=False),
        sa.Column("details", sa.JSON, nullable=False),
        sa.Column("created", sa.Float, nullable=False))
    return m


def upgrade():
    metadata().create_all(op.get_bind(), checkfirst=False)


def downgrade():
    raise RuntimeError("Removing the original evidence schema is prohibited; restore a verified backup")
