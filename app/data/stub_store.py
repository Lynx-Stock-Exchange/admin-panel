from datetime import datetime, timezone
from uuid import uuid4
import secrets

from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class StubStore:
    def __init__(self):
        now = datetime.now(timezone.utc)

        self.admins: dict[str, dict] = {
            "admin": {
                "id": str(uuid4()),
                "username": "admin",
                "password_hash": pwd_context.hash("admin123"),
                "is_active": True,
                "created_at": now,
            }
        }

        self.platforms: dict[str, dict] = {}

        self.market = {
            "is_open": False,
            "market_time": now,
            "real_time": now,
            "speed_multiplier": 60,
            "active_event": None,
        }

    def create_platform(self, name: str, description: str | None = None, api_secret_hash: str | None = None) -> tuple[
        dict, str]:
        platform_id = str(uuid4())
        api_key = f"lynx_{secrets.token_hex(12)}"
        api_secret = secrets.token_urlsafe(32)

        platform = {
            "id": platform_id,
            "name": name,
            "description": description,
            "api_key": api_key,
            "api_secret_hash": api_secret_hash,
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "revoked_at": None,
        }

        self.platforms[platform_id] = platform

        safe_platform = platform.copy()
        safe_platform.pop("api_secret_hash", None)

        return safe_platform, api_secret


stub_store = StubStore()