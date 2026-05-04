from fastapi import APIRouter, Depends, Response

from app.core.config import settings
from app.core.security import ADMIN_COOKIE_NAME, get_current_admin
from app.schemas.auth import LoginRequest, LoginResponse, MeResponse
from app.services.auth_service import auth_service

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, response: Response):
    admin, token = auth_service.login(request.username, request.password)

    response.set_cookie(
        key=ADMIN_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.secure_cookies,
        samesite="lax",
        max_age=settings.jwt_expire_minutes * 60,
        path="/",
    )

    return {
        "message": "Admin logged in successfully.",
        "admin": {
            "id": admin["id"],
            "username": admin["username"],
            "is_active": admin["is_active"],
        },
    }


@router.get("/me", response_model=MeResponse)
def me(current_admin: dict = Depends(get_current_admin)):
    return {
        "admin": {
            "id": current_admin["id"],
            "username": current_admin["username"],
            "is_active": current_admin["is_active"],
        }
    }


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(
        key=ADMIN_COOKIE_NAME,
        path="/",
    )

    return {
        "message": "Admin logged out successfully."
    }