"""Import a local GTFS static feed (stops/routes/trips/stop_times/shapes/calendar*) into the
schedule tables. Re-run after downloading a fresh archive. trips/stop_times/shapes/calendar*
are fully rebuilt every import; stops/routes are upserted in place (not deleted), since
vehicle_positions/vehicle_state/favourite_stops/favourite_lines reference them and must
survive a re-import unaffected.

Run: python -m ingest.gtfs_import [path/to/feed.zip]
"""
import csv
import io
import logging
import sys
import zipfile
from itertools import groupby
from pathlib import Path

from shapely.geometry import LineString
from sqlalchemy import insert, text
from sqlalchemy.dialects.postgresql import insert as pg_insert

from api.db.session import engine
from api.models import Calendar, CalendarDate, Route, Shape, Stop, Trip
from ingest.logging_config import configure_logging

logger = logging.getLogger(__name__)

DEFAULT_GTFS_PATH = Path(__file__).resolve().parent.parent / "data" / "wroclaw.gtfs.zip"

# stops/routes are upserted (never deleted) because vehicle_positions, vehicle_state and
# favourite_stops/favourite_lines reference them by stop_id/route_id - deleting and
# re-inserting those rows would either violate their FK constraints or (with CASCADE)
# silently wipe live vehicle data and user favourites on every re-import. The remaining
# schedule tables (trips, stop_times, shapes, calendar*) are fully rebuilt every import,
# since nothing outside the schedule depends on their specific rows - except trips, which
# vehicle_positions/vehicle_state also reference, so those FKs are cleared first and the
# table is cleared with DELETE (which respects that) rather than TRUNCATE (which, for a
# table with incoming FKs, refuses unless every referencing table is truncated too - see
# https://www.postgresql.org/docs/current/sql-truncate.html).
_RESET_SCHEDULE_TABLES_SQL = [
    text("TRUNCATE TABLE stop_times RESTART IDENTITY"),
    text("UPDATE vehicle_positions SET trip_id = NULL"),
    text("UPDATE vehicle_state SET trip_id = NULL"),
    text("DELETE FROM calendar_dates"),
    text("DELETE FROM trips"),
    text("DELETE FROM calendar"),
    text("DELETE FROM shapes"),
]


def _read_rows(archive: zipfile.ZipFile, filename: str) -> list[dict]:
    with archive.open(filename) as raw:
        text_stream = io.TextIOWrapper(raw, encoding="utf-8-sig", newline="")
        return list(csv.DictReader(text_stream))


def _time_to_seconds(value: str) -> int:
    hours, minutes, seconds = (int(part) for part in value.split(":"))
    return hours * 3600 + minutes * 60 + seconds


def _import_stops(archive: zipfile.ZipFile, conn) -> int:
    """Upserted, never deleted - vehicle_positions/vehicle_state/favourite_stops
    reference stops by stop_id and must survive a re-import unaffected."""
    rows = _read_rows(archive, "stops.txt")
    stmt = pg_insert(Stop).values(
        [
            {
                "stop_id": r["stop_id"],
                "stop_code": r.get("stop_code") or None,
                "name": r["stop_name"],
                "geom": f"SRID=4326;POINT({r['stop_lon']} {r['stop_lat']})",
            }
            for r in rows
        ]
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=[Stop.stop_id],
        set_={
            "stop_code": stmt.excluded.stop_code,
            "name": stmt.excluded.name,
            "geom": stmt.excluded.geom,
        },
    )
    conn.execute(stmt)
    return len(rows)


def _import_routes(archive: zipfile.ZipFile, conn) -> int:
    """Upserted, never deleted - vehicle_state/favourite_lines reference routes by
    route_id and must survive a re-import unaffected."""
    rows = _read_rows(archive, "routes.txt")
    stmt = pg_insert(Route).values(
        [
            {
                "route_id": r["route_id"],
                "short_name": r["route_short_name"],
                "long_name": r.get("route_long_name") or None,
                "type": int(r["route_type"]),
            }
            for r in rows
        ]
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=[Route.route_id],
        set_={
            "short_name": stmt.excluded.short_name,
            "long_name": stmt.excluded.long_name,
            "type": stmt.excluded.type,
        },
    )
    conn.execute(stmt)
    return len(rows)


