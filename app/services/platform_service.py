from app.core.exceptions import ConflictException, NotFoundException
from app.data.stub_store import stub_store


class PlatformService:
    def list_platforms(self) -> list[dict]:
        return list(stub_store.platforms.values())

    def create_platform(self, name: str) -> tuple[dict, str]:
        existing = [
            platform
            for platform in stub_store.platforms.values()
            if platform["name"].lower() == name.lower()
        ]

        if existing:
            raise ConflictException(
                message="A platform with this name already exists.",
                details={"name": "Platform name must be unique."},
            )

        return stub_store.create_platform(name)

    def revoke_platform(self, platform_id: str) -> dict:
        platform = stub_store.platforms.get(platform_id)

        if not platform:
            raise NotFoundException(message=f"Platform {platform_id} was not found.")

        platform["is_active"] = False
        return platform


platform_service = PlatformService()