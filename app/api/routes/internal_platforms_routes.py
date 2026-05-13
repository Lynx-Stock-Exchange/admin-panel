from fastapi import APIRouter
from fastapi import Depends

from app.api.deps import get_platform_service
from app.dtos.platform import (
    InternalActivePlatformsResponse,
    PlatformVerifyRequest,
    PlatformVerifyResponse,
)
from app.services.platform_service import PlatformService

router = APIRouter()


@router.get("/platforms/active", response_model=InternalActivePlatformsResponse)
def list_active_platforms(
    platform_service: PlatformService = Depends(get_platform_service),
):
    return {
        "platforms": platform_service.list_active_platforms_internal()
    }


@router.post("/platforms/verify", response_model=PlatformVerifyResponse)
def verify_platform(
    request: PlatformVerifyRequest,
    platform_service: PlatformService = Depends(get_platform_service),
):
    return platform_service.verify_platform_credentials(
        api_key=request.api_key,
        api_secret=request.api_secret,
    )