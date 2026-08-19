"""add indexes for task owner filters

Revision ID: c1a2d3e4f5a6
Revises: 8c4e1b9f2a70
Create Date: 2026-08-19 10:45:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "c1a2d3e4f5a6"
down_revision: Union[str, Sequence[str], None] = "8c4e1b9f2a70"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_tasks_owner_id",
        "tasks",
        ["owner_id"],
        unique=False,
    )
    op.create_index(
        "ix_tasks_owner_id_is_completed",
        "tasks",
        ["owner_id", "is_completed"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_tasks_owner_id_is_completed", table_name="tasks")
    op.drop_index("ix_tasks_owner_id", table_name="tasks")
