
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.incident import IncidentScenario
from app.simulators.scenarios import (
    SAMPLE_INCIDENTS,
    generate_logs,
    generate_metrics,
)


client = TestClient(app)


@pytest.mark.parametrize("scenario", list(IncidentScenario))
def test_every_scenario_generates_ordered_telemetry(scenario):
    incident_id = uuid4()

    logs = generate_logs(scenario, incident_id)
    metrics = generate_metrics(scenario, incident_id)

    assert logs and metrics
    assert all(log.incident_id == incident_id for log in logs)
    assert all(metric.incident_id == incident_id for metric in metrics)

    timestamps = [log.timestamp for log in logs]
    assert timestamps == sorted(timestamps)


@pytest.mark.parametrize("scenario", list(IncidentScenario))
def test_every_scenario_has_a_sample_incident(scenario):
    assert SAMPLE_INCIDENTS[scenario].scenario == scenario


def test_incident_defaults_to_auth_scenario():
    response = client.post(
        "/api/v1/incidents",
        json={
            "title": "Authentication service failure",
            "description": "Users receive 401 errors after deployment",
            "severity": "high",
        },
    )

    assert response.json()["scenario"] == "auth_failure"


def test_logs_endpoint_follows_incident_scenario():
    response = client.post(
        "/api/v1/incidents",
        json={
            "title": "Product catalog is slow",
            "description": "Catalog pages take several seconds to load",
            "severity": "medium",
            "scenario": "cache_outage",
        },
    )
    incident_id = response.json()["id"]

    logs = client.get(f"/api/v1/incidents/{incident_id}/logs").json()
    services = {log["service"] for log in logs}

    assert "redis-cache" in services
    assert "auth-service" not in services


def test_unknown_scenario_is_rejected():
    response = client.post(
        "/api/v1/incidents",
        json={
            "title": "Something broke",
            "description": "Something broke in production",
            "severity": "low",
            "scenario": "alien_invasion",
        },
    )

    assert response.status_code == 422
