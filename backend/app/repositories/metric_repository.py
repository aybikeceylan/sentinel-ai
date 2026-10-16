
from uuid import UUID

from app.schemas.metric import IncidentMetric


class MetricRepository:
    def __init__(self):
        self._metrics: dict[UUID, list[IncidentMetric]] = {}

    def save_many(
        self,
        incident_id: UUID,
        metrics: list[IncidentMetric],
    ) -> None:
        self._metrics.setdefault(incident_id, []).extend(metrics)

    def find_by_incident_id(
        self,
        incident_id: UUID,
    ) -> list[IncidentMetric]:
        return list(self._metrics.get(incident_id, []))
