from datetime import datetime, timezone
from uuid import uuid4
import secrets


class StubStore:
    def __init__(self):
        now = datetime.now(timezone.utc)

        self.platforms: dict[str, dict] = {}

        self.market = {
            "is_open": False,
            "market_time": now,
            "real_time": now,
            "speed_multiplier": 60,
            "active_event": None,
        }

    def create_platform(self, name: str) -> tuple[dict, str]:
        platform_id = str(uuid4())
        api_key = f"lynx_{secrets.token_hex(12)}"
        api_secret = secrets.token_urlsafe(32)

        platform = {
            "id": platform_id,
            "name": name,
            "api_key": api_key,
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
        }

        self.platforms[platform_id] = platform

        return platform, api_secret


stub_store = StubStore()