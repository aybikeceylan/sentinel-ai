
from enum import Enum
from pydantic import BaseModel, Field


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
