from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.schemas.vehicle import VehicleStateRead

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("", response_model=list[VehicleStateRead])
def list_vehicles(
    line: str | None = Query(default=None),
    type: str | None = Query(default=None, description="'tram' or 'bus'"),
    db: Session = Depends(get_db),
) -> list[dict]:
    """Current vehicle positions."""
    stmt = text(
        "SELECT vehicle_id, line, vehicle_type, ST_Y(geom) AS lat, ST_X(geom) AS lon, "
        "recorded_at, delay_s "
        "FROM vehicle_state "
        "WHERE (CAST(:line AS text) IS NULL OR line = :line) "
        "AND (CAST(:type AS text) IS NULL OR vehicle_type = :type)"
    )
    return [dict(row._mapping) for row in db.execute(stmt, {"line": line, "type": type})]
