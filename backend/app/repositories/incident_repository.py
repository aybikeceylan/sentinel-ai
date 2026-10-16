
from uuid import UUID

from app.schemas.incident import Incident


class IncidentRepository:
    def __init__(self):
        self._incidents: dict[UUID, Incident] = {}

    def save(self, incident: Incident) -> Incident:
        self._incidents[incident.id] = incident
        return incident

    def find_all(self) -> list[Incident]:
        return list(self._incidents.values())

    def find_by_id(self, incident_id: UUID) -> Incident | None:
        return self._incidents.get(incident_id)
