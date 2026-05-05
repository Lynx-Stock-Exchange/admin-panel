import uuid
from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.core.exceptions import AppException, ValidationException
from app.dtos.event import EventTriggerRequest


class EventService:
    def __init__(self):
        self._stub_events: list[dict] = [
            {
                "event_id": "evt-00000001",
                "event_type": "BULL_RUN",
                "scope": "MARKET",
                "target": None,
                "magnitude": 1.5,
                "duration_ticks": 30,
                "headline": "Global markets surge on positive economic data",
                "triggered_at": "2024-03-15T09:15:00+00:00",
                "triggered_by": "SYSTEM",
            },
            {
                "event_id": "evt-00000002",
                "event_type": "SECTOR_SLUMP",
                "scope": "SECTOR",
                "target": "Tech",
                "magnitude": 1.8,
                "duration_ticks": 20,
                "headline": "Regulatory concerns shake the Tech sector",
                "triggered_at": "2024-03-15T10:30:00+00:00",
                "triggered_by": "ADMIN",
            },
            {
                "event_id": "evt-00000003",
                "event_type": "STOCK_SHOCK",
                "scope": "STOCK",
                "target": "SOLX",
                "magnitude": 2.0,
                "duration_ticks": 10,
                "headline": "Solara Energy hit by surprise regulatory fine",
                "triggered_at": "2024-03-15T11:45:00+00:00",
                "triggered_by": "SYSTEM",
            },
        ]

    def _headers(self) -> dict:
        return {"X-Admin-Token": settings.exchange_admin_token}

    def _handle_response(self, response: httpx.Response) -> dict | list:
        try:
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            try:
                body = e.response.json()
                error = body.get("error", {})
                raise AppException(
                    code=error.get("code", "EXCHANGE_ERROR"),
                    message=error.get("message", "Exchange returned an error."),
                    status_code=e.response.status_code,
                    details=error.get("details", {}),
                )
            except (ValueError, KeyError):
                raise AppException(
                    code="EXCHANGE_ERROR",
                    message=f"Exchange returned status {e.response.status_code}.",
                    status_code=502,
                )
        except httpx.RequestError:
            raise AppException(
                code="EXCHANGE_UNREACHABLE",
                message="Could not reach the exchange. Is it running?",
                status_code=503,
            )

    def _validate_scope(self, req: EventTriggerRequest) -> None:
        if req.scope in ("SECTOR", "STOCK") and not req.target:
            raise ValidationException(
                message=f"'target' is required for scope '{req.scope}'.",
                details={"target": f"Provide a {'sector name' if req.scope == 'SECTOR' else 'ticker'}."},
            )
        if req.scope == "MARKET" and req.target:
            raise ValidationException(
                message="'target' must be null for MARKET scope.",
                details={"target": "Remove target for MARKET-wide events."},
            )

    def list_events(self) -> list[dict]:
        if settings.use_stubs:
            return list(reversed(self._stub_events))
        with httpx.Client() as client:
            response = client.get(
                f"{settings.exchange_base_url}/market/events",
                headers=self._headers(),
            )
            return self._handle_response(response)

    def trigger_event(self, req: EventTriggerRequest) -> dict:
        self._validate_scope(req)

        if settings.use_stubs:
            event = {
                "event_id": f"evt-{uuid.uuid4().hex[:8]}",
                "event_type": req.event_type,
                "scope": req.scope,
                "target": req.target,
                "magnitude": req.magnitude,
                "duration_ticks": req.duration_ticks,
                "headline": req.headline,
                "triggered_at": datetime.now(timezone.utc).isoformat(),
                "triggered_by": "ADMIN",
            }
            self._stub_events.append(event)
            return event

        with httpx.Client() as client:
            response = client.post(
                f"{settings.exchange_base_url}/admin/events/trigger",
                headers=self._headers(),
                json=req.model_dump(),
            )
            return self._handle_response(response)


event_service = EventService()