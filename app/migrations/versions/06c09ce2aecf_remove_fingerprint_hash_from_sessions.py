"""remove_fingerprint_hash_from_sessions

Revision ID: 06c09ce2aecf
Revises: 374d7e76b4cc
Create Date: 2026-08-19 12:10:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "06c09ce2aecf"
down_revision: Union[str, Sequence[str], None] = "374d7e76b4cc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("sessions", "fingerprint_hash")


def downgrade() -> None:
    op.add_column(
        "sessions",
        sa.Column("fingerprint_hash", sa.String(), nullable=True),
    )
