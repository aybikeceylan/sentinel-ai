
from app.ai.chunking import build_evidence_chunks
from app.schemas.evidence import EvidenceChunk
from app.schemas.incident import Incident
from app.services.log_service import LogService
from app.services.metric_service import MetricService


class EvidenceService:
    def __init__(
        self,
        log_service: LogService,
        metric_service: MetricService,
    ):
        self.log_service = log_service
        self.metric_service = metric_service

    def collect(self, incident: Incident) -> list[EvidenceChunk]:
        logs = self.log_service.get_incident_logs(incident.id)
        metrics = self.metric_service.get_incident_metrics(incident.id)

        return build_evidence_chunks(incident, logs, metrics)
