
from functools import lru_cache

from fastapi import HTTPException, status
from openai import OpenAI

from app import config
from app.ai.embeddings import OpenAIEmbedder
from app.ai.llm_client import LLMClient
from app.ai.vector_store import InMemoryVectorStore
from app.repositories.incident_repository import IncidentRepository
from app.repositories.investigation_repository import (
    InvestigationRepository,
)
from app.repositories.log_repository import LogRepository
from app.repositories.metric_repository import MetricRepository
from app.services.evidence_service import EvidenceService
from app.services.incident_service import IncidentService
from app.services.investigation_service import InvestigationService
from app.services.log_service import LogService
from app.services.metric_service import MetricService


incident_service = IncidentService(IncidentRepository())
log_service = LogService(LogRepository())
metric_service = MetricService(MetricRepository())
evidence_service = EvidenceService(log_service, metric_service)

vector_store = InMemoryVectorStore()
investigation_repository = InvestigationRepository()


@lru_cache
def get_investigation_service() -> InvestigationService:
    api_key = config.openai_api_key()

    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OPENAI_API_KEY is not configured",
        )

    client = OpenAI(api_key=api_key)

    return InvestigationService(
        incident_service=incident_service,
        evidence_service=evidence_service,
        embedder=OpenAIEmbedder(client, config.openai_embedding_model()),
        vector_store=vector_store,
        analyzer=LLMClient(client, config.openai_model()),
        repository=investigation_repository,
    )
