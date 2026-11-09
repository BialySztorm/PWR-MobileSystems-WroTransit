from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.models.line import Line
from api.models.vehicle import Vehicle


def test_list_vehicles_filters_by_line(client: TestClient, db_session: Session) -> None:
    line_a = Line(code="A", name="Linia A", color=None)
    line_b = Line(code="144", name="Linia 144", color=None)
    db_session.add_all([line_a, line_b])
    db_session.flush()

    now = datetime.now(UTC)
    db_session.add_all(
        [
            Vehicle(line_id=line_a.id, label="A-101", lat=51.1, lon=17.0, updated_at=now),
            Vehicle(line_id=line_b.id, label="144-07", lat=51.2, lon=17.1, updated_at=now),
        ]
    )
    db_session.commit()

    response = client.get(f"/vehicles?line_id={line_a.id}")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["label"] == "A-101"
