from datetime import date, timedelta

from fastapi.testclient import TestClient
from geoalchemy2.elements import WKTElement
from sqlalchemy.orm import Session

from api.models.calendar import Calendar
from api.models.route import Route
from api.models.stop import Stop
from api.models.stop_time import StopTime
from api.models.trip import Trip

WEEKDAY_COLUMNS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


def test_get_stop_departures_returns_upcoming_trip(
    client: TestClient, db_session: Session
) -> None:
    today = date.today()
    active_weekdays = {col: False for col in WEEKDAY_COLUMNS}
    active_weekdays[WEEKDAY_COLUMNS[today.weekday()]] = True

    stop = Stop(
        stop_id="s", stop_code="s", name="Rynek", geom=WKTElement("POINT(17.03 51.11)", srid=4326)
    )
    db_session.add_all(
        [
            stop,
            Route(route_id="4", short_name="4", long_name=None, type=0),
            Calendar(
                service_id="svc",
                start_date=today - timedelta(days=1),
                end_date=today + timedelta(days=1),
                **active_weekdays,
            ),
            Trip(trip_id="t1", route_id="4", service_id="svc", direction_id=0, headsign="Oporów"),
        ]
    )
    db_session.flush()
    # 90000s is always in the future relative to "now" (max real time-of-day is 86399s).
    db_session.add(
        StopTime(trip_id="t1", stop_sequence=0, stop_id="s", arrival_time_s=90000, departure_time_s=90000)
    )
    db_session.commit()

    response = client.get(f"/stops/{stop.stop_id}/departures")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["route_short_name"] == "4"
    assert body[0]["headsign"] == "Oporów"
    assert body[0]["departure_time_s"] == 90000


def test_get_stop_departures_excludes_inactive_service(
    client: TestClient, db_session: Session
) -> None:
    today = date.today()
    inactive_weekdays = {col: False for col in WEEKDAY_COLUMNS}  # no weekday active

    stop = Stop(
        stop_id="s", stop_code="s", name="Rynek", geom=WKTElement("POINT(17.03 51.11)", srid=4326)
    )
    db_session.add_all(
        [
            stop,
            Route(route_id="4", short_name="4", long_name=None, type=0),
            Calendar(
                service_id="svc",
                start_date=today - timedelta(days=1),
                end_date=today + timedelta(days=1),
                **inactive_weekdays,
            ),
            Trip(trip_id="t1", route_id="4", service_id="svc", direction_id=0, headsign="Oporów"),
        ]
    )
    db_session.flush()
    db_session.add(
        StopTime(trip_id="t1", stop_sequence=0, stop_id="s", arrival_time_s=90000, departure_time_s=90000)
    )
    db_session.commit()

    response = client.get(f"/stops/{stop.stop_id}/departures")

    assert response.status_code == 200
    assert response.json() == []
