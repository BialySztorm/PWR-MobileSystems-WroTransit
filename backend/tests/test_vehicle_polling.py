from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.orm import Session

from ingest.sources import VehicleReading
from ingest.vehicle_polling import insert_vehicle_position, upsert_vehicle_state


def _reading(vehicle_id: str = "A-1", lat: float = 51.11, lon: float = 17.03) -> VehicleReading:
    return VehicleReading(
        vehicle_id=vehicle_id,
        line="4",
        vehicle_type="tram",
        lat=lat,
        lon=lon,
        recorded_at=datetime.now(timezone.utc),
    )


def test_insert_vehicle_position_appends_row(db_session: Session) -> None:
    insert_vehicle_position(db_session, _reading())
    db_session.commit()

    rows = db_session.execute(
        text("SELECT vehicle_id, line, vehicle_type FROM vehicle_positions")
    ).all()
    assert len(rows) == 1
    assert rows[0].vehicle_id == "A-1"
    assert rows[0].line == "4"
    assert rows[0].vehicle_type == "tram"


def test_upsert_vehicle_state_replaces_existing_row(db_session: Session) -> None:
    upsert_vehicle_state(db_session, _reading(lat=51.11, lon=17.03))
    db_session.commit()

    upsert_vehicle_state(db_session, _reading(lat=51.20, lon=17.10))
    db_session.commit()

    rows = db_session.execute(
        text("SELECT ST_Y(geom) AS lat, ST_X(geom) AS lon, vehicle_type FROM vehicle_state")
    ).all()
    assert len(rows) == 1
    assert rows[0].lat == 51.20
    assert rows[0].lon == 17.10
    assert rows[0].vehicle_type == "tram"
