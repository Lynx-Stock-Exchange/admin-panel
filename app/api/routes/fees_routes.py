from fastapi import APIRouter, Depends

from app.api.deps import get_current_admin
from app.dtos.fee import FeeRateResponse, FeeRateUpdateRequest, RevenueResponse
from app.services.fee_service import fee_service

router = APIRouter(dependencies=[Depends(get_current_admin)])


@router.get("/revenue", response_model=RevenueResponse)
def get_revenue():
    return fee_service.get_revenue()


@router.get("", response_model=FeeRateResponse)
def get_fee_rate():
    return fee_service.get_fee_rate()


@router.put("", response_model=FeeRateResponse)
def update_fee_rate(request: FeeRateUpdateRequest):
    return fee_service.update_fee_rate(request)
