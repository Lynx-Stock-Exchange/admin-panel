import httpx

from app.core.config import settings
from app.core.exceptions import AppException
from app.dtos.stock import StockCreateRequest


class StockService:
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

    def list_stocks(self) -> list[dict]:
        with httpx.Client() as client:
            response = client.get(
                f"{settings.exchange_base_url}/market/stocks",
                headers=self._headers(),
            )
            return self._handle_response(response)

    def create_stock(self, req: StockCreateRequest) -> dict:
        with httpx.Client() as client:
            response = client.post(
                f"{settings.exchange_base_url}/admin/stocks",
                headers=self._headers(),
                json=req.model_dump(),
            )
            return self._handle_response(response)

    def get_total(self) -> dict:
        return {"count": len(self.list_stocks())}

    def seed_stocks(self, stocks: list[StockCreateRequest]) -> list[dict]:
        with httpx.Client() as client:
            response = client.post(
                f"{settings.exchange_base_url}/admin/stocks/seed",
                headers=self._headers(),
                json=[s.model_dump() for s in stocks],
            )
            return self._handle_response(response)


stock_service = StockService()