from fastapi import APIRouter

from app.api.routes import health_routes, market_routes, platforms_routes

api_router = APIRouter()

api_router.include_router(health_routes.router, tags=["Health"])
api_router.include_router(platforms_routes.router, prefix="/platforms", tags=["Platforms"])
api_router.include_router(market_routes.router, prefix="/market", tags=["Market"])