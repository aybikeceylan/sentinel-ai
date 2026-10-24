
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from openai import OpenAIError

from app.dependencies import (
    get_investigation_service,
    incident_service as service,
    investigation_repository,
    log_service,
    metric_service,
)
from app.schemas.incident import Incident, IncidentCreate
from app.schemas.investigation import (
    InvestigationReport,
    InvestigationRequest,
)
from app.schemas.log import IncidentLog
from app.schemas.metric import IncidentMetric
from app.services.investigation_service import InvestigationService


router = APIRouter(
    prefix="/api/v1/incidents",
    tags=["Incidents"],
)


def _get_incident_or_404(incident_id: UUID) -> Incident:
    incident = service.get_by_id(incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return incident


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
    return _get_incident_or_404(incident_id)


@router.get(
    "/{incident_id}/logs",
    response_model=list[IncidentLog],
)
async def get_incident_logs(incident_id: UUID):
    _get_incident_or_404(incident_id)

    return log_service.get_incident_logs(incident_id)


@router.get(
    "/{incident_id}/metrics",
    response_model=list[IncidentMetric],
)
async def get_incident_metrics(incident_id: UUID):
    _get_incident_or_404(incident_id)

    return metric_service.get_incident_metrics(incident_id)


@router.post(
    "/{incident_id}/investigate",
    response_model=InvestigationReport,
    status_code=status.HTTP_201_CREATED,
)
def investigate_incident(
    incident_id: UUID,
    payload: InvestigationRequest | None = None,
    investigation_service: InvestigationService = Depends(
        get_investigation_service
    ),
):
    try:
        report = investigation_service.investigate(
            incident_id,
            payload or InvestigationRequest(),
        )
    except (OpenAIError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI investigation failed: {error}",
        ) from error

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return report


@router.get(
    "/{incident_id}/investigations",
    response_model=list[InvestigationReport],
)
async def list_investigations(incident_id: UUID):
    _get_incident_or_404(incident_id)

    return investigation_repository.find_by_incident_id(incident_id)
