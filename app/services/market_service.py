from datetime import datetime, timezone

from app.data.stub_store import stub_store


class MarketService:
    def get_status(self) -> dict:
        stub_store.market["real_time"] = datetime.now(timezone.utc)
        return stub_store.market

    def open_market(self) -> dict:
        now = datetime.now(timezone.utc)

        stub_store.market["is_open"] = True
        stub_store.market["market_time"] = now
        stub_store.market["real_time"] = now

        return stub_store.market

    def close_market(self) -> dict:
        stub_store.market["is_open"] = False
        stub_store.market["real_time"] = datetime.now(timezone.utc)

        return stub_store.market

    def update_speed(self, multiplier: int) -> dict:
        stub_store.market["speed_multiplier"] = multiplier
        stub_store.market["real_time"] = datetime.now(timezone.utc)

        return stub_store.market


market_service = MarketService()