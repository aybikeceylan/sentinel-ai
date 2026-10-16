
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class IncidentSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"


class IncidentCreate(BaseModel):
    title: str = Field(min_length=5, max_length=200)
    description: str = Field(min_length=10)
    severity: IncidentSeverity


class Incident(IncidentCreate):
    id: UUID = Field(default_factory=uuid4)
    status: IncidentStatus = IncidentStatus.OPEN
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
