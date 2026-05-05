from datetime import datetime, timezone


class MarketService:
    def __init__(self):
        self._state = {
            "is_open": False,
            "market_time": datetime.now(timezone.utc),
            "real_time": datetime.now(timezone.utc),
            "speed_multiplier": 1,
            "active_event": None,
        }

    def _status(self) -> dict:
        self._state["real_time"] = datetime.now(timezone.utc)
        return dict(self._state)

    def get_status(self) -> dict:
        return self._status()

    def open_market(self) -> dict:
        self._state["is_open"] = True
        self._state["market_time"] = datetime.now(timezone.utc)
        return self._status()

    def close_market(self) -> dict:
        self._state["is_open"] = False
        return self._status()

    def update_speed(self, multiplier: int) -> dict:
        self._state["speed_multiplier"] = multiplier
        return self._status()


market_service = MarketService()