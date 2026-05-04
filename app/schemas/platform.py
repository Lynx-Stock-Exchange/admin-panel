from datetime import datetime
from pydantic import BaseModel, Field


class PlatformCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)


class PlatformResponse(BaseModel):
    id: str
    name: str
    api_key: str
    is_active: bool
    created_at: datetime


class PlatformCreateResponse(BaseModel):
    message: str
    platform: PlatformResponse
    api_secret: str


class PlatformListResponse(BaseModel):
    platforms: list[PlatformResponse]