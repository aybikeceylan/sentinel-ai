
from uuid import UUID

from app.repositories.log_repository import LogRepository
from app.schemas.log import IncidentLog
from app.simulators.auth_simulator import generate_auth_failure_logs


class LogService:
    def __init__(self, repository: LogRepository):
        self.repository = repository

    def get_incident_logs(
        self,
        incident_id: UUID,
    ) -> list[IncidentLog]:

        existing_logs = self.repository.find_by_incident_id(
            incident_id
        )

        if existing_logs:
            return existing_logs

        logs = generate_auth_failure_logs(incident_id)

        self.repository.save_many(incident_id, logs)

        return logs
