from fastapi import APIRouter, Depends, Response
from sqlmodel import Session

from app.core.config import settings
from app.core.security import ADMIN_COOKIE_NAME
from app.db.session import get_session
from app.repositories.admin_repository import AdminRepository
from app.dtos.auth import LoginRequest, LoginResponse, MeResponse
from app.services.auth_service import AuthService
from app.api.deps import get_current_admin

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, response: Response, session: Session = Depends(get_session)):
    auth_service = AuthService(AdminRepository(session))
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
            "id": str(admin.id),
            "username": admin.username,
            "is_active": admin.is_active,
        },
    }


@router.get("/me", response_model=MeResponse)
def me(current_admin=Depends(get_current_admin)):
    return {
        "admin": {
            "id": str(current_admin.id),
            "username": current_admin.username,
            "is_active": current_admin.is_active,
        }
    }


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key=ADMIN_COOKIE_NAME, path="/")
    return {"message": "Admin logged out successfully."}