
from uuid import UUID

from app.repositories.metric_repository import MetricRepository
from app.schemas.metric import IncidentMetric
from app.simulators.metrics_simulator import (
    generate_auth_failure_metrics,
)


class MetricService:
    def __init__(self, repository: MetricRepository):
        self.repository = repository

    def get_incident_metrics(
        self,
        incident_id: UUID,
    ) -> list[IncidentMetric]:

        existing_metrics = self.repository.find_by_incident_id(
            incident_id
        )

        if existing_metrics:
            return existing_metrics

        metrics = generate_auth_failure_metrics(incident_id)

        self.repository.save_many(incident_id, metrics)

        return metrics
