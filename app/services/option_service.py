import uuid

import httpx

from app.core.config import settings
from app.core.exceptions import AppException
from app.dtos.option import OptionCreateRequest


class OptionService:
    def __init__(self):
        self._stub_options: dict[str, dict] = {
            "opt-arka-call-1": {
                "option_id": "opt-arka-call-1",
                "underlying_ticker": "ARKA",
                "option_type": "CALL",
                "strike_price": 130.00,
                "expiry_time": "2024-03-15T14:00:00",
                "premium": 5.00,
                "is_active": True,
                "auto_exercise": True,
            },
            "opt-arka-put-1": {
                "option_id": "opt-arka-put-1",
                "underlying_ticker": "ARKA",
                "option_type": "PUT",
                "strike_price": 110.00,
                "expiry_time": "2024-03-15T14:00:00",
                "premium": 3.50,
                "is_active": True,
                "auto_exercise": True,
            },
            "opt-solx-call-1": {
                "option_id": "opt-solx-call-1",
                "underlying_ticker": "SOLX",
                "option_type": "CALL",
                "strike_price": 60.00,
                "expiry_time": "2024-03-15T16:00:00",
                "premium": 2.20,
                "is_active": True,
                "auto_exercise": True,
            },
        }

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

    def list_options(self) -> list[dict]:
        if settings.use_stubs:
            return list(self._stub_options.values())
        with httpx.Client() as client:
            response = client.get(
                f"{settings.exchange_base_url}/market/options",
                headers=self._headers(),
            )
            return self._handle_response(response)

    def create_option(self, req: OptionCreateRequest) -> dict:
        if settings.use_stubs:
            option_id = f"opt-{uuid.uuid4().hex[:8]}"
            option = {
                "option_id": option_id,
                "underlying_ticker": req.underlying_ticker,
                "option_type": req.option_type,
                "strike_price": req.strike_price,
                "expiry_time": req.expiry_time.isoformat(),
                "premium": req.initial_premium,
                "is_active": True,
                "auto_exercise": True,
            }
            self._stub_options[option_id] = option
            return option
        with httpx.Client() as client:
            response = client.post(
                f"{settings.exchange_base_url}/admin/options",
                headers=self._headers(),
                json=req.model_dump(mode="json"),
            )
            return self._handle_response(response)


option_service = OptionService()