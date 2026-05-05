import httpx

from app.core.config import settings
from app.core.exceptions import AppException
from app.dtos.fee import FeeRateUpdateRequest
from app.dtos.option import OptionCreateRequest
from app.dtos.seed import SeedRequest
from app.dtos.stock import StockCreateRequest
from app.services.fee_service import fee_service
from app.services.market_service import market_service
from app.services.option_service import option_service
from app.services.stock_service import stock_service


class SeedService:
    def _headers(self) -> dict:
        return {"X-Admin-Token": settings.exchange_admin_token}

    def _send_events_config_to_exchange(self, events_config: dict) -> None:
        with httpx.Client() as client:
            response = client.post(
                f"{settings.exchange_base_url}/admin/events/config",
                headers=self._headers(),
                json=events_config,
            )
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                raise AppException(
                    code="EXCHANGE_ERROR",
                    message=f"Failed to push event config to exchange: {e.response.status_code}",
                    status_code=502,
                )
            except httpx.RequestError:
                raise AppException(
                    code="EXCHANGE_UNREACHABLE",
                    message="Could not reach the exchange. Is it running?",
                    status_code=503,
                )

    def apply(self, req: SeedRequest) -> dict:
        # 1. Exchange config: fee rate + speed
        fee_service.update_fee_rate(FeeRateUpdateRequest(rate=req.exchange.fee_rate))
        market_service.update_speed(req.exchange.default_speed_multiplier)

        # 2. Stocks
        stock_requests = [StockCreateRequest(**s.model_dump()) for s in req.stocks]
        seeded_stocks = stock_service.seed_stocks(stock_requests)

        # 3. Options
        seeded_options = []
        for entry in req.options:
            option = option_service.create_option(OptionCreateRequest(**entry.model_dump()))
            seeded_options.append(option)

        # 4. Event definitions + headlines
        event_definitions_loaded = 0
        if req.events:
            event_definitions_loaded = len(req.events.definitions)
            if not settings.use_stubs:
                self._send_events_config_to_exchange(req.events.model_dump(mode="json"))

        return {
            "message": "Seed applied successfully.",
            "fee_rate": req.exchange.fee_rate,
            "speed_multiplier": req.exchange.default_speed_multiplier,
            "stocks_seeded": len(seeded_stocks),
            "options_seeded": len(seeded_options),
            "event_definitions_loaded": event_definitions_loaded,
        }


seed_service = SeedService()