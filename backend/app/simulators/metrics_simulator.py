
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.schemas.metric import IncidentMetric, MetricType


def generate_auth_failure_metrics(
    incident_id: UUID,
    base_time: datetime | None = None,
) -> list[IncidentMetric]:

    if base_time is None:
         base_time = datetime.now(timezone.utc) - timedelta(minutes=9)

    error_rates = [0.02, 0.03, 0.18, 0.32, 0.42]

    metrics = []

    for index, error_rate in enumerate(error_rates):
        metric = IncidentMetric(
            incident_id=incident_id,
            timestamp=base_time + timedelta(
                minutes=index * 2
            ),
            service="auth-service",
            metric_type=MetricType.ERROR_RATE,
            value=error_rate,
            unit="ratio",
        )

        metrics.append(metric)

    return metrics
