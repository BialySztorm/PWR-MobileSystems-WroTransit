from pydantic import BaseModel, ConfigDict

from api.schemas.stop import StopRead


class RouteRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "route_id": "4",
                "short_name": "4",
                "long_name": None,
                "type": 0,
            }
        },
    )

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
