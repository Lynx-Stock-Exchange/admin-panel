from fastapi import APIRouter

from app.schemas.platform import (
    InternalActivePlatformsResponse,
    PlatformVerifyRequest,
    PlatformVerifyResponse,
)
from app.services.platform_service import platform_service

router = APIRouter()


@router.get("/platforms/active", response_model=InternalActivePlatformsResponse)
def list_active_platforms():
    return {
        "platforms": platform_service.list_active_platforms_internal()
    }


@router.post("/platforms/verify", response_model=PlatformVerifyResponse)
def verify_platform(request: PlatformVerifyRequest):
    return platform_service.verify_platform_credentials(
        api_key=request.api_key,
        api_secret=request.api_secret,
    )