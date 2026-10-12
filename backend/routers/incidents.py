
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.schemas.incident import Incident, IncidentCreate


router = APIRouter(
    prefix="/api/v1/incidents",
    tags=["Incidents"],
)

# Temporary in-memory storage
incidents_db: dict[UUID, Incident] = {}


@router.post(
    "",
    response_model=Incident,
    status_code=status.HTTP_201_CREATED,
)
async def create_incident(payload: IncidentCreate):
    incident = Incident(**payload.model_dump())
    incidents_db[incident.id] = incident

    return incident


@router.get("", response_model=list[Incident])
async def list_incidents():
    return list(incidents_db.values())


@router.get("/{incident_id}", response_model=Incident)
async def get_incident(incident_id: UUID):
    incident = incidents_db.get(incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return incident
