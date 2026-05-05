from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.core.exceptions import AppException
from app.dtos.stock import StockCreateRequest


class StockService:
    def __init__(self):
        self._stub_stocks: dict[str, dict] = {
            "ARKA": {
                "ticker": "ARKA", "name": "Arkadia Technologies", "sector": "Tech",
                "current_price": 120.00, "open_price": 118.50, "high_price": 121.30,
                "low_price": 117.80, "volume": 45200, "volatility": 0.03,
                "trend_bias": 0.001, "event_weight": 1.5, "momentum": 0.6,
                "listed_at": "2024-03-15T09:00:00",
            },
            "MNVS": {
                "ticker": "MNVS", "name": "Minerva Solutions", "sector": "Finance",
                "current_price": 84.50, "open_price": 83.00, "high_price": 85.10,
                "low_price": 82.40, "volume": 31000, "volatility": 0.02,
                "trend_bias": 0.0005, "event_weight": 1.2, "momentum": 0.4,
                "listed_at": "2024-03-15T09:00:00",
            },
            "SOLX": {
                "ticker": "SOLX", "name": "Solara Energy", "sector": "Energy",
                "current_price": 55.75, "open_price": 56.20, "high_price": 57.00,
                "low_price": 54.90, "volume": 62400, "volatility": 0.04,
                "trend_bias": -0.0005, "event_weight": 1.8, "momentum": 0.7,
                "listed_at": "2024-03-15T09:00:00",
            },
            "VRTX": {
                "ticker": "VRTX", "name": "Vertex Pharma", "sector": "Health",
                "current_price": 210.00, "open_price": 208.00, "high_price": 212.50,
                "low_price": 207.00, "volume": 18900, "volatility": 0.025,
                "trend_bias": 0.002, "event_weight": 1.3, "momentum": 0.5,
                "listed_at": "2024-03-15T09:00:00",
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
                headers=self._headers(),
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
                headers=self._headers(),
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
                headers=self._headers(),
                json=[s.model_dump() for s in stocks],
            )
            return self._handle_response(response)


stock_service = StockService()