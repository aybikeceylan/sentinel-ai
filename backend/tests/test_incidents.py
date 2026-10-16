
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_incident():
    response = client.post(
        "/api/v1/incidents",
        json={
            "title": "Authentication service returning 401",
            "description": "Users receive 401 errors after token refresh",
            "severity": "high",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Authentication service returning 401"
    assert data["severity"] == "high"
    assert data["status"] == "open"
    assert "id" in data


def test_invalid_incident():
    response = client.post(
        "/api/v1/incidents",
        json={
            "title": "Bug",
            "description": "Short",
            "severity": "urgent",
        },
    )

    assert response.status_code == 422

def test_get_incident_count():
    response = client.get("/api/v1/incidents/count")
    assert response.status_code == 200
