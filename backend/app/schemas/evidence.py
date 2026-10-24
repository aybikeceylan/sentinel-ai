from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class EvidenceSource(str, Enum):
    INCIDENT = "incident"
    LOG = "log"
    METRIC = "metric"
    METRIC_TREND = "metric_trend"


class EvidenceChunk(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    incident_id: UUID
    source: EvidenceSource
    text: str


class RetrievedEvidence(BaseModel):
    chunk: EvidenceChunk
    score: float
