from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.models.line import Line
from api.models.route import Route, RouteStop
from api.models.stop import Stop
from api.schemas.line import LineRead
from api.schemas.stop import StopRead

router = APIRouter(prefix="/stops", tags=["stops"])


@router.get("", response_model=list[StopRead])
def list_stops(db: Session = Depends(get_db)) -> list[Stop]:
    return list(db.scalars(select(Stop).order_by(Stop.name)))


@router.get("/{stop_id}", response_model=StopRead)
def get_stop(stop_id: int, db: Session = Depends(get_db)) -> Stop:
    stop = db.get(Stop, stop_id)
    if stop is None:
        raise HTTPException(status_code=404, detail="Stop not found")
    return stop


@router.get("/{stop_id}/lines", response_model=list[LineRead])
def get_stop_lines(stop_id: int, db: Session = Depends(get_db)) -> list[Line]:
    stop = db.get(Stop, stop_id)
    if stop is None:
        raise HTTPException(status_code=404, detail="Stop not found")

    stmt = (
        select(Line)
        .join(Route, Route.line_id == Line.id)
        .join(RouteStop, RouteStop.route_id == Route.id)
        .where(RouteStop.stop_id == stop_id)
        .distinct()
    )
    return list(db.scalars(stmt))
