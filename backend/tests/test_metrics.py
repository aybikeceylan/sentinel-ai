
from uuid import uuid4

from app.schemas.metric import IncidentMetric, MetricType


def test_create_incident_metric():
    incident_id = uuid4()

    metric = IncidentMetric(
        incident_id=incident_id,
        service="auth-service",
        metric_type=MetricType.ERROR_RATE,
        value=0.42,
        unit="ratio",
    )

    assert metric.incident_id == incident_id
    assert metric.service == "auth-service"
    assert metric.metric_type == MetricType.ERROR_RATE
    assert metric.value == 0.42
    assert metric.unit == "ratio"
    assert metric.id is not None
