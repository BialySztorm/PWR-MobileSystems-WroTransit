from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.models.line import Line
from api.models.route import Route
from api.schemas.line import LineRead
from api.schemas.route import RouteRead

router = APIRouter(prefix="/lines", tags=["lines"])


@router.get("", response_model=list[LineRead])
def list_lines(db: Session = Depends(get_db)) -> list[Line]:
    return list(db.scalars(select(Line).order_by(Line.code)))


@router.get("/{line_id}", response_model=LineRead)
def get_line(line_id: int, db: Session = Depends(get_db)) -> Line:
    line = db.get(Line, line_id)
    if line is None:
        raise HTTPException(status_code=404, detail="Line not found")
    return line


@router.get("/{line_id}/route", response_model=RouteRead)
def get_line_route(line_id: int, db: Session = Depends(get_db)) -> Route:
    route = db.scalars(select(Route).where(Route.line_id == line_id)).first()
    if route is None:
        raise HTTPException(status_code=404, detail="Route not found for this line")
    return route
