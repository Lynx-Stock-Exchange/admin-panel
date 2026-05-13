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
        return {"ADMIN-TOKEN": settings.exchange_admin_token}

    def _stub_status(self) -> dict:
        self._stub_state["real_time"] = datetime.now(timezone.utc)
        return dict(self._stub_state)

    def _handle_response(self, response: httpx.Response) -> dict:
        try:
            response.raise_for_status()
            return response.json() if response.content else {}
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
            except (ValueError, KeyError, AttributeError):
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

    def _rest_api_headers(self) -> dict:
        return {"ADMIN-TOKEN": settings.exchange_admin_token}

    def _rest_api(self) -> str:
        return f"{settings.rest_api_url}/api/v1/admin/market"

    def _call_json(self, url: str, **kwargs) -> dict:
        try:
            with httpx.Client() as client:
                response = client.post(url, **kwargs)
                return self._handle_response(response)
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
            except (ValueError, KeyError, AttributeError):
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
            response = client.get(f"{self._rest_api()}/status", headers=self._rest_api_headers())
            return self._handle_response(response)

    def open_market(self) -> dict:
        if settings.use_stubs:
            self._stub_state["is_open"] = True
            self._stub_state["market_time"] = datetime.now(timezone.utc)
            return self._stub_status()
        return self._call_json(f"{self._rest_api()}/open", headers=self._rest_api_headers())

    def close_market(self) -> dict:
        if settings.use_stubs:
            self._stub_state["is_open"] = False
            return self._stub_status()
        return self._call_json(f"{self._rest_api()}/close", headers=self._rest_api_headers())

    def update_speed(self, multiplier: int) -> dict:
        if settings.use_stubs:
            self._stub_state["speed_multiplier"] = multiplier
            return self._stub_status()
        with httpx.Client() as client:
            response = client.put(
                f"{self._rest_api()}/speed",
                json={"multiplier": multiplier},
                headers=self._rest_api_headers(),
            )
            return self._handle_response(response)


market_service = MarketService()
