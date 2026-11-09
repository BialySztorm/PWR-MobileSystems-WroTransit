from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.models.vehicle import Vehicle
from api.schemas.vehicle import VehicleRead

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("", response_model=list[VehicleRead])
def list_vehicles(
    line_id: int | None = Query(default=None), db: Session = Depends(get_db)
) -> list[Vehicle]:
    stmt = select(Vehicle)
    if line_id is not None:
        stmt = stmt.where(Vehicle.line_id == line_id)
    return list(db.scalars(stmt))


@router.get("/{vehicle_id}", response_model=VehicleRead)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)) -> Vehicle:
    vehicle = db.get(Vehicle, vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle
