from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from api.models.base import Base


class Route(Base):
    __tablename__ = "routes"

    route_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    short_name: Mapped[str] = mapped_column(String(16))
    long_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    type: Mapped[int] = mapped_column(Integer)
    """GTFS route_type: 0 = tram, 3 = bus (others are unused by this feed)."""
