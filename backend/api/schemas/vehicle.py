from datetime import datetime

from pydantic import BaseModel


class VehicleStateRead(BaseModel):
    vehicle_id: str
    line: str | None
    lat: float | None
    lon: float | None
    recorded_at: datetime | None
    delay_s: int | None
