from fastapi import APIRouter, Depends

from app.api.deps import get_current_admin
from app.dtos.option import OptionCreateRequest, OptionListResponse, OptionResponse
from app.services.option_service import option_service

router = APIRouter(dependencies=[Depends(get_current_admin)])


@router.get("", response_model=OptionListResponse)
def list_options():
    return {"options": option_service.list_options()}


@router.post("", response_model=OptionResponse, status_code=201)
def create_option(request: OptionCreateRequest):
    return option_service.create_option(request)