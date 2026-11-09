from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.models.route import Route
from api.schemas.route import RouteRead

router = APIRouter(prefix="/routes", tags=["routes"])


@router.get("", response_model=list[RouteRead])
def list_routes(db: Session = Depends(get_db)) -> list[Route]:
    return list(db.scalars(select(Route)))


@router.get("/{route_id}", response_model=RouteRead)
def get_route(route_id: int, db: Session = Depends(get_db)) -> Route:
    route = db.get(Route, route_id)
    if route is None:
        raise HTTPException(status_code=404, detail="Route not found")
    return route
