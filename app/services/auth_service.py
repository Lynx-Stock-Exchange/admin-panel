from app.core.exceptions import AppException
from app.core.security import create_admin_access_token, verify_password
from app.repositories.admin_repository import AdminRepository


class AuthService:
    def __init__(self, admin_repository: AdminRepository):
        self.admin_repository = admin_repository

    def login(self, username: str, password: str):
        admin = self.admin_repository.find_by_username(username)

        if not admin or not admin.is_active:
            raise AppException(
                code="INVALID_CREDENTIALS",
                message="Invalid username or password.",
                status_code=401,
                details={},
            )

        if not verify_password(password, admin.password_hash):
            raise AppException(
                code="INVALID_CREDENTIALS",
                message="Invalid username or password.",
                status_code=401,
                details={},
            )

        token = create_admin_access_token(admin)

        return admin, token