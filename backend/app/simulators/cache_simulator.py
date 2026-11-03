
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.schemas.log import IncidentLog, LogLevel
from app.schemas.metric import IncidentMetric, MetricType
from app.simulators.metrics_simulator import (
    build_metric_series,
    default_base_time,
)


def generate_cache_outage_logs(
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
            "cdn",
            LogLevel.INFO,
            "Static asset cache purge completed",
            {"assets": 1840},
        ),
        log(
            1,
            "redis-cache",
            LogLevel.WARNING,
            "Node redis-cache-2 failed health check",
            {"node": "redis-cache-2", "consecutive_failures": 3},
        ),
        log(
            2,
            "redis-cache",
            LogLevel.ERROR,
            "Node redis-cache-2 removed from cluster, "
            "failover did not complete",
            {"node": "redis-cache-2", "slots_unavailable": 5461},
        ),
        log(
            3,
            "catalog-service",
            LogLevel.WARNING,
            "Cache miss rate increased, falling back to database reads",
            {"cache_hit_ratio": 0.12},
        ),
        log(
            4,
            "notification-service",
            LogLevel.INFO,
            "Email batch sent",
            {"recipients": 5200},
        ),
        log(
            5,
            "catalog-db",
            LogLevel.WARNING,
            "CPU utilization above 90 percent",
            {"cpu_percent": 94},
        ),
    ]


def generate_cache_outage_metrics(
    incident_id: UUID,
    base_time: datetime | None = None,
) -> list[IncidentMetric]:

    base_time = base_time or default_base_time()

    return [
        *build_metric_series(
            incident_id,
            base_time,
            service="catalog-db",
            metric_type=MetricType.REQUEST_COUNT,
            unit="rpm",
            values=[1200, 1300, 5200, 8800, 9100],
        ),
        *build_metric_series(
            incident_id,
            base_time,
            service="catalog-service",
            metric_type=MetricType.LATENCY_P95,
            unit="ms",
            values=[90, 95, 640, 1400, 1650],
        ),
    ]
