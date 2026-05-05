from datetime import datetime
from pydantic import BaseModel, Field


class PlatformCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class PlatformResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    api_key: str
    is_active: bool
    created_at: datetime
    revoked_at: datetime | None = None


class PlatformCreateResponse(BaseModel):
    message: str
    platform: PlatformResponse
    api_secret: str


class PlatformListResponse(BaseModel):
    platforms: list[PlatformResponse]


class PlatformRevokeResponse(BaseModel):
    message: str
    platform: PlatformResponse


class InternalPlatformResponse(BaseModel):
    id: int
    name: str
    api_key: str
    api_secret_hash: str
    is_active: bool


class InternalActivePlatformsResponse(BaseModel):
    platforms: list[InternalPlatformResponse]


class PlatformVerifyRequest(BaseModel):
    api_key: str = Field(min_length=1)
    api_secret: str = Field(min_length=1)


class PlatformVerifyResponse(BaseModel):
    valid: bool
    platform_id: str | None = None
    platform_name: str | None = None