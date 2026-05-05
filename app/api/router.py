from fastapi import APIRouter

from app.api.routes import (
    auth_routes,
    events_routes,
    fees_routes,
    health_routes,
    internal_platforms_routes,
    market_routes,
    options_routes,
    platforms_routes,
    stocks_routes,
)

api_router = APIRouter()

api_router.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
api_router.include_router(health_routes.router, prefix="/api/admin", tags=["Health"])
api_router.include_router(platforms_routes.router, prefix="/api/admin/platforms", tags=["Platforms"])
api_router.include_router(market_routes.router, prefix="/api/admin/market", tags=["Market"])
api_router.include_router(stocks_routes.router, prefix="/api/admin/stocks", tags=["Stocks"])
api_router.include_router(options_routes.router, prefix="/api/admin/options", tags=["Options"])
api_router.include_router(events_routes.router, prefix="/api/admin/events", tags=["Events"])
api_router.include_router(fees_routes.router, prefix="/api/admin/fees", tags=["Fees"])

api_router.include_router(
    internal_platforms_routes.router,
    prefix="/internal",
    tags=["Internal Platforms"],
)