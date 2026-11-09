from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.schemas.vehicle import VehicleStateRead

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("", response_model=list[VehicleStateRead])
def list_vehicles(
    line: str | None = Query(default=None), db: Session = Depends(get_db)
) -> list[dict]:
    """Current vehicle positions. Empty until Sprint 3's polling job populates vehicle_state."""
    stmt = text(
        "SELECT vehicle_id, line, ST_Y(geom) AS lat, ST_X(geom) AS lon, recorded_at, delay_s "
        "FROM vehicle_state WHERE (CAST(:line AS text) IS NULL OR line = :line)"
    )
    return [dict(row._mapping) for row in db.execute(stmt, {"line": line})]
