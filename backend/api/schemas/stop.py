from pydantic import BaseModel


class StopRead(BaseModel):
    stop_id: str
    stop_code: str | None
    name: str
    lat: float
    lon: float
    modes: list[int] = []
    """Distinct GTFS route_type values served here: 0 = tram, 3 = bus. Only populated for
    bbox (map) queries; empty for plain search results."""
