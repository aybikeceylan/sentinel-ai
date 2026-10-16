
from datetime import datetime, timezone
from uuid import uuid4

from app.schemas.metric import MetricType
from app.simulators.metrics_simulator import (
    generate_auth_failure_metrics,
)


def test_generate_auth_failure_metrics():
    incident_id = uuid4()

    base_time = datetime(
        2026, 10, 16, 18, 45, tzinfo=timezone.utc
    )

    metrics = generate_auth_failure_metrics(
        incident_id,
        base_time=base_time,
    )

    assert len(metrics) == 5

    assert all(
        metric.incident_id == incident_id
        for metric in metrics
    )

    assert all(
        metric.metric_type == MetricType.ERROR_RATE
        for metric in metrics
    )

    assert metrics[0].value == 0.02
    assert metrics[-1].value == 0.42

    assert metrics[0].timestamp < metrics[-1].timestamp