def _import_calendar(archive: zipfile.ZipFile, conn) -> int:
    rows = _read_rows(archive, "calendar.txt")
    conn.execute(
        insert(Calendar),
        [
            {
                "service_id": r["service_id"],
                "monday": r["monday"] == "1",
                "tuesday": r["tuesday"] == "1",
                "wednesday": r["wednesday"] == "1",
                "thursday": r["thursday"] == "1",
                "friday": r["friday"] == "1",
                "saturday": r["saturday"] == "1",
                "sunday": r["sunday"] == "1",
                "start_date": r["start_date"],
                "end_date": r["end_date"],
            }
            for r in rows
        ],
    )
    return len(rows)


def _import_calendar_dates(archive: zipfile.ZipFile, conn) -> int:
    rows = _read_rows(archive, "calendar_dates.txt")
    if not rows:
        return 0
    conn.execute(
        insert(CalendarDate),
        [
            {
                "service_id": r["service_id"],
                "date": r["date"],
                "exception_type": int(r["exception_type"]),
            }
            for r in rows
        ],
    )
    return len(rows)


def _import_shapes(archive: zipfile.ZipFile, conn) -> int:
    rows = _read_rows(archive, "shapes.txt")
    rows.sort(key=lambda r: (r["shape_id"], int(r["shape_pt_sequence"])))

    shapes = []
    for shape_id, points in groupby(rows, key=lambda r: r["shape_id"]):
        coords = [(float(p["shape_pt_lon"]), float(p["shape_pt_lat"])) for p in points]
        shapes.append(
            {"shape_id": shape_id, "geom": f"SRID=4326;{LineString(coords).wkt}"}
        )

    conn.execute(insert(Shape), shapes)
    return len(shapes)


def _import_trips(archive: zipfile.ZipFile, conn) -> int:
    rows = _read_rows(archive, "trips.txt")
    conn.execute(
        insert(Trip),
        [
            {
                "trip_id": r["trip_id"],
                "route_id": r["route_id"],
                "service_id": r["service_id"],
                "direction_id": int(r["direction_id"]) if r.get("direction_id") else None,
                "shape_id": r.get("shape_id") or None,
                "headsign": r.get("trip_headsign") or None,
            }
            for r in rows
        ],
    )
    return len(rows)


def _import_stop_times(archive: zipfile.ZipFile, raw_conn) -> int:
    """Bulk-loaded via COPY - this table has 1M+ rows for a city-wide feed."""
    count = 0
    with archive.open("stop_times.txt") as raw, raw_conn.cursor() as cursor:
        text_stream = io.TextIOWrapper(raw, encoding="utf-8-sig", newline="")
        reader = csv.DictReader(text_stream)
        with cursor.copy(
            "COPY stop_times (trip_id, stop_sequence, stop_id, arrival_time_s, departure_time_s) "
            "FROM STDIN"
        ) as copy:
            for r in reader:
                copy.write_row(
                    (
                        r["trip_id"],
                        int(r["stop_sequence"]),
                        r["stop_id"],
                        _time_to_seconds(r["arrival_time"]),
                        _time_to_seconds(r["departure_time"]),
                    )
                )
                count += 1
    return count


def run_gtfs_import(path: Path = DEFAULT_GTFS_PATH) -> None:
    if not path.exists():
        raise FileNotFoundError(
            f"GTFS archive not found at {path}. Download the current feed and place it there "
            "(see docs/Specifications.md section 2 for the source)."
        )

    with zipfile.ZipFile(path) as archive, engine.begin() as conn:
        for stmt in _RESET_SCHEDULE_TABLES_SQL:
            conn.execute(stmt)

        stops = _import_stops(archive, conn)
        logger.info("stops: %d", stops)
        routes = _import_routes(archive, conn)
        logger.info("routes: %d", routes)
        shapes = _import_shapes(archive, conn)
        logger.info("shapes: %d", shapes)
        calendar = _import_calendar(archive, conn)
        logger.info("calendar: %d", calendar)
        calendar_dates = _import_calendar_dates(archive, conn)
        logger.info("calendar_dates: %d", calendar_dates)
        trips = _import_trips(archive, conn)
        logger.info("trips: %d", trips)

        raw_conn = conn.connection.dbapi_connection
        stop_times = _import_stop_times(archive, raw_conn)
        logger.info("stop_times: %d", stop_times)


if __name__ == "__main__":
    configure_logging()
    gtfs_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_GTFS_PATH
    run_gtfs_import(gtfs_path)
