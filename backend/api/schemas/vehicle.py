from datetime import datetime

from pydantic import BaseModel, ConfigDict


class VehicleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    line_id: int
    label: str
    lat: float
    lon: float
    updated_at: datetime
