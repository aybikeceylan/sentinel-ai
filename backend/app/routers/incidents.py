
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.schemas.incident import Incident, IncidentCreate
from app.repositories.incident_repository import IncidentRepository
from app.services.incident_service import IncidentService


router = APIRouter(
    prefix="/api/v1/incidents",
    tags=["Incidents"],
)

repository = IncidentRepository()
service = IncidentService(repository)


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
