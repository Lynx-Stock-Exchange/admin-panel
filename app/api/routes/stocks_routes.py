from fastapi import APIRouter, Depends

from app.api.deps import get_current_admin
from app.dtos.common import MessageResponse
from app.dtos.stock import StockCreateRequest, StockListResponse, StockResponse, StockSeedRequest
from app.services.stock_service import stock_service

router = APIRouter(dependencies=[Depends(get_current_admin)])


@router.get("", response_model=StockListResponse)
def list_stocks():
    return {"stocks": stock_service.list_stocks()}


@router.post("", response_model=StockResponse, status_code=201)
def create_stock(request: StockCreateRequest):
    return stock_service.create_stock(request)


@router.post("/seed", response_model=StockListResponse, status_code=201)
def seed_stocks(request: StockSeedRequest):
    return {"stocks": stock_service.seed_stocks(request.stocks)}