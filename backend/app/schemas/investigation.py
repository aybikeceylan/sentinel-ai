
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.schemas.evidence import RetrievedEvidence


DEFAULT_QUESTION = (
    "What is the most likely root cause of this incident "
    "and what should be done next?"
)


class ConfidenceLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class InvestigationResult(BaseModel):
    summary: str
    probable_root_cause: str
    confidence: ConfidenceLevel
    evidence: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(
        default_factory=list
    )


class InvestigationRequest(BaseModel):
    question: str = Field(
        default=DEFAULT_QUESTION,
        min_length=5,
        max_length=500,
    )
    top_k: int = Field(default=6, ge=1, le=20)


class InvestigationReport(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    incident_id: UUID
    question: str
    model: str
    result: InvestigationResult
    retrieved_evidence: list[RetrievedEvidence]
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
