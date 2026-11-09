"""create GTFS schedule, vehicle and user schema

Revision ID: b2c1a7e4f9d3
Revises:
Create Date: 2026-11-09
"""
import geoalchemy2
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b2c1a7e4f9d3"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.create_table(
        "stops",
        sa.Column("stop_id", sa.String(length=32), primary_key=True),
        sa.Column("stop_code", sa.String(length=32), nullable=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column(
            "geom",
            geoalchemy2.types.Geometry(geometry_type="POINT", srid=4326),
            nullable=False,
        ),
    )
    op.create_index("ix_stops_geom", "stops", ["geom"], postgresql_using="gist")

    op.create_table(
        "routes",
        sa.Column("route_id", sa.String(length=32), primary_key=True),
        sa.Column("short_name", sa.String(length=16), nullable=False),
        sa.Column("long_name", sa.String(length=255), nullable=True),
        sa.Column("type", sa.Integer(), nullable=False),
    )

    op.create_table(
        "shapes",
        sa.Column("shape_id", sa.String(length=32), primary_key=True),
        sa.Column(
            "geom",
            geoalchemy2.types.Geometry(geometry_type="LINESTRING", srid=4326),
            nullable=False,
        ),
    )
    op.create_index("ix_shapes_geom", "shapes", ["geom"], postgresql_using="gist")

    op.create_table(
        "calendar",
        sa.Column("service_id", sa.String(length=32), primary_key=True),
        sa.Column("monday", sa.Boolean(), nullable=False),
        sa.Column("tuesday", sa.Boolean(), nullable=False),
        sa.Column("wednesday", sa.Boolean(), nullable=False),
        sa.Column("thursday", sa.Boolean(), nullable=False),
        sa.Column("friday", sa.Boolean(), nullable=False),
        sa.Column("saturday", sa.Boolean(), nullable=False),
        sa.Column("sunday", sa.Boolean(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
    )

    op.create_table(
        "calendar_dates",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("service_id", sa.String(length=32), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("exception_type", sa.Integer(), nullable=False),
    )

    op.create_table(
        "trips",
        sa.Column("trip_id", sa.String(length=32), primary_key=True),
        sa.Column(
            "route_id", sa.String(length=32), sa.ForeignKey("routes.route_id"), nullable=False
        ),
        sa.Column("service_id", sa.String(length=32), nullable=False),
        sa.Column("direction_id", sa.Integer(), nullable=True),
        sa.Column(
            "shape_id", sa.String(length=32), sa.ForeignKey("shapes.shape_id"), nullable=True
        ),
        sa.Column("headsign", sa.String(length=120), nullable=True),
    )

    op.create_table(
        "stop_times",
        sa.Column(
            "trip_id", sa.String(length=32), sa.ForeignKey("trips.trip_id"), primary_key=True
        ),
        sa.Column("stop_sequence", sa.Integer(), primary_key=True),
        sa.Column(
            "stop_id", sa.String(length=32), sa.ForeignKey("stops.stop_id"), nullable=False
        ),
        sa.Column("arrival_time_s", sa.Integer(), nullable=False),
        sa.Column("departure_time_s", sa.Integer(), nullable=False),
    )
    op.create_index("ix_stop_times_stop_id", "stop_times", ["stop_id"])

    op.create_table(
        "vehicle_positions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("vehicle_id", sa.String(length=32), nullable=False),
        sa.Column("line", sa.String(length=16), nullable=False),
        sa.Column(
            "geom",
            geoalchemy2.types.Geometry(geometry_type="POINT", srid=4326),
            nullable=False,
        ),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "trip_id", sa.String(length=32), sa.ForeignKey("trips.trip_id"), nullable=True
        ),
        sa.Column("delay_s", sa.Integer(), nullable=True),
    )

    op.create_table(
        "vehicle_state",
        sa.Column("vehicle_id", sa.String(length=32), primary_key=True),
        sa.Column("line", sa.String(length=16), nullable=True),
        sa.Column(
            "geom",
            geoalchemy2.types.Geometry(geometry_type="POINT", srid=4326),
            nullable=True,
        ),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "trip_id", sa.String(length=32), sa.ForeignKey("trips.trip_id"), nullable=True
        ),
        sa.Column("delay_s", sa.Integer(), nullable=True),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "favourite_stops",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column(
            "stop_id", sa.String(length=32), sa.ForeignKey("stops.stop_id"), primary_key=True
        ),
    )

    op.create_table(
        "favourite_lines",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column(
            "route_id",
            sa.String(length=32),
            sa.ForeignKey("routes.route_id"),
            primary_key=True,
        ),
    )

    op.create_table(
        "devices",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("fcm_token", sa.String(length=255), nullable=False),
        sa.Column("notify_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
    )


def downgrade() -> None:
    op.drop_table("devices")
    op.drop_table("favourite_lines")
    op.drop_table("favourite_stops")
    op.drop_table("users")
    op.drop_table("vehicle_state")
    op.drop_table("vehicle_positions")
    op.drop_table("stop_times")
    op.drop_table("trips")
    op.drop_table("calendar_dates")
    op.drop_table("calendar")
    op.drop_index("ix_shapes_geom", table_name="shapes")
    op.drop_table("shapes")
    op.drop_table("routes")
    op.drop_index("ix_stops_geom", table_name="stops")
    op.drop_table("stops")
