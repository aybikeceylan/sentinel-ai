
from uuid import uuid4

from app.schemas.log import LogLevel
from app.simulators.auth_simulator import generate_auth_failure_logs


def test_generate_auth_failure_logs():
    incident_id = uuid4()

    logs = generate_auth_failure_logs(incident_id)

    assert len(logs) == 4

    assert all(
        log.incident_id == incident_id
        for log in logs
    )

    assert logs[0].level == LogLevel.INFO
    assert logs[1].level == LogLevel.ERROR
    assert logs[3].level == LogLevel.CRITICAL

    assert logs[0].timestamp < logs[1].timestamp
    assert logs[1].timestamp < logs[2].timestamp
    assert logs[2].timestamp < logs[3].timestamp
