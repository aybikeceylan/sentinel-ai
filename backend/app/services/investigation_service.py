
from uuid import UUID

from app.ai.embeddings import Embedder
from app.ai.llm_client import IncidentAnalyzer
from app.ai.prompt import build_investigation_prompt
from app.ai.vector_store import InMemoryVectorStore
from app.repositories.investigation_repository import (
    InvestigationRepository,
)
from app.schemas.incident import Incident, IncidentStatus
from app.schemas.investigation import (
    InvestigationReport,
    InvestigationRequest,
)
from app.services.evidence_service import EvidenceService
from app.services.incident_service import IncidentService


class InvestigationService:
    def __init__(
        self,
        incident_service: IncidentService,
        evidence_service: EvidenceService,
        embedder: Embedder,
        vector_store: InMemoryVectorStore,
        analyzer: IncidentAnalyzer,
        repository: InvestigationRepository,
    ):
        self.incident_service = incident_service
        self.evidence_service = evidence_service
        self.embedder = embedder
        self.vector_store = vector_store
        self.analyzer = analyzer
        self.repository = repository

    def investigate(
        self,
        incident_id: UUID,
        request: InvestigationRequest,
    ) -> InvestigationReport | None:

        incident = self.incident_service.get_by_id(incident_id)

        if incident is None:
            return None

        self._ensure_indexed(incident)

        query_vector = self.embedder.embed([request.question])[0]
        evidence = self.vector_store.search(
            incident.id,
            query_vector,
            request.top_k,
        )

        prompt = build_investigation_prompt(
            incident,
            request.question,
            evidence,
        )
        result = self.analyzer.analyze(prompt)

        if incident.status == IncidentStatus.OPEN:
            self.incident_service.update_status(
                incident,
                IncidentStatus.INVESTIGATING,
            )

        report = InvestigationReport(
            incident_id=incident.id,
            question=request.question,
            model=self.analyzer.model,
            result=result,
            retrieved_evidence=evidence,
        )

        return self.repository.save(report)

    def _ensure_indexed(self, incident: Incident) -> None:
        if self.vector_store.has_incident(incident.id):
            return

        chunks = self.evidence_service.collect(incident)
        vectors = self.embedder.embed([chunk.text for chunk in chunks])

        self.vector_store.add(chunks, vectors)
