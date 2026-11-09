from geoalchemy2 import Geometry
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from api.models.base import Base


class Shape(Base):
    __tablename__ = "shapes"

    shape_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    geom: Mapped[str] = mapped_column(Geometry(geometry_type="LINESTRING", srid=4326))
