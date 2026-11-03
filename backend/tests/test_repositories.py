
from app.db import Database
from app.repositories.incident_repository import IncidentRepository
from app.repositories.log_repository import LogRepository
from app.schemas.incident import (
    Incident,
    IncidentSeverity,
    IncidentStatus,
)
from app.simulators.auth_simulator import generate_auth_failure_logs


def _incident() -> Incident:
    return Incident(
        title="Authentication service failure",
        description="Users receive 401 errors after deployment",
        severity=IncidentSeverity.HIGH,
    )


def test_data_survives_reopening_the_database(tmp_path):
    path = str(tmp_path / "sentinel.db")
    incident = _incident()
    logs = generate_auth_failure_logs(incident.id)

    IncidentRepository(Database(path)).save(incident)
    LogRepository(Database(path)).save_many(incident.id, logs)

    reopened = Database(path)

    assert IncidentRepository(reopened).find_by_id(incident.id) == incident
    assert LogRepository(reopened).find_by_incident_id(incident.id) == logs


def test_save_updates_existing_incident():
    repository = IncidentRepository(Database(":memory:"))
    incident = repository.save(_incident())

    repository.save(
        incident.model_copy(update={"status": IncidentStatus.RESOLVED})
    )

    assert repository.count() == 1
    assert (
        repository.find_by_id(incident.id).status
        == IncidentStatus.RESOLVED
    )
