from fastapi.testclient import TestClient
from geoalchemy2.elements import WKTElement
from sqlalchemy.orm import Session

from api.models.vehicle import VehicleState


def test_list_vehicles_filters_by_line(client: TestClient, db_session: Session) -> None:
    db_session.add_all(
        [
            VehicleState(
                vehicle_id="A-101",
                line="4",
                geom=WKTElement("POINT(17.03 51.11)", srid=4326),
                recorded_at=None,
                delay_s=None,
            ),
            VehicleState(
                vehicle_id="B-02",
                line="144",
                geom=WKTElement("POINT(17.05 51.12)", srid=4326),
                recorded_at=None,
                delay_s=None,
            ),
        ]
    )
    db_session.commit()

    response = client.get("/vehicles?line=4")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["vehicle_id"] == "A-101"
