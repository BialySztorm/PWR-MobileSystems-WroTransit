from pydantic import BaseModel, ConfigDict


class StopRead(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "stop_id": "1",
                "stop_code": "1",
                "name": "Rynek",
                "lat": 51.1101,
                "lon": 17.0326,
                "modes": [0, 3],
            }
        }
    )

    stop_id: str
    stop_code: str | None
    name: str
    lat: float
    lon: float
    modes: list[int] = []
    """Distinct GTFS route_type values served here: 0 = tram, 3 = bus. Only populated for
    bbox (map) queries; empty for plain search results."""


class StopNearbyRead(StopRead):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "stop_id": "1",
                "stop_code": "1",
                "name": "Rynek",
                "lat": 51.1101,
                "lon": 17.0326,
                "modes": [],
                "distance_m": 123.4,
            }
        }
    )

    distance_m: float
