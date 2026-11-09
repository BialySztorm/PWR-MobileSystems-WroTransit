from pydantic import BaseModel


class DepartureRead(BaseModel):
    route_short_name: str
    route_type: int
    headsign: str | None
    direction_id: int | None
    departure_time_s: int
    """Seconds since midnight of the service day; may exceed 86400 for past-midnight trips."""
