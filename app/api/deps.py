from fastapi import Cookie, Depends
from sqlmodel import Session

from app.core.exceptions import AppException
from app.core.security import ADMIN_COOKIE_NAME, decode_admin_token
from app.db.session import get_session
from app.repositories.admin_repository import AdminRepository
from app.repositories.platform_repository import PlatformRepository
from app.services.platform_service import PlatformService


def get_current_admin(
    admin_access_token: str | None = Cookie(default=None, alias=ADMIN_COOKIE_NAME),
    session: Session = Depends(get_session),
):
    if not admin_access_token:
        raise AppException(
            code="UNAUTHORIZED",
            message="Missing or invalid authentication token.",
            status_code=401,
            details={},
        )

    payload = decode_admin_token(admin_access_token)
    admin_id = payload.get("sub")

    if not admin_id:
        raise AppException(
            code="UNAUTHORIZED",
            message="Missing or invalid authentication token.",
            status_code=401,
            details={},
        )

    admin = AdminRepository(session).get_by_id(int(admin_id))

    if not admin or not admin.is_active:
        raise AppException(
            code="UNAUTHORIZED",
            message="Missing or invalid authentication token.",
            status_code=401,
            details={},
        )

    return admin


def get_platform_service(
    session: Session = Depends(get_session),
) -> PlatformService:
    return PlatformService(PlatformRepository(session))

