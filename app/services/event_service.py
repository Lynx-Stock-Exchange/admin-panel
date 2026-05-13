import uuid
from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.core.exceptions import AppException, ValidationException
from app.dtos.event import EventTriggerRequest


class EventService:
    def __init__(self):
        self._stub_events: list[dict] = []
        self._triggered_history: list[dict] = []

    def _admin_headers(self) -> dict:
        return {"ADMIN-TOKEN": settings.exchange_admin_token}

    def _platform_headers(self) -> dict:
        return {
            "API-KEY": settings.rest_api_platform_key,
            "API-SECRET": settings.rest_api_platform_secret,
        }

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
        return [
            {
                "event_id": "def-bull-run",
                "event_type": "BULL_RUN",
                "scope": "MARKET",
                "target": None,
                "magnitude": 1.5,
                "duration_ticks": 10,
                "headline": "Global interest rates slashed unexpectedly!",
            },
            {
                "event_id": "def-bear-crash",
                "event_type": "BEAR_CRASH",
                "scope": "MARKET",
                "target": None,
                "magnitude": 1.8,
                "duration_ticks": 10,
                "headline": "Global recession fears grip markets.",
            },
            {
                "event_id": "def-sector-boom",
                "event_type": "SECTOR_BOOM",
                "scope": "SECTOR",
                "target": "TECH",
                "magnitude": 1.5,
                "duration_ticks": 15,
                "headline": "Tech giants report record quarterly earnings.",
            },
            {
                "event_id": "def-sector-slump",
                "event_type": "SECTOR_SLUMP",
                "scope": "SECTOR",
                "target": "TECH",
                "magnitude": 1.8,
                "duration_ticks": 20,
                "headline": "Regulatory concerns shake the Tech sector.",
            },
            {
                "event_id": "def-stock-shock",
                "event_type": "STOCK_SHOCK",
                "scope": "STOCK",
                "target": "ARKA",
                "magnitude": 2.0,
                "duration_ticks": 5,
                "headline": "Breaking: Arkadia Technologies faces unexpected audit.",
            },
        ]

    def get_history(self) -> list[dict]:
        return list(reversed(self._triggered_history))

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
            self._triggered_history.append(event)
            return event

        with httpx.Client() as client:
            response = client.post(
                f"{settings.api_gateway_url}/admin/events/trigger",
                headers=self._admin_headers(),
                json=req.model_dump(),
            )
            event = self._handle_response(response)
            self._triggered_history.append(event)
            return event


event_service = EventService()
