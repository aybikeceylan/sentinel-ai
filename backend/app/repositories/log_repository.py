
from uuid import UUID

from app.db import Database
from app.schemas.log import IncidentLog


class LogRepository:
    def __init__(self, database: Database):
        self.database = database

    def save_many(
        self,
        incident_id: UUID,
        logs: list[IncidentLog],
    ) -> None:
        self.database.execute_many(
            "INSERT INTO logs (id, incident_id, data) VALUES (?, ?, ?)",
            [
                (str(log.id), str(incident_id), log.model_dump_json())
                for log in logs
            ],
        )

    def find_by_incident_id(
        self,
        incident_id: UUID,
    ) -> list[IncidentLog]:
        rows = self.database.execute(
            "SELECT data FROM logs WHERE incident_id = ? ORDER BY rowid",
            (str(incident_id),),
        )
        return [IncidentLog.model_validate_json(data) for (data,) in rows]
