from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.base import Base


class Route(Base):
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(primary_key=True)
    line_id: Mapped[int] = mapped_column(ForeignKey("lines.id"))

    stops: Mapped[list["RouteStop"]] = relationship(
        back_populates="route", order_by="RouteStop.sequence"
    )


class RouteStop(Base):
    __tablename__ = "route_stops"

    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id"), primary_key=True)
    stop_id: Mapped[int] = mapped_column(ForeignKey("stops.id"), primary_key=True)
    sequence: Mapped[int] = mapped_column(Integer)

    route: Mapped[Route] = relationship(back_populates="stops")
    stop: Mapped["Stop"] = relationship()
