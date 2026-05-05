from fastapi import APIRouter, Depends

from app.api.deps import get_current_admin
from app.dtos.event import EventListResponse, EventTriggerRequest, EventTriggerResponse
from app.services.event_service import event_service

router = APIRouter(dependencies=[Depends(get_current_admin)])


@router.get("", response_model=EventListResponse)
def list_events():
    return {"events": event_service.list_events()}


@router.post("/trigger", response_model=EventTriggerResponse, status_code=201)
def trigger_event(request: EventTriggerRequest):
    return {
        "message": "Market event triggered successfully.",
        "event": event_service.trigger_event(request),
    }