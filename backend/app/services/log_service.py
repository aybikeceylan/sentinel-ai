
from app.repositories.log_repository import LogRepository
from app.schemas.incident import Incident
from app.schemas.log import IncidentLog
from app.simulators.scenarios import generate_logs


class LogService:
    def __init__(self, repository: LogRepository):
        self.repository = repository

    def get_incident_logs(
        self,
        incident: Incident,
    ) -> list[IncidentLog]:

        existing_logs = self.repository.find_by_incident_id(
            incident.id
        )

        if existing_logs:
            return existing_logs

        logs = generate_logs(incident.scenario, incident.id)

        self.repository.save_many(incident.id, logs)

        return logs
