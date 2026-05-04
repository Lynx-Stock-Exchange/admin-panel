from datetime import datetime, timezone

from app.data.stub_store import stub_store


class PlatformRepository:
    def find_all(self) -> list[dict]:
        return [
            self._without_secret(platform)
            for platform in stub_store.platforms.values()
        ]

    def find_active_internal(self) -> list[dict]:
        return [
            platform.copy()
            for platform in stub_store.platforms.values()
            if platform["is_active"]
        ]

    def find_by_id(self, platform_id: str) -> dict | None:
        platform = stub_store.platforms.get(platform_id)

        if not platform:
            return None

        return self._without_secret(platform)

    def find_by_name(self, name: str) -> dict | None:
        for platform in stub_store.platforms.values():
            if platform["name"].lower() == name.lower():
                return self._without_secret(platform)

        return None

    def find_by_api_key_internal(self, api_key: str) -> dict | None:
        for platform in stub_store.platforms.values():
            if platform["api_key"] == api_key:
                return platform.copy()

        return None

    def create(
        self,
        name: str,
        description: str | None,
        api_secret_hash: str,
    ) -> tuple[dict, str]:
        return stub_store.create_platform(name, description, api_secret_hash)

    def revoke(self, platform_id: str) -> dict | None:
        platform = stub_store.platforms.get(platform_id)

        if not platform:
            return None

        platform["is_active"] = False
        platform["revoked_at"] = datetime.now(timezone.utc)

        return self._without_secret(platform)

    def _without_secret(self, platform: dict) -> dict:
        safe_platform = platform.copy()
        safe_platform.pop("api_secret_hash", None)
        return safe_platform


platform_repository = PlatformRepository()