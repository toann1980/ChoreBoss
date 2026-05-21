"""add chore completion request approval fields

Revision ID: 8f9c3d2e7b4a
Revises: 6f2d3b8a5a11
Create Date: 2026-05-07 23:25:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8f9c3d2e7b4a"
down_revision = "6f2d3b8a5a11"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("chores", sa.Column("completion_requested_by_id", sa.Integer(), nullable=True))
    op.add_column("chores", sa.Column("completion_requested_at", sa.DateTime(), nullable=True))
    op.add_column("chores", sa.Column("completion_approved_by_id", sa.Integer(), nullable=True))
    op.add_column("chores", sa.Column("completion_approved_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("chores", "completion_approved_at")
    op.drop_column("chores", "completion_approved_by_id")
    op.drop_column("chores", "completion_requested_at")
    op.drop_column("chores", "completion_requested_by_id")
