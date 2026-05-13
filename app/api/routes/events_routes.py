from fastapi import APIRouter, Depends

from app.api.deps import get_current_admin
from app.dtos.event import EventDefinitionListResponse, EventListResponse, EventTriggerRequest, EventTriggerResponse
from app.services.event_service import event_service

router = APIRouter(dependencies=[Depends(get_current_admin)])


@router.get("", response_model=EventDefinitionListResponse)
def list_events():
    return {"events": event_service.list_events()}


@router.get("/history", response_model=EventListResponse)
def get_event_history():
    return {"events": event_service.get_history()}


@router.post("/trigger", response_model=EventTriggerResponse, status_code=201)
def trigger_event(request: EventTriggerRequest):
    return {
        "message": "Market event triggered successfully.",
        "event": event_service.trigger_event(request),
    }