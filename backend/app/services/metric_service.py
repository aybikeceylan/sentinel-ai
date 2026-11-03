
from app.repositories.metric_repository import MetricRepository
from app.schemas.incident import Incident
from app.schemas.metric import IncidentMetric
from app.simulators.scenarios import generate_metrics


class MetricService:
    def __init__(self, repository: MetricRepository):
        self.repository = repository

    def get_incident_metrics(
        self,
        incident: Incident,
    ) -> list[IncidentMetric]:

        existing_metrics = self.repository.find_by_incident_id(
            incident.id
        )

        if existing_metrics:
            return existing_metrics

        metrics = generate_metrics(incident.scenario, incident.id)

        self.repository.save_many(incident.id, metrics)

        return metrics
