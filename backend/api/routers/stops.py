from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.schemas.departure import DepartureRead
from api.schemas.stop import StopRead

router = APIRouter(prefix="/stops", tags=["stops"])

WEEKDAY_COLUMNS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


@router.get("", response_model=list[StopRead])
def list_stops(
    q: str | None = Query(default=None),
    bbox: str | None = Query(
        default=None, description="minLon,minLat,maxLon,maxLat (map viewport)"
    ),
    db: Session = Depends(get_db),
) -> list[dict]:
    conditions = ["(CAST(:q AS text) IS NULL OR s.name ILIKE '%' || :q || '%')"]
    params: dict = {"q": q}
    limit = 100

    if bbox:
        min_lon, min_lat, max_lon, max_lat = (float(v) for v in bbox.split(","))
        conditions.append(
            "ST_Intersects(s.geom, ST_MakeEnvelope(:min_lon, :min_lat, :max_lon, :max_lat, 4326))"
        )
        params.update(min_lon=min_lon, min_lat=min_lat, max_lon=max_lon, max_lat=max_lat)
        limit = 500

    if bbox:
        # Only worth the extra join when rendering the map viewport - plain search results
        # don't need the served modes.
        stmt = text(
            """
            SELECT s.stop_id, s.stop_code, s.name, ST_Y(s.geom) AS lat, ST_X(s.geom) AS lon,
                   COALESCE(
                       array_agg(DISTINCT r.type) FILTER (WHERE r.type IS NOT NULL), '{}'
                   ) AS modes
            FROM stops s
            LEFT JOIN stop_times st ON st.stop_id = s.stop_id
            LEFT JOIN trips t ON t.trip_id = st.trip_id
            LEFT JOIN routes r ON r.route_id = t.route_id
            """
            f"WHERE {' AND '.join(conditions)} "
            "GROUP BY s.stop_id, s.stop_code, s.name, s.geom "
            f"ORDER BY s.name LIMIT {limit}"
        )
    else:
        stmt = text(
            "SELECT s.stop_id, s.stop_code, s.name, ST_Y(s.geom) AS lat, ST_X(s.geom) AS lon, "
            "'{}'::int[] AS modes "
            f"FROM stops s WHERE {' AND '.join(conditions)} "
            f"ORDER BY s.name LIMIT {limit}"
        )
    return [dict(row._mapping) for row in db.execute(stmt, params)]


@router.get("/{stop_id}", response_model=StopRead)
def get_stop(stop_id: str, db: Session = Depends(get_db)) -> dict:
    stmt = text(
        "SELECT stop_id, stop_code, name, ST_Y(geom) AS lat, ST_X(geom) AS lon "
        "FROM stops WHERE stop_id = :stop_id"
    )
    row = db.execute(stmt, {"stop_id": stop_id}).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Stop not found")
    return dict(row._mapping)


@router.get("/{stop_id}/departures", response_model=list[DepartureRead])
def get_stop_departures(
    stop_id: str, limit: int = Query(default=10, le=50), db: Session = Depends(get_db)
) -> list[dict]:
    now = datetime.now()
    weekday_column = WEEKDAY_COLUMNS[now.weekday()]
    now_s = now.hour * 3600 + now.minute * 60 + now.second

    stmt = text(
        f"""
        SELECT r.short_name AS route_short_name, r.type AS route_type,
               t.headsign, t.direction_id, st.departure_time_s
        FROM stop_times st
        JOIN trips t ON t.trip_id = st.trip_id
        JOIN routes r ON r.route_id = t.route_id
        JOIN calendar c ON c.service_id = t.service_id
        WHERE st.stop_id = :stop_id
          AND st.departure_time_s >= :now_s
          AND c.{weekday_column} IS TRUE
          AND CURRENT_DATE BETWEEN c.start_date AND c.end_date
        ORDER BY st.departure_time_s
        LIMIT :limit
        """
    )
    # Note: calendar_dates.txt exceptions (added/removed single-day services) are not
    # applied yet - this feed's calendar_dates.txt is empty, so it's a no-op for now.
    return [
        dict(row._mapping)
        for row in db.execute(stmt, {"stop_id": stop_id, "now_s": now_s, "limit": limit})
    ]
