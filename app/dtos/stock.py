from datetime import datetime
from pydantic import BaseModel, Field


class StockCreateRequest(BaseModel):
    ticker: str = Field(min_length=1, max_length=5, pattern=r"^[A-Z]+$")
    name: str = Field(min_length=1, max_length=100)
    sector: str = Field(min_length=1, max_length=50)
    start_price: float = Field(gt=0)
    volatility: float = Field(ge=0, le=1)
    trend_bias: float
    event_weight: float = Field(ge=0)
    momentum: float = Field(ge=0, le=1)


class StockSeedRequest(BaseModel):
    stocks: list[StockCreateRequest]


class StockResponse(BaseModel):
    ticker: str
    name: str
    sector: str
    current_price: float
    open_price: float
    high_price: float
    low_price: float
    volume: int
    volatility: float
    trend_bias: float
    event_weight: float
    momentum: float
    listed_at: datetime | None = None


class StockListResponse(BaseModel):
    stocks: list[StockResponse]