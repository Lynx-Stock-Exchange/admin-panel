from fastapi import APIRouter, Depends

from app.api.deps import get_current_admin
from app.dtos.seed import SeedRequest, SeedResultResponse
from app.services.seed_service import seed_service

router = APIRouter(dependencies=[Depends(get_current_admin)])


@router.post("", response_model=SeedResultResponse, status_code=201)
def apply_seed(request: SeedRequest):
    return seed_service.apply(request)