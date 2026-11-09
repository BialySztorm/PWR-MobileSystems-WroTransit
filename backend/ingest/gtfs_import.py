"""Import a local GTFS static feed (stops/routes/trips/stop_times/shapes/calendar*) into the
schedule tables. Re-run after downloading a fresh archive - the schedule tables are rebuilt
from scratch on every import.

Run: python -m ingest.gtfs_import [path/to/feed.zip]
"""
import csv
import io
import sys
import zipfile
from itertools import groupby
from pathlib import Path

from shapely.geometry import LineString
from sqlalchemy import insert, text

from api.db.session import engine
from api.models import Calendar, CalendarDate, Route, Shape, Stop, Trip

DEFAULT_GTFS_PATH = Path(__file__).resolve().parent.parent / "data" / "wroclaw.gtfs.zip"

SCHEDULE_TABLES_TRUNCATE_SQL = text(
    "TRUNCATE TABLE stop_times, trips, calendar_dates, calendar, shapes, routes, stops "
    "RESTART IDENTITY CASCADE"
)


def _read_rows(archive: zipfile.ZipFile, filename: str) -> list[dict]:
    with archive.open(filename) as raw:
        text_stream = io.TextIOWrapper(raw, encoding="utf-8-sig", newline="")
        return list(csv.DictReader(text_stream))


def _time_to_seconds(value: str) -> int:
    hours, minutes, seconds = (int(part) for part in value.split(":"))
    return hours * 3600 + minutes * 60 + seconds


def _import_stops(archive: zipfile.ZipFile, conn) -> int:
    rows = _read_rows(archive, "stops.txt")
    conn.execute(
        insert(Stop),
        [
            {
                "stop_id": r["stop_id"],
                "stop_code": r.get("stop_code") or None,
                "name": r["stop_name"],
                "geom": f"SRID=4326;POINT({r['stop_lon']} {r['stop_lat']})",
            }
            for r in rows
        ],
    )
    return len(rows)


def _import_routes(archive: zipfile.ZipFile, conn) -> int:
    rows = _read_rows(archive, "routes.txt")
    conn.execute(
        insert(Route),
        [
            {
                "route_id": r["route_id"],
                "short_name": r["route_short_name"],
                "long_name": r.get("route_long_name") or None,
                "type": int(r["route_type"]),
            }
            for r in rows
        ],
    )
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
        conn.execute(SCHEDULE_TABLES_TRUNCATE_SQL)

        stops = _import_stops(archive, conn)
        print(f"stops: {stops}")
        routes = _import_routes(archive, conn)
        print(f"routes: {routes}")
        shapes = _import_shapes(archive, conn)
        print(f"shapes: {shapes}")
        calendar = _import_calendar(archive, conn)
        print(f"calendar: {calendar}")
        calendar_dates = _import_calendar_dates(archive, conn)
        print(f"calendar_dates: {calendar_dates}")
        trips = _import_trips(archive, conn)
        print(f"trips: {trips}")

        raw_conn = conn.connection.dbapi_connection
        stop_times = _import_stop_times(archive, raw_conn)
        print(f"stop_times: {stop_times}")


if __name__ == "__main__":
    gtfs_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_GTFS_PATH
    run_gtfs_import(gtfs_path)
