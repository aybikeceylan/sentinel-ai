
from uuid import UUID

from app.db import Database
from app.schemas.investigation import InvestigationReport


class InvestigationRepository:
    def __init__(self, database: Database):
        self.database = database

    def save(self, report: InvestigationReport) -> InvestigationReport:
        self.database.execute(
            "INSERT INTO investigations (id, incident_id, data) "
            "VALUES (?, ?, ?)",
            (
                str(report.id),
                str(report.incident_id),
                report.model_dump_json(),
            ),
        )
        return report

    def find_by_incident_id(
        self,
        incident_id: UUID,
    ) -> list[InvestigationReport]:
        rows = self.database.execute(
            "SELECT data FROM investigations WHERE incident_id = ? "
            "ORDER BY rowid",
            (str(incident_id),),
        )
        return [
            InvestigationReport.model_validate_json(data)
            for (data,) in rows
        ]
