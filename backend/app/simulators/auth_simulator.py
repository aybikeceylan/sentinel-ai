
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.schemas.log import IncidentLog, LogLevel


def generate_auth_failure_logs(
    incident_id: UUID,
) -> list[IncidentLog]:

    base_time = datetime.now(timezone.utc)

    logs = [
        IncidentLog(
            incident_id=incident_id,
            timestamp=base_time,
            service="deployment-service",
            level=LogLevel.INFO,
            message="Deployment completed: auth-service v2.4.0",
            metadata={
                "version": "2.4.0",
                "environment": "production",
            },
        ),
        IncidentLog(
            incident_id=incident_id,
            timestamp=base_time + timedelta(minutes=2),
            service="auth-service",
            level=LogLevel.ERROR,
            message="Refresh token signature verification failed",
            metadata={
                "status_code": 401,
                "endpoint": "/api/auth/refresh",
                "error_code": "INVALID_TOKEN_SIGNATURE",
            },
        ),
        IncidentLog(
            incident_id=incident_id,
            timestamp=base_time + timedelta(minutes=3),
            service="auth-service",
            level=LogLevel.ERROR,
            message="Multiple users receiving 401 Unauthorized",
            metadata={
                "status_code": 401,
                "affected_users": 145,
            },
        ),
        IncidentLog(
            incident_id=incident_id,
            timestamp=base_time + timedelta(minutes=5),
            service="monitoring-service",
            level=LogLevel.CRITICAL,
            message="Authentication error rate exceeded threshold",
            metadata={
                "error_rate": 0.42,
                "threshold": 0.10,
            },
        ),
    ]

    return logs
