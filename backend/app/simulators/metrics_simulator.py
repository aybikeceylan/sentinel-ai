
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.schemas.metric import IncidentMetric, MetricType


SAMPLE_INTERVAL = timedelta(minutes=2)


def build_metric_series(
    incident_id: UUID,
    base_time: datetime,
    service: str,
    metric_type: MetricType,
    unit: str,
    values: list[float],
) -> list[IncidentMetric]:

    return [
        IncidentMetric(
            incident_id=incident_id,
            timestamp=base_time + index * SAMPLE_INTERVAL,
            service=service,
            metric_type=metric_type,
            value=value,
            unit=unit,
        )
        for index, value in enumerate(values)
    ]


def default_base_time() -> datetime:
    return datetime.now(timezone.utc) - timedelta(minutes=9)


def generate_auth_failure_metrics(
    incident_id: UUID,
    base_time: datetime | None = None,
) -> list[IncidentMetric]:

    return build_metric_series(
        incident_id,
        base_time or default_base_time(),
        service="auth-service",
        metric_type=MetricType.ERROR_RATE,
        unit="ratio",
        values=[0.02, 0.03, 0.18, 0.32, 0.42],
    )
