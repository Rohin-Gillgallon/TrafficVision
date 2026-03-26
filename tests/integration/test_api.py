from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from src.api.main import app

client = TestClient(app)


@patch(
    "src.api.routes.cameras.get_busiest",
    new_callable=AsyncMock,
    return_value=[
        {
            "camera_id": "test",
            "lat": 0.0,
            "lon": 0.0,
            "total_detections": 0,
            "vehicle_count_30s": 0,
        }
    ],
)
def test_list_cameras_returns_200(mock_get):
    response = client.get("/cameras/")
    assert response.status_code == 200
    assert response.json()[0]["vehicle_count_30s"] == 0


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
