from datetime import datetime

from pydantic import BaseModel, ConfigDict


class VehicleStateRead(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "vehicle_id": "14482003",
                "line": "4",
                "lat": 51.09238,
                "lon": 17.01899,
                "recorded_at": "2026-11-14T08:30:00Z",
                "delay_s": 95,
            }
        }
    )

    vehicle_id: str
    line: str | None
    lat: float | None
    lon: float | None
    recorded_at: datetime | None
    delay_s: int | None
