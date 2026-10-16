
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MetricType(str, Enum):
    ERROR_RATE = "error_rate"
    LATENCY_P95 = "latency_p95"
    REQUEST_COUNT = "request_count"


class IncidentMetric(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    incident_id: UUID
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    service: str
    metric_type: MetricType
    value: float
    unit: str
