from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from api.models.base import Base


class VehiclePosition(Base):
    """Historical log of every polled vehicle position (populated starting Sprint 3)."""

    __tablename__ = "vehicle_positions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vehicle_id: Mapped[str] = mapped_column(String(32))
    line: Mapped[str] = mapped_column(String(16))
    geom: Mapped[str] = mapped_column(Geometry(geometry_type="POINT", srid=4326))
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    trip_id: Mapped[str | None] = mapped_column(
        ForeignKey("trips.trip_id"), nullable=True
    )
    delay_s: Mapped[int | None] = mapped_column(Integer, nullable=True)


class VehicleState(Base):
    """Latest known state per vehicle, for fast map queries."""

    __tablename__ = "vehicle_state"

    vehicle_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    line: Mapped[str | None] = mapped_column(String(16), nullable=True)
    geom: Mapped[str | None] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=True
    )
    recorded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    trip_id: Mapped[str | None] = mapped_column(
        ForeignKey("trips.trip_id"), nullable=True
    )
    delay_s: Mapped[int | None] = mapped_column(Integer, nullable=True)
