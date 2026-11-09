from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from api.models.base import Base


class Trip(Base):
    __tablename__ = "trips"

    trip_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    route_id: Mapped[str] = mapped_column(ForeignKey("routes.route_id"))
    service_id: Mapped[str] = mapped_column(String(32))
    """Not a FK: calendar_dates.txt may define a service_id with no row in calendar.txt."""
    direction_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shape_id: Mapped[str | None] = mapped_column(
        ForeignKey("shapes.shape_id"), nullable=True
    )
    headsign: Mapped[str | None] = mapped_column(String(120), nullable=True)
