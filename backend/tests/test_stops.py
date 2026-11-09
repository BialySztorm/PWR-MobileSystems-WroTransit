from fastapi.testclient import TestClient
from geoalchemy2.elements import WKTElement
from sqlalchemy.orm import Session

from api.models.stop import Stop


def _make_stop(stop_id: str, name: str, lat: float, lon: float) -> Stop:
    return Stop(
        stop_id=stop_id,
        stop_code=stop_id,
        name=name,
        geom=WKTElement(f"POINT({lon} {lat})", srid=4326),
    )


def test_list_stops_filters_by_query(client: TestClient, db_session: Session) -> None:
    db_session.add_all(
        [
            _make_stop("1", "Rynek", 51.1101, 17.0326),
            _make_stop("2", "Renoma", 51.1075, 17.0281),
        ]
    )
    db_session.commit()

    response = client.get("/stops?q=rynek")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0] == {
        "stop_id": "1",
        "stop_code": "1",
        "name": "Rynek",
        "lat": 51.1101,
        "lon": 17.0326,
        "modes": [],
    }


def test_get_stop_not_found_returns_404(client: TestClient) -> None:
    response = client.get("/stops/999")

    assert response.status_code == 404


def test_list_stops_with_bbox_returns_served_modes(
    client: TestClient, db_session: Session
) -> None:
    from api.models.route import Route
    from api.models.stop_time import StopTime
    from api.models.trip import Trip

    db_session.add_all(
        [
            _make_stop("1", "Rynek", 51.1101, 17.0326),
            Route(route_id="4", short_name="4", long_name=None, type=0),
            Trip(trip_id="t1", route_id="4", service_id="s1", direction_id=0, headsign=None),
        ]
    )
    db_session.flush()
    db_session.add(
        StopTime(trip_id="t1", stop_sequence=0, stop_id="1", arrival_time_s=0, departure_time_s=0)
    )
    db_session.commit()

    response = client.get("/stops?bbox=17.00,51.09,17.06,51.13")

    assert response.status_code == 200
    body = response.json()
    assert body[0]["modes"] == [0]
