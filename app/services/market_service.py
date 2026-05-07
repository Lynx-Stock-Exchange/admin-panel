import httpx

from app.core.config import settings
from app.core.exceptions import AppException


class MarketService:
    def _headers(self) -> dict:
        return {"X-Admin-Token": settings.exchange_admin_token}

    def _base(self) -> str:
        return f"{settings.exchange_base_url}/admin/market"

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
        with httpx.Client() as client:
            response = client.get(f"{self._base()}/status", headers=self._headers())
            return self._handle_response(response)

    def open_market(self) -> dict:
        with httpx.Client() as client:
            client.post(f"{self._base()}/open", headers=self._headers())
        return self.get_status()

    def close_market(self) -> dict:
        with httpx.Client() as client:
            client.post(f"{self._base()}/close", headers=self._headers())
        return self.get_status()

    def update_speed(self, multiplier: int) -> dict:
        with httpx.Client() as client:
            client.put(
                f"{self._base()}/speed",
                headers=self._headers(),
                json={"multiplier": multiplier},
            )
        return self.get_status()


market_service = MarketService()