"""Polls live vehicle positions and writes them to vehicle_positions / vehicle_state.

Run: python -m ingest.vehicle_polling
Source is chosen via the SOURCE env var ("mpk", the default, or "replay").
"""
import logging
import time

from sqlalchemy import insert, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from api.db.session import SessionLocal, engine
from api.models.route import Route
from api.models.vehicle import VehiclePosition, VehicleState
from ingest.config import Config, load_config
from ingest.logging_config import configure_logging
from ingest.sources import ReplaySource, VehicleReading, VehiclePositionSource, build_mpk_source, build_replay_source

logger = logging.getLogger(__name__)


def _fetch_lines() -> tuple[list[str], list[str]]:
    """Returns (tram_lines, bus_lines) from the imported GTFS schedule."""
    with engine.connect() as conn:
        rows = conn.execute(
            select(Route.short_name, Route.type).distinct()
        ).all()
    tram_lines = sorted({name for name, type_ in rows if type_ == 0})
    bus_lines = sorted({name for name, type_ in rows if type_ == 3})
    return tram_lines, bus_lines


def build_source(config: Config) -> VehiclePositionSource:
    if config.source == "replay":
        return build_replay_source(config)
    tram_lines, bus_lines = _fetch_lines()
    return build_mpk_source(config, tram_lines, bus_lines)


def insert_vehicle_position(session: Session, reading: VehicleReading) -> None:
    session.execute(
        insert(VehiclePosition).values(
            vehicle_id=reading.vehicle_id,
            line=reading.line,
            geom=f"SRID=4326;POINT({reading.lon} {reading.lat})",
            recorded_at=reading.recorded_at,
        )
    )


def upsert_vehicle_state(session: Session, reading: VehicleReading) -> None:
    stmt = pg_insert(VehicleState).values(
        vehicle_id=reading.vehicle_id,
        line=reading.line,
        geom=f"SRID=4326;POINT({reading.lon} {reading.lat})",
        recorded_at=reading.recorded_at,
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=[VehicleState.vehicle_id],
        set_={
            "line": stmt.excluded.line,
            "geom": stmt.excluded.geom,
            "recorded_at": stmt.excluded.recorded_at,
        },
    )
    session.execute(stmt)


def poll_vehicle_positions(source: VehiclePositionSource, session_factory=SessionLocal) -> int:
    """One fetch + write cycle. Returns the number of readings written."""
    readings = source.fetch()
    if not readings:
        return 0

    session = session_factory()
    try:
        for reading in readings:
            insert_vehicle_position(session, reading)
            upsert_vehicle_state(session, reading)
        session.commit()
    finally:
        session.close()
    return len(readings)


def run_polling_loop() -> None:
    configure_logging()
    config = load_config()
    source = build_source(config)
    logger.info("Starting vehicle polling loop (source=%s)", config.source)

    while True:
        try:
            count = poll_vehicle_positions(source)
            logger.info("Polled %d vehicle position(s)", count)
        except Exception:
            logger.exception("Vehicle polling cycle failed, continuing")

        if not isinstance(source, ReplaySource):
            time.sleep(config.poll_interval_s)


if __name__ == "__main__":
    run_polling_loop()
