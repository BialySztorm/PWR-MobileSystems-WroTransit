from fastapi.testclient import TestClient


def test_list_shapes_with_malformed_bbox_returns_422(client: TestClient) -> None:
    response = client.get("/shapes?bbox=1,2,3")
    assert response.status_code == 422

    response = client.get("/shapes?bbox=abc,def,ghi,jkl")
    assert response.status_code == 422
