
from functools import lru_cache

import chromadb
from chromadb.config import Settings
from fastapi import HTTPException, status
from openai import OpenAI

from app import config
from app.ai.embeddings import OpenAIEmbedder
from app.ai.llm_client import LLMClient
from app.ai.vector_store import ChromaVectorStore, evidence_collection
from app.db import Database
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


database = Database(config.database_path())

incident_service = IncidentService(IncidentRepository(database))
log_service = LogService(LogRepository(database))
metric_service = MetricService(MetricRepository(database))
evidence_service = EvidenceService(log_service, metric_service)

investigation_repository = InvestigationRepository(database)


@lru_cache
def get_investigation_service() -> InvestigationService:
    api_key = config.openai_api_key()

    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OPENAI_API_KEY is not configured",
        )

    openai_client = OpenAI(api_key=api_key)
    embedding_model = config.openai_embedding_model()

    chroma_client = chromadb.PersistentClient(
        path=config.chroma_path(),
        settings=Settings(anonymized_telemetry=False),
    )

    return InvestigationService(
        incident_service=incident_service,
        evidence_service=evidence_service,
        embedder=OpenAIEmbedder(openai_client, embedding_model),
        vector_store=ChromaVectorStore(
            evidence_collection(chroma_client, embedding_model)
        ),
        analyzer=LLMClient(openai_client, config.openai_model()),
        repository=investigation_repository,
    )
