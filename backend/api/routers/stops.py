from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.schemas.departure import DepartureRead
from api.schemas.stop import StopNearbyRead, StopRead

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


@router.get("/nearby", response_model=list[StopNearbyRead])
def list_stops_nearby(
    lat: float = Query(...),
    lon: float = Query(...),
    radius: float = Query(default=500, le=5000, description="Search radius in meters"),
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db),
) -> list[dict]:
    stmt = text(
        """
        SELECT stop_id, stop_code, name, ST_Y(geom) AS lat, ST_X(geom) AS lon,
               '{}'::int[] AS modes,
               ST_Distance(geom::geography, ST_MakePoint(:lon, :lat)::geography) AS distance_m
        FROM stops
        WHERE ST_DWithin(geom::geography, ST_MakePoint(:lon, :lat)::geography, :radius)
        ORDER BY distance_m
        LIMIT :limit
        """
    )
    return [
        dict(row._mapping)
        for row in db.execute(stmt, {"lat": lat, "lon": lon, "radius": radius, "limit": limit})
    ]


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
    today_column = WEEKDAY_COLUMNS[now.weekday()]
    yesterday_column = WEEKDAY_COLUMNS[(now.weekday() - 1) % 7]
    now_s = now.hour * 3600 + now.minute * 60 + now.second

    # GTFS allows departure_time_s > 86400 for a trip that keeps running past midnight
    # (night lines): that time is still relative to *yesterday's* service day. So "today's
    # upcoming departures" is two sets unioned together: today's calendar with a plain
    # time filter, and yesterday's calendar with the time shifted by +86400.
    stmt = text(
        f"""
        SELECT route_short_name, route_type, headsign, direction_id, departure_time_s
        FROM (
            SELECT r.short_name AS route_short_name, r.type AS route_type,
                   t.headsign, t.direction_id, st.departure_time_s,
                   st.departure_time_s - :now_s AS seconds_until
            FROM stop_times st
            JOIN trips t ON t.trip_id = st.trip_id
            JOIN routes r ON r.route_id = t.route_id
            JOIN calendar c ON c.service_id = t.service_id
            WHERE st.stop_id = :stop_id
              AND st.departure_time_s >= :now_s
              AND c.{today_column} IS TRUE
              AND CURRENT_DATE BETWEEN c.start_date AND c.end_date

            UNION ALL

            SELECT r.short_name, r.type, t.headsign, t.direction_id, st.departure_time_s,
                   st.departure_time_s - 86400 - :now_s AS seconds_until
            FROM stop_times st
            JOIN trips t ON t.trip_id = st.trip_id
            JOIN routes r ON r.route_id = t.route_id
            JOIN calendar c ON c.service_id = t.service_id
            WHERE st.stop_id = :stop_id
              AND st.departure_time_s >= :now_s + 86400
              AND c.{yesterday_column} IS TRUE
              AND CURRENT_DATE - 1 BETWEEN c.start_date AND c.end_date
        ) AS candidates
        ORDER BY seconds_until
        LIMIT :limit
        """
    )
    # Note: calendar_dates.txt exceptions (added/removed single-day services) are not
    # applied yet - this feed's calendar_dates.txt is empty, so it's a no-op for now.
    return [
        dict(row._mapping)
        for row in db.execute(stmt, {"stop_id": stop_id, "now_s": now_s, "limit": limit})
    ]
