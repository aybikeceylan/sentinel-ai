
from uuid import uuid4

from app.schemas.log import IncidentLog, LogLevel


def test_create_incident_log():
    incident_id = uuid4()

    log = IncidentLog(
        incident_id=incident_id,
        service="auth-service",
        level=LogLevel.ERROR,
        message="Token refresh failed",
        metadata={
            "status_code": 401,
            "endpoint": "/api/auth/refresh",
        },
    )

    assert log.incident_id == incident_id
    assert log.level == LogLevel.ERROR
    assert log.metadata["status_code"] == 401
    assert log.id is not None
    assert log.timestamp is not None
