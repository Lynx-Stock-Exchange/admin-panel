from fastapi import APIRouter

from app.schemas.market import (
    MarketActionResponse,
    MarketSpeedUpdateRequest,
    MarketStatusResponse,
)
from app.services.market_service import market_service

router = APIRouter()


@router.get("/status", response_model=MarketStatusResponse)
def get_market_status():
    return market_service.get_status()


@router.post("/open", response_model=MarketActionResponse)
def open_market():
    return {
        "message": "Market opened successfully.",
        "market": market_service.open_market(),
    }


@router.post("/close", response_model=MarketActionResponse)
def close_market():
    return {
        "message": "Market closed successfully.",
        "market": market_service.close_market(),
    }


@router.put("/speed", response_model=MarketActionResponse)
def update_market_speed(request: MarketSpeedUpdateRequest):
    return {
        "message": "Market speed updated successfully.",
        "market": market_service.update_speed(request.multiplier),
    }