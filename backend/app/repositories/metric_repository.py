
from uuid import UUID

from app.db import Database
from app.schemas.metric import IncidentMetric


class MetricRepository:
    def __init__(self, database: Database):
        self.database = database

    def save_many(
        self,
        incident_id: UUID,
        metrics: list[IncidentMetric],
    ) -> None:
        self.database.execute_many(
            "INSERT INTO metrics (id, incident_id, data) VALUES (?, ?, ?)",
            [
                (
                    str(metric.id),
                    str(incident_id),
                    metric.model_dump_json(),
                )
                for metric in metrics
            ],
        )

    def find_by_incident_id(
        self,
        incident_id: UUID,
    ) -> list[IncidentMetric]:
        rows = self.database.execute(
            "SELECT data FROM metrics WHERE incident_id = ? "
            "ORDER BY rowid",
            (str(incident_id),),
        )
        return [
            IncidentMetric.model_validate_json(data) for (data,) in rows
        ]
