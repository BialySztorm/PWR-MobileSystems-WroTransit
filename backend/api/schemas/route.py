from pydantic import BaseModel, ConfigDict

from api.schemas.stop import StopRead


class RouteStopRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sequence: int
    stop: StopRead


class RouteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    line_id: int
    stops: list[RouteStopRead]
