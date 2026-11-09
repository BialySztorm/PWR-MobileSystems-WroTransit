from pydantic import BaseModel, ConfigDict

from api.schemas.stop import StopRead


class RouteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    route_id: str
    short_name: str
    long_name: str | None
    type: int
    """GTFS route_type: 0 = tram, 3 = bus."""


class RouteStopRead(BaseModel):
    sequence: int
    stop: StopRead


class RouteShapeRead(BaseModel):
    route_id: str
    direction_id: int | None
    stops: list[RouteStopRead]
