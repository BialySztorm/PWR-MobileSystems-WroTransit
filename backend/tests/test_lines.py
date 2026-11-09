from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.models.line import Line
from api.models.route import Route, RouteStop
from api.models.stop import Stop


def test_list_lines_returns_seeded_line(client: TestClient, db_session: Session) -> None:
    db_session.add(Line(code="A", name="Linia A", color="#D32F2F"))
    db_session.commit()

    response = client.get("/lines")

    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "code": "A", "name": "Linia A", "color": "#D32F2F"}
    ]


def test_get_line_route_returns_ordered_stops(client: TestClient, db_session: Session) -> None:
    line = Line(code="A", name="Linia A", color=None)
    stop_a = Stop(name="Rynek", lat=51.11, lon=17.03)
    stop_b = Stop(name="Renoma", lat=51.1075, lon=17.0281)
    db_session.add_all([line, stop_a, stop_b])
    db_session.flush()

    route = Route(line_id=line.id)
    db_session.add(route)
    db_session.flush()
    db_session.add_all(
        [
            RouteStop(route_id=route.id, stop_id=stop_b.id, sequence=1),
            RouteStop(route_id=route.id, stop_id=stop_a.id, sequence=0),
        ]
    )
    db_session.commit()

    response = client.get(f"/lines/{line.id}/route")

    assert response.status_code == 200
    body = response.json()
    assert [s["stop"]["name"] for s in body["stops"]] == ["Rynek", "Renoma"]


def test_get_line_route_not_found_returns_404(client: TestClient) -> None:
    response = client.get("/lines/999/route")

    assert response.status_code == 404
