from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class OptionCreateRequest(BaseModel):
    underlying_ticker: str = Field(min_length=1, max_length=5)
    option_type: Literal["CALL", "PUT"]
    strike_price: float = Field(gt=0)
    expiry_time: datetime
    initial_premium: float = Field(gt=0)


class OptionResponse(BaseModel):
    option_id: str
    underlying_ticker: str
    option_type: str
    strike_price: float
    expiry_time: datetime
    premium: float
    is_active: bool
    auto_exercise: bool = True


class OptionListResponse(BaseModel):
    options: list[OptionResponse]