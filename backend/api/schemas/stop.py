from pydantic import BaseModel, ConfigDict


class StopRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    lat: float
    lon: float
