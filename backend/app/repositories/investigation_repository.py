
from uuid import UUID

from app.schemas.investigation import InvestigationReport


class InvestigationRepository:
    def __init__(self):
        self._reports: dict[UUID, list[InvestigationReport]] = {}

    def save(self, report: InvestigationReport) -> InvestigationReport:
        self._reports.setdefault(report.incident_id, []).append(report)
        return report

    def find_by_incident_id(
        self,
        incident_id: UUID,
    ) -> list[InvestigationReport]:
        return list(self._reports.get(incident_id, []))
