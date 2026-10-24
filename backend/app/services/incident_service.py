
from uuid import UUID

from app.repositories.incident_repository import IncidentRepository
from app.schemas.incident import (
    Incident,
    IncidentCreate,
    IncidentStatus,
)


class IncidentService:
    def __init__(self, repository: IncidentRepository):
        self.repository = repository

    def create(self, payload: IncidentCreate) -> Incident:
        incident = Incident(**payload.model_dump())
        return self.repository.save(incident)

    def get_all(self) -> list[Incident]:
        return self.repository.find_all()

    def get_by_id(self, incident_id: UUID) -> Incident | None:
        return self.repository.find_by_id(incident_id)

    def count(self) -> int:
        return len(self.repository.find_all())

    def update_status(
        self,
        incident: Incident,
        status: IncidentStatus,
    ) -> Incident:
        updated = incident.model_copy(update={"status": status})
        return self.repository.save(updated)
