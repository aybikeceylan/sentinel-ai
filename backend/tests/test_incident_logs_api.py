
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_incident_logs():
    create_response = client.post(
        "/api/v1/incidents",
        json={
            "title": "Authentication service failure",
            "description": "Users receive 401 errors after token refresh",
            "severity": "high",
        },
    )

    assert create_response.status_code == 201

    incident_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/incidents/{incident_id}/logs"
    )

    assert response.status_code == 200

    logs = response.json()

    assert len(logs) == 4
    assert all(
        log["incident_id"] == incident_id
        for log in logs
    )

    # Repeated requests should not create duplicate logs
    second_response = client.get(
        f"/api/v1/incidents/{incident_id}/logs"
    )

    assert second_response.status_code == 200
    assert second_response.json() == logs
