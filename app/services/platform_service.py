import httpx
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import AppException, ConflictException, NotFoundException
from app.models.platform import Platform
from app.repositories.platform_repository import PlatformRepository


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PlatformService:
    def __init__(self, platform_repository: PlatformRepository):
        self.platform_repository = platform_repository

    def _gateway(self) -> str:
        return f"{settings.api_gateway_url}/admin/platforms"

    def _headers(self) -> dict:
        return {"ADMIN-TOKEN": settings.exchange_admin_token}

    def _handle_response(self, response: httpx.Response) -> dict:
        try:
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            try:
                body = e.response.json()
                error = body.get("error", {})
                raise AppException(
                    code=error.get("code", "GATEWAY_ERROR"),
                    message=error.get("message", "Gateway returned an error."),
                    status_code=e.response.status_code,
                    details=error.get("details", {}),
                )
            except (ValueError, KeyError):
                raise AppException(
                    code="GATEWAY_ERROR",
                    message=f"Gateway returned status {e.response.status_code}.",
                    status_code=502,
                )
        except httpx.RequestError:
            raise AppException(
                code="GATEWAY_UNREACHABLE",
                message="Could not reach the gateway. Is it running?",
                status_code=503,
            )

    def list_platforms(self) -> list[Platform]:
        return self.platform_repository.get_all()

    def list_active_platforms_internal(self) -> list[Platform]:
        return self.platform_repository.find_active()

    def create_platform(self, name: str, description: str | None = None) -> tuple[Platform, str]:
        existing = self.platform_repository.find_by_name(name)

        if existing:
            raise ConflictException(
                message="A platform with this name already exists.",
                details={"name": "Platform name must be unique."},
            )

        api_key = self._generate_api_key()
        plain_secret = self._generate_api_secret()
        secret_hash = pwd_context.hash(plain_secret)

        platform = Platform(
            name=name,
            description=description,
            api_key=api_key,
            api_secret_hash=secret_hash,
        )

        platform = self.platform_repository.create(platform)

        if not settings.use_stubs:
            with httpx.Client() as client:
                response = client.post(
                    self._gateway(),
                    headers=self._headers(),
                    json={"name": name, "description": description},
                )
                self._handle_response(response)

        return platform, plain_secret

    def revoke_platform(self, platform_id: str) -> Platform:
        try:
            platform_id_value = int(platform_id)
        except ValueError:
            raise NotFoundException(message=f"Platform {platform_id} was not found.")

        platform = self.platform_repository.get_by_id(platform_id_value)

        if not platform:
            raise NotFoundException(message=f"Platform {platform_id} was not found.")

        platform = self.platform_repository.revoke(platform)

        if not settings.use_stubs:
            with httpx.Client() as client:
                response = client.delete(f"{self._gateway()}/{platform_id}", headers=self._headers())
                self._handle_response(response)

        return platform

    def verify_platform_credentials(self, api_key: str, api_secret: str) -> dict:
        platform = self.platform_repository.find_by_api_key(api_key)

        if not platform:
            return {
                "valid": False,
                "platform_id": None,
                "platform_name": None,
            }

        if not platform.is_active:
            return {
                "valid": False,
                "platform_id": None,
                "platform_name": None,
            }

        is_valid_secret = pwd_context.verify(api_secret, platform.api_secret_hash)

        if not is_valid_secret:
            return {
                "valid": False,
                "platform_id": None,
                "platform_name": None,
            }

        return {
            "valid": True,
            "platform_id": str(platform.id),
            "platform_name": platform.name,
        }

    def _generate_api_key(self) -> str:
        import secrets

        return secrets.token_urlsafe(32)

    def _generate_api_secret(self) -> str:
        import secrets

        return secrets.token_urlsafe(32)
