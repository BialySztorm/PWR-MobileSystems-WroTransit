"""add vehicle_type to vehicle_positions/vehicle_state

Revision ID: 4cf4aff76de1
Revises: b2c1a7e4f9d3
Create Date: 2026-11-14
"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4cf4aff76de1"
down_revision = "b2c1a7e4f9d3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "vehicle_positions", sa.Column("vehicle_type", sa.String(length=8), nullable=True)
    )
    op.add_column(
        "vehicle_state", sa.Column("vehicle_type", sa.String(length=8), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("vehicle_state", "vehicle_type")
    op.drop_column("vehicle_positions", "vehicle_type")
