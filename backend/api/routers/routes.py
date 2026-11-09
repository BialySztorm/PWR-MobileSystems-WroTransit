from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.schemas.route import RouteRead, RouteShapeRead

router = APIRouter(prefix="/routes", tags=["routes"])


@router.get("", response_model=list[RouteRead])
def list_routes(
    q: str | None = Query(default=None), db: Session = Depends(get_db)
) -> list[dict]:
    stmt = text(
        "SELECT route_id, short_name, long_name, type FROM routes "
        "WHERE (CAST(:q AS text) IS NULL OR short_name ILIKE '%' || :q || '%') "
        "ORDER BY short_name LIMIT 100"
    )
    return [dict(row._mapping) for row in db.execute(stmt, {"q": q})]


@router.get("/{route_id}", response_model=RouteRead)
def get_route(route_id: str, db: Session = Depends(get_db)) -> dict:
    stmt = text("SELECT route_id, short_name, long_name, type FROM routes WHERE route_id = :id")
    row = db.execute(stmt, {"id": route_id}).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Route not found")
    return dict(row._mapping)


@router.get("/{route_id}/route", response_model=RouteShapeRead)
def get_route_shape(
    route_id: str, direction: int | None = Query(default=None), db: Session = Depends(get_db)
) -> dict:
    """Ordered stops of the trip with the most stops for this route (a representative variant)."""
    trip_stmt = text(
        """
        SELECT t.trip_id, t.direction_id
        FROM trips t
        JOIN stop_times st ON st.trip_id = t.trip_id
        WHERE t.route_id = :route_id
          AND (CAST(:direction AS integer) IS NULL OR t.direction_id = CAST(:direction AS integer))
        GROUP BY t.trip_id, t.direction_id
        ORDER BY COUNT(*) DESC
        LIMIT 1
        """
    )
    trip_row = db.execute(trip_stmt, {"route_id": route_id, "direction": direction}).first()
    if trip_row is None:
        raise HTTPException(status_code=404, detail="No trips found for this route")

    stops_stmt = text(
        """
        SELECT st.stop_sequence AS sequence, s.stop_id, s.stop_code, s.name,
               ST_Y(s.geom) AS lat, ST_X(s.geom) AS lon
        FROM stop_times st
        JOIN stops s ON s.stop_id = st.stop_id
        WHERE st.trip_id = :trip_id
        ORDER BY st.stop_sequence
        """
    )
    stop_rows = db.execute(stops_stmt, {"trip_id": trip_row.trip_id}).all()

    return {
        "route_id": route_id,
        "direction_id": trip_row.direction_id,
        "stops": [
            {
                "sequence": r.sequence,
                "stop": {
                    "stop_id": r.stop_id,
                    "stop_code": r.stop_code,
                    "name": r.name,
                    "lat": r.lat,
                    "lon": r.lon,
                },
            }
            for r in stop_rows
        ],
    }
