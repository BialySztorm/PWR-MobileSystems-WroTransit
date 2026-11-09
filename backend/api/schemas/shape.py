from pydantic import BaseModel


class ShapeRead(BaseModel):
    shape_id: str
    coordinates: list[list[float]]
    """GeoJSON order: each point is [lon, lat]."""
    route_type: int | None
    """GTFS route_type of a route using this shape: 0 = tram, 3 = bus. None if orphaned."""
