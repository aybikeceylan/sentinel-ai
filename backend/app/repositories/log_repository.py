
from uuid import UUID

from app.schemas.log import IncidentLog


class LogRepository:
    def __init__(self):
        self._logs: dict[UUID, list[IncidentLog]] = {}

    def save_many(
        self,
        incident_id: UUID,
        logs: list[IncidentLog],
    ) -> None:
        self._logs.setdefault(incident_id, []).extend(logs)

    def find_by_incident_id(
        self,
        incident_id: UUID,
    ) -> list[IncidentLog]:
        return list(self._logs.get(incident_id, []))
