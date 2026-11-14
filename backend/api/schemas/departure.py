from pydantic import BaseModel, ConfigDict


class DepartureRead(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "route_short_name": "4",
                "route_type": 0,
                "headsign": "Osobowice",
                "direction_id": 0,
                "departure_time_s": 31500,
            }
        }
    )

    route_short_name: str
    route_type: int
    headsign: str | None
    direction_id: int | None
    departure_time_s: int
    """Seconds since midnight of the service day; may exceed 86400 for past-midnight trips."""
