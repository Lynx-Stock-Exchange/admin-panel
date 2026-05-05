from fastapi import APIRouter, Depends

from app.api.deps import get_current_admin, get_platform_service
from app.dtos.platform import (
    PlatformCreateRequest,
    PlatformCreateResponse,
    PlatformListResponse,
    PlatformRevokeResponse,
)
from app.services.platform_service import PlatformService

router = APIRouter(dependencies=[Depends(get_current_admin)])


@router.get("", response_model=PlatformListResponse)
def list_platforms(platform_service: PlatformService = Depends(get_platform_service)):
    return {
        "platforms": platform_service.list_platforms()
    }


@router.post("", response_model=PlatformCreateResponse, status_code=201)
def create_platform(
    request: PlatformCreateRequest,
    platform_service: PlatformService = Depends(get_platform_service),
):
    platform, api_secret = platform_service.create_platform(
        name=request.name,
        description=request.description,
    )

    return {
        "message": "Platform registered successfully.",
        "platform": platform,
        "api_secret": api_secret,
    }


@router.delete("/{platform_id}", response_model=PlatformRevokeResponse)
def revoke_platform(
    platform_id: str,
    platform_service: PlatformService = Depends(get_platform_service),
):
    platform = platform_service.revoke_platform(platform_id)

    return {
        "message": "Platform revoked successfully.",
        "platform": platform,
    }