from datetime import datetime
from pydantic import BaseModel, Field


class FeeRateUpdateRequest(BaseModel):
    rate: float = Field(gt=0, lt=1, description="Fee rate as decimal, e.g. 0.001 = 0.1%")


class FeeRateResponse(BaseModel):
    fee_rate: float
    message: str


class OrderFeeRecord(BaseModel):
    order_id: str
    platform_id: str
    platform_user_id: str
    instrument_type: str
    instrument_id: str
    side: str
    filled_quantity: int
    average_fill_price: float
    exchange_fee: float
    status: str
    created_at: datetime


class RevenueResponse(BaseModel):
    fee_rate: float
    total_revenue: float
    filled_order_count: int
    orders: list[OrderFeeRecord]