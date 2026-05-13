from datetime import datetime
from pydantic import BaseModel, Field


class MarketStatusResponse(BaseModel):
    is_open: bool
    market_time: datetime
    real_time: datetime
    speed_multiplier: int
    active_event: dict | None = None


class MarketSpeedUpdateRequest(BaseModel):
    multiplier: int = Field(ge=1, le=360)


class MarketActionResponse(BaseModel):
    message: str
    market: MarketStatusResponse