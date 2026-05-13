from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.core.exceptions import AppException
from app.dtos.stock import StockCreateRequest


class StockService:
    def __init__(self):
        self._stub_stocks: dict[str, dict] = {}

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

    def _stub_stock_from_request(self, req: StockCreateRequest) -> dict:
        return {
            "ticker": req.ticker,
            "name": req.name,
            "sector": req.sector,
            "current_price": req.start_price,
            "open_price": req.start_price,
            "high_price": req.start_price,
            "low_price": req.start_price,
            "volume": 0,
            "volatility": req.volatility,
            "trend_bias": req.trend_bias,
            "event_weight": req.event_weight,
            "momentum": req.momentum,
            "listed_at": datetime.now(timezone.utc).isoformat(),
        }

    def list_stocks(self) -> list[dict]:
        if settings.use_stubs:
            return list(self._stub_stocks.values())
        with httpx.Client() as client:
            response = client.get(
                f"{settings.exchange_base_url}/market/stocks",
                headers=self._platform_headers(),
            )
            return self._handle_response(response)

    def create_stock(self, req: StockCreateRequest) -> dict:
        if settings.use_stubs:
            if req.ticker in self._stub_stocks:
                raise AppException(
                    code="RESOURCE_EXISTS",
                    message=f"Stock '{req.ticker}' already exists.",
                    status_code=409,
                )
            stock = self._stub_stock_from_request(req)
            self._stub_stocks[req.ticker] = stock
            return stock
        with httpx.Client() as client:
            response = client.post(
                f"{settings.exchange_base_url}/admin/stocks",
                headers=self._admin_headers(),
                json=req.model_dump(),
            )
            return self._handle_response(response)

    def seed_stocks(self, stocks: list[StockCreateRequest]) -> list[dict]:
        if settings.use_stubs:
            created = []
            for req in stocks:
                if req.ticker not in self._stub_stocks:
                    stock = self._stub_stock_from_request(req)
                    self._stub_stocks[req.ticker] = stock
                    created.append(stock)
            return created
        with httpx.Client() as client:
            response = client.post(
                f"{settings.exchange_base_url}/admin/stocks/seed",
                headers=self._admin_headers(),
                json=[s.model_dump() for s in stocks],
            )
            return self._handle_response(response)


stock_service = StockService()
