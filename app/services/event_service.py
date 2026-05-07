import uuid
from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.core.exceptions import AppException, ValidationException
from app.dtos.event import EventTriggerRequest


class EventService:
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




event_service = EventService()