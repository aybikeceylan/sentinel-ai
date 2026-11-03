
from uuid import UUID

from app.db import Database
from app.schemas.incident import Incident


class IncidentRepository:
    def __init__(self, database: Database):
        self.database = database

    def save(self, incident: Incident) -> Incident:
        self.database.execute(
            "INSERT INTO incidents (id, data) VALUES (?, ?) "
            "ON CONFLICT(id) DO UPDATE SET data = excluded.data",
            (str(incident.id), incident.model_dump_json()),
        )
        return incident

    def find_all(self) -> list[Incident]:
        rows = self.database.execute(
            "SELECT data FROM incidents ORDER BY rowid"
        )
        return [Incident.model_validate_json(data) for (data,) in rows]

    def find_by_id(self, incident_id: UUID) -> Incident | None:
        rows = self.database.execute(
            "SELECT data FROM incidents WHERE id = ?",
            (str(incident_id),),
        )

        if not rows:
            return None

        return Incident.model_validate_json(rows[0][0])

    def count(self) -> int:
        rows = self.database.execute("SELECT COUNT(*) FROM incidents")
        return rows[0][0]
