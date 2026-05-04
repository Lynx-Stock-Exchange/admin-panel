from app.core.exceptions import AppException
from app.core.security import create_admin_access_token, verify_password
from app.repositories.admin_repository import admin_repository


class AuthService:
    def login(self, username: str, password: str) -> tuple[dict, str]:
        admin = admin_repository.find_by_username(username)

        if not admin or not admin["is_active"]:
            raise AppException(
                code="INVALID_CREDENTIALS",
                message="Invalid username or password.",
                status_code=401,
                details={},
            )

        if not verify_password(password, admin["password_hash"]):
            raise AppException(
                code="INVALID_CREDENTIALS",
                message="Invalid username or password.",
                status_code=401,
                details={},
            )

        token = create_admin_access_token(admin)

        return admin, token


auth_service = AuthService()