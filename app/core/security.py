from datetime import datetime, timedelta, timezone

from fastapi import Cookie
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import AppException
from app.repositories.admin_repository import admin_repository


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ADMIN_COOKIE_NAME = "admin_access_token"


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def create_admin_access_token(admin: dict) -> str:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=settings.jwt_expire_minutes)

    payload = {
        "sub": admin["id"],
        "username": admin["username"],
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_admin_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError:
        raise AppException(
            code="UNAUTHORIZED",
            message="Missing or invalid authentication token.",
            status_code=401,
            details={},
        )


def get_current_admin(
    admin_access_token: str | None = Cookie(default=None, alias=ADMIN_COOKIE_NAME),
) -> dict:
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

    admin = admin_repository.find_by_id(admin_id)

    if not admin or not admin["is_active"]:
        raise AppException(
            code="UNAUTHORIZED",
            message="Missing or invalid authentication token.",
            status_code=401,
            details={},
        )

    return admin
