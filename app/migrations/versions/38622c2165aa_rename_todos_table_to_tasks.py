"""rename todos table to tasks

Revision ID: 38622c2165aa
Revises: 23f050738acb
Create Date: 2026-08-15 19:17:31.456056

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '38622c2165aa'
down_revision: Union[str, Sequence[str], None] = '23f050738acb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.rename_table("todos", "tasks")


def downgrade():
    op.rename_table("tasks", "todos")