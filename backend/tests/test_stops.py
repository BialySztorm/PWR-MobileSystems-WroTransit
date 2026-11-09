from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.models.line import Line
from api.models.route import Route, RouteStop
from api.models.stop import Stop


def test_list_stops_returns_seeded_stop(client: TestClient, db_session: Session) -> None:
    db_session.add(Stop(name="Rynek", lat=51.1101, lon=17.0326))
    db_session.commit()

    response = client.get("/stops")

    assert response.status_code == 200
    assert response.json() == [{"id": 1, "name": "Rynek", "lat": 51.1101, "lon": 17.0326}]


def test_get_stop_not_found_returns_404(client: TestClient) -> None:
    response = client.get("/stops/999")

    assert response.status_code == 404


def test_get_stop_lines_returns_lines_serving_stop(
    client: TestClient, db_session: Session
) -> None:
    stop = Stop(name="Rynek", lat=51.11, lon=17.03)
    line = Line(code="A", name="Linia A", color=None)
    db_session.add_all([stop, line])
    db_session.flush()

    route = Route(line_id=line.id)
    db_session.add(route)
    db_session.flush()
    db_session.add(RouteStop(route_id=route.id, stop_id=stop.id, sequence=0))
    db_session.commit()

    response = client.get(f"/stops/{stop.id}/lines")

    assert response.status_code == 200
    assert [l["code"] for l in response.json()] == ["A"]
