from passlib.context import CryptContext

from app.core.exceptions import ConflictException, NotFoundException
from app.repositories.platform_repository import platform_repository


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PlatformService:
    def list_platforms(self) -> list[dict]:
        return platform_repository.find_all()

    def list_active_platforms_internal(self) -> list[dict]:
        return platform_repository.find_active_internal()

    def create_platform(self, name: str, description: str | None = None) -> tuple[dict, str]:
        existing = platform_repository.find_by_name(name)

        if existing:
            raise ConflictException(
                message="A platform with this name already exists.",
                details={"name": "Platform name must be unique."},
            )

        plain_secret = self._generate_preview_secret()
        secret_hash = pwd_context.hash(plain_secret)

        platform, _ = platform_repository.create(
            name=name,
            description=description,
            api_secret_hash=secret_hash,
        )

        return platform, plain_secret

    def revoke_platform(self, platform_id: str) -> dict:
        platform = platform_repository.revoke(platform_id)

        if not platform:
            raise NotFoundException(message=f"Platform {platform_id} was not found.")

        return platform

    def verify_platform_credentials(self, api_key: str, api_secret: str) -> dict:
        platform = platform_repository.find_by_api_key_internal(api_key)

        if not platform:
            return {
                "valid": False,
                "platform_id": None,
                "platform_name": None,
            }

        if not platform["is_active"]:
            return {
                "valid": False,
                "platform_id": None,
                "platform_name": None,
            }

        is_valid_secret = pwd_context.verify(api_secret, platform["api_secret_hash"])

        if not is_valid_secret:
            return {
                "valid": False,
                "platform_id": None,
                "platform_name": None,
            }

        return {
            "valid": True,
            "platform_id": platform["id"],
            "platform_name": platform["name"],
        }

    def _generate_preview_secret(self) -> str:
        import secrets

        return secrets.token_urlsafe(32)


platform_service = PlatformService()