"""Add assign_chores to people

Revision ID: 6f2d3b8a5a11
Revises: b17de874045a
Create Date: 2026-05-07 00:00:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6f2d3b8a5a11"
down_revision: str | None = "b17de874045a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "people",
        sa.Column(
            "assign_chores",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("people", "assign_chores")
