from fastapi.testclient import TestClient
from geoalchemy2.elements import WKTElement
from sqlalchemy.orm import Session

from api.models.route import Route
from api.models.stop import Stop
from api.models.stop_time import StopTime
from api.models.trip import Trip


def test_list_routes_filters_by_query(client: TestClient, db_session: Session) -> None:
    db_session.add_all(
        [
            Route(route_id="4", short_name="4", long_name=None, type=0),
            Route(route_id="144", short_name="144", long_name=None, type=3),
        ]
    )
    db_session.commit()

    response = client.get("/routes?q=4")

    assert response.status_code == 200
    body = response.json()
    assert {r["route_id"] for r in body} == {"4", "144"}


def test_get_route_not_found_returns_404(client: TestClient) -> None:
    response = client.get("/routes/999")

    assert response.status_code == 404


def test_get_route_shape_returns_ordered_stops(
    client: TestClient, db_session: Session
) -> None:
    stop_a = Stop(
        stop_id="a", stop_code="a", name="Rynek", geom=WKTElement("POINT(17.03 51.11)", srid=4326)
    )
    stop_b = Stop(
        stop_id="b",
        stop_code="b",
        name="Renoma",
        geom=WKTElement("POINT(17.0281 51.1075)", srid=4326),
    )
    db_session.add_all(
        [
            Route(route_id="4", short_name="4", long_name=None, type=0),
            stop_a,
            stop_b,
            Trip(trip_id="t1", route_id="4", service_id="s1", direction_id=0, headsign="A"),
        ]
    )
    db_session.flush()
    db_session.add_all(
        [
            StopTime(trip_id="t1", stop_sequence=1, stop_id="b", arrival_time_s=0, departure_time_s=0),
            StopTime(trip_id="t1", stop_sequence=0, stop_id="a", arrival_time_s=0, departure_time_s=0),
        ]
    )
    db_session.commit()

    response = client.get("/routes/4/route")

    assert response.status_code == 200
    body = response.json()
    assert [s["stop"]["name"] for s in body["stops"]] == ["Rynek", "Renoma"]


def test_get_route_shape_not_found_returns_404(client: TestClient) -> None:
    response = client.get("/routes/999/route")

    assert response.status_code == 404
