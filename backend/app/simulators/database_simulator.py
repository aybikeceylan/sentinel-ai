
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.schemas.log import IncidentLog, LogLevel
from app.schemas.metric import IncidentMetric, MetricType
from app.simulators.metrics_simulator import (
    build_metric_series,
    default_base_time,
)


def generate_database_pool_logs(
    incident_id: UUID,
) -> list[IncidentLog]:

    base_time = datetime.now(timezone.utc)

    def log(minutes, service, level, message, metadata):
        return IncidentLog(
            incident_id=incident_id,
            timestamp=base_time + timedelta(minutes=minutes),
            service=service,
            level=level,
            message=message,
            metadata=metadata,
        )

    return [
        log(
            0,
            "deployment-service",
            LogLevel.INFO,
            "Deployment completed: order-service v3.1.0 "
            "with worker concurrency increased from 8 to 32",
            {"version": "3.1.0", "environment": "production"},
        ),
        log(
            1,
            "backup-service",
            LogLevel.INFO,
            "Nightly backup completed",
            {"duration_seconds": 412},
        ),
        log(
            3,
            "order-service",
            LogLevel.WARNING,
            "Database connection pool nearing capacity",
            {"pool": "primary", "in_use": 19, "max_size": 20},
        ),
        log(
            4,
            "order-service",
            LogLevel.ERROR,
            "Timed out acquiring database connection after 30s",
            {"pool": "primary", "waiting_requests": 87},
        ),
        log(
            5,
            "api-gateway",
            LogLevel.ERROR,
            "Upstream order-service returned 504 Gateway Timeout",
            {"endpoint": "/api/orders", "status_code": 504},
        ),
        log(
            6,
            "postgres-primary",
            LogLevel.INFO,
            "Active connections within limits",
            {"active_connections": 20, "max_connections": 200},
        ),
    ]


def generate_database_pool_metrics(
    incident_id: UUID,
    base_time: datetime | None = None,
) -> list[IncidentMetric]:

    base_time = base_time or default_base_time()

    return [
        *build_metric_series(
            incident_id,
            base_time,
            service="order-service",
            metric_type=MetricType.LATENCY_P95,
            unit="ms",
            values=[180, 240, 950, 2100, 3000],
        ),
        *build_metric_series(
            incident_id,
            base_time,
            service="order-service",
            metric_type=MetricType.ERROR_RATE,
            unit="ratio",
            values=[0.01, 0.01, 0.06, 0.17, 0.24],
        ),
    ]
