
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class LogLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class IncidentLog(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    incident_id: UUID
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    service: str
    level: LogLevel
    message: str
    metadata: dict[str, str | int | float | bool] = Field(
        default_factory=dict
    )
