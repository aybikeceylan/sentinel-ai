
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.schemas.incident import Incident, IncidentCreate
from app.repositories.incident_repository import IncidentRepository
from app.services.incident_service import IncidentService

from app.repositories.log_repository import LogRepository
from app.services.log_service import LogService
from app.schemas.log import IncidentLog

from app.schemas.metric import IncidentMetric
from app.repositories.metric_repository import MetricRepository
from app.services.metric_service import MetricService


router = APIRouter(
    prefix="/api/v1/incidents",
    tags=["Incidents"],
)

repository = IncidentRepository()
service = IncidentService(repository)

log_repository = LogRepository()
log_service = LogService(log_repository)

metric_repository = MetricRepository()
metric_service = MetricService(metric_repository)


@router.post(
    "",
    response_model=Incident,
    status_code=status.HTTP_201_CREATED,
)
async def create_incident(payload: IncidentCreate):
    return service.create(payload)


@router.get("", response_model=list[Incident])
async def list_incidents():
    return service.get_all()


@router.get("/count")
async def get_incident_count():
    return {"count": service.count()}


@router.get("/{incident_id}", response_model=Incident)
async def get_incident(incident_id: UUID):
    incident = service.get_by_id(incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return incident


@router.get(
    "/{incident_id}/logs",
    response_model=list[IncidentLog],
)
async def get_incident_logs(incident_id: UUID):
    incident = service.get_by_id(incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return log_service.get_incident_logs(incident_id)

@router.get(
    "/{incident_id}/metrics",
    response_model=list[IncidentMetric],
)
async def get_incident_metrics(incident_id: UUID):
    incident = service.get_by_id(incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return metric_service.get_incident_metrics(incident_id)