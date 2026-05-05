from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class EventTriggerRequest(BaseModel):
    event_type: Literal["BULL_RUN", "BEAR_CRASH", "SECTOR_BOOM", "SECTOR_SLUMP", "STOCK_SHOCK"]
    scope: Literal["MARKET", "SECTOR", "STOCK"]
    target: str | None = Field(default=None, description="Sector name or ticker. Null for MARKET scope.")
    magnitude: float = Field(gt=0, description="Price movement multiplier, e.g. 1.5 = 50% stronger moves.")
    duration_ticks: int = Field(gt=0)
    headline: str = Field(min_length=1, max_length=300)


class EventResponse(BaseModel):
    event_id: str
    event_type: str
    scope: str
    target: str | None = None
    magnitude: float
    duration_ticks: int
    headline: str
    triggered_at: datetime
    triggered_by: Literal["SYSTEM", "ADMIN"]


class EventTriggerResponse(BaseModel):
    message: str
    event: EventResponse


class EventListResponse(BaseModel):
    events: list[EventResponse]