from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from api.models.base import Base


class StopTime(Base):
    __tablename__ = "stop_times"

    trip_id: Mapped[str] = mapped_column(ForeignKey("trips.trip_id"), primary_key=True)
    stop_sequence: Mapped[int] = mapped_column(Integer, primary_key=True)
    stop_id: Mapped[str] = mapped_column(ForeignKey("stops.stop_id"))
    arrival_time_s: Mapped[int] = mapped_column(Integer)
    departure_time_s: Mapped[int] = mapped_column(Integer)
    """Seconds since midnight of the service day; GTFS allows > 86400 for past-midnight trips."""
