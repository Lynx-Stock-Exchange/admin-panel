from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class SeedExchangeConfig(BaseModel):
    fee_rate: float = Field(gt=0, lt=1)
    market_open_time: str = "09:00"
    market_close_time: str = "17:00"
    default_tick_interval_ms: int = Field(default=1000, gt=0)
    default_speed_multiplier: int = Field(default=60, ge=1, le=360)


class SeedStockEntry(BaseModel):
    ticker: str = Field(min_length=1, max_length=5, pattern=r"^[A-Z]+$")
    name: str
    sector: str
    start_price: float = Field(gt=0)
    volatility: float = Field(ge=0, le=1)
    trend_bias: float
    event_weight: float = Field(ge=0)
    momentum: float = Field(ge=0, le=1)


class SeedOptionEntry(BaseModel):
    underlying_ticker: str = Field(min_length=1, max_length=5)
    option_type: Literal["CALL", "PUT"]
    strike_price: float = Field(gt=0)
    expiry_time: datetime
    initial_premium: float = Field(gt=0)


class SeedEventDefinition(BaseModel):
    event_type: Literal["BULL_RUN", "BEAR_CRASH", "SECTOR_BOOM", "SECTOR_SLUMP", "STOCK_SHOCK"]
    scope: Literal["MARKET", "SECTOR", "STOCK"]
    target: str | None = None
    magnitude: float = Field(gt=0)
    duration_ticks: int = Field(gt=0)
    weight: float = Field(gt=0)


class SeedEventsConfig(BaseModel):
    auto_trigger_enabled: bool = True
    auto_trigger_probability_per_tick: float = Field(default=0.005, ge=0, le=1)
    definitions: list[SeedEventDefinition] = []
    headlines: dict[str, list[str]] = {}


class SeedRequest(BaseModel):
    exchange: SeedExchangeConfig
    stocks: list[SeedStockEntry] = []
    options: list[SeedOptionEntry] = []
    events: SeedEventsConfig | None = None


class SeedResultResponse(BaseModel):
    message: str
    fee_rate: float
    speed_multiplier: int
    stocks_seeded: int
    options_seeded: int
    event_definitions_loaded: int