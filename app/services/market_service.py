from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.core.exceptions import AppException


class MarketService:
    def __init__(self):
        self._stub_state = {
            "is_open": False,
            "market_time": datetime.now(timezone.utc),
            "real_time": datetime.now(timezone.utc),
            "speed_multiplier": 1,
            "active_event": None,
        }

    def _headers(self) -> dict:
        return {"X-Admin-Token": settings.exchange_admin_token}

    def _stub_status(self) -> dict:
        self._stub_state["real_time"] = datetime.now(timezone.utc)
        return dict(self._stub_state)

    def _handle_response(self, response: httpx.Response) -> dict:
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

    def get_status(self) -> dict:
        if settings.use_stubs:
            return self._stub_status()
        with httpx.Client() as client:
            response = client.get(
                f"{settings.exchange_base_url}/market/status",
                headers=self._headers(),
            )
            return self._handle_response(response)

    def open_market(self) -> dict:
        if settings.use_stubs:
            self._stub_state["is_open"] = True
            self._stub_state["market_time"] = datetime.now(timezone.utc)
            return self._stub_status()
        with httpx.Client() as client:
            response = client.post(
                f"{settings.exchange_base_url}/admin/market/open",
                headers=self._headers(),
            )
            return self._handle_response(response)

    def close_market(self) -> dict:
        if settings.use_stubs:
            self._stub_state["is_open"] = False
            return self._stub_status()
        with httpx.Client() as client:
            response = client.post(
                f"{settings.exchange_base_url}/admin/market/close",
                headers=self._headers(),
            )
            return self._handle_response(response)

    def update_speed(self, multiplier: int) -> dict:
        if settings.use_stubs:
            self._stub_state["speed_multiplier"] = multiplier
            return self._stub_status()
        with httpx.Client() as client:
            response = client.put(
                f"{settings.exchange_base_url}/admin/market/speed",
                headers=self._headers(),
                json={"multiplier": multiplier},
            )
            return self._handle_response(response)


market_service = MarketService()