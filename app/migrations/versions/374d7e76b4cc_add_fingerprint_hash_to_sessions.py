"""add_fingerprint_hash_to_sessions

Revision ID: 374d7e76b4cc
Revises: c1a2d3e4f5a6
Create Date: 2026-08-19 11:45:54.309535

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "374d7e76b4cc"
down_revision: Union[str, Sequence[str], None] = "c1a2d3e4f5a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "sessions",
        sa.Column("fingerprint_hash", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("sessions", "fingerprint_hash")
