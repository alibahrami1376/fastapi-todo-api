"""change task due_date from datetime to date

Revision ID: 8c4e1b9f2a70
Revises: 38622c2165aa
Create Date: 2026-08-17 23:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "8c4e1b9f2a70"
down_revision: Union[str, Sequence[str], None] = "38622c2165aa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "tasks",
        "due_date",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        type_=sa.Date(),
        existing_nullable=True,
        postgresql_using="due_date::date",
    )


def downgrade() -> None:
    op.alter_column(
        "tasks",
        "due_date",
        existing_type=sa.Date(),
        type_=postgresql.TIMESTAMP(timezone=True),
        existing_nullable=True,
        postgresql_using="due_date::timestamp with time zone",
    )
