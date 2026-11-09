"""create stop, line, route, vehicle tables

Revision ID: a1f0c9d8b3e1
Revises:
Create Date: 2026-11-09
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "a1f0c9d8b3e1"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "stops",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lon", sa.Float(), nullable=False),
    )
    op.create_table(
        "lines",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=10), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("color", sa.String(length=7), nullable=True),
    )
    op.create_table(
        "routes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("line_id", sa.Integer(), sa.ForeignKey("lines.id"), nullable=False),
    )
    op.create_table(
        "route_stops",
        sa.Column("route_id", sa.Integer(), sa.ForeignKey("routes.id"), primary_key=True),
        sa.Column("stop_id", sa.Integer(), sa.ForeignKey("stops.id"), primary_key=True),
        sa.Column("sequence", sa.Integer(), nullable=False),
    )
    op.create_table(
        "vehicles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("line_id", sa.Integer(), sa.ForeignKey("lines.id"), nullable=False),
        sa.Column("label", sa.String(length=20), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lon", sa.Float(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("vehicles")
    op.drop_table("route_stops")
    op.drop_table("routes")
    op.drop_table("lines")
    op.drop_table("stops")
