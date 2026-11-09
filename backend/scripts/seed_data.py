"""Populate the database with a small set of Wroclaw stops, lines, a route and vehicles.

Run after migrations: python -m scripts.seed_data
"""
from datetime import UTC, datetime

from api.db.session import SessionLocal
from api.models.line import Line
from api.models.route import Route, RouteStop
from api.models.stop import Stop
from api.models.vehicle import Vehicle

STOPS = [
    ("Rynek", 51.1101, 17.0326),
    ("Galeria Dominikanska", 51.1095, 17.0394),
    ("Renoma", 51.1075, 17.0281),
    ("Plac Grunwaldzki", 51.1125, 17.0601),
    ("Politechnika Wroclawska", 51.1054, 17.0632),
]

LINES = [
    ("A", "Linia A", "#D32F2F"),
    ("144", "Linia 144", "#1976D2"),
]


def run_seed() -> None:
    db = SessionLocal()
    try:
        stops = [Stop(name=name, lat=lat, lon=lon) for name, lat, lon in STOPS]
        db.add_all(stops)
        db.flush()

        lines = [Line(code=code, name=name, color=color) for code, name, color in LINES]
        db.add_all(lines)
        db.flush()

        route = Route(line_id=lines[0].id)
        db.add(route)
        db.flush()

        for sequence, stop in enumerate(stops):
            db.add(RouteStop(route_id=route.id, stop_id=stop.id, sequence=sequence))

        now = datetime.now(UTC)
        db.add_all(
            [
                Vehicle(line_id=lines[0].id, label="A-101", lat=stops[0].lat, lon=stops[0].lon, updated_at=now),
                Vehicle(line_id=lines[1].id, label="144-07", lat=stops[3].lat, lon=stops[3].lon, updated_at=now),
            ]
        )

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
