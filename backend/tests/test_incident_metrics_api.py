
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_incident_metrics():
    create_response = client.post(
        "/api/v1/incidents",
        json={
            "title": "Authentication service failure",
            "description": "Users receive 401 errors after deployment",
            "severity": "high",
        },
    )

    assert create_response.status_code == 201

    incident_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/incidents/{incident_id}/metrics"
    )

    assert response.status_code == 200

    metrics = response.json()

    assert len(metrics) == 5
    assert all(
        metric["incident_id"] == incident_id
        for metric in metrics
    )

    assert metrics[0]["value"] == 0.02
    assert metrics[-1]["value"] == 0.42

    # Aynı istekte yeni metrikler üretilmemeli
    second_response = client.get(
        f"/api/v1/incidents/{incident_id}/metrics"
    )

    assert second_response.status_code == 200
    assert second_response.json() == metrics


def test_metrics_for_unknown_incident():
    response = client.get(
        "/api/v1/incidents/"
        "00000000-0000-0000-0000-000000000000/metrics"
    )

    assert response.status_code == 404
