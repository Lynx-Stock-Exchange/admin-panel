from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from app.api.router import api_router
from app.core.config import settings
from app.core.error_handler import register_error_handlers
from app.core.security import pwd_context
from app.db.session import create_db_and_tables, engine
from app.models.admin import Admin
from app.models.platform import Platform

DEV_PLATFORM_NAME = "Broker Local Dev"
DEV_PLATFORM_API_KEY = "test-key"
DEV_PLATFORM_API_SECRET = "test-secret"


def ensure_dev_platform(session: Session) -> None:
    platform = session.exec(
        select(Platform).where(Platform.api_key == DEV_PLATFORM_API_KEY)
    ).first()
    secret_hash = pwd_context.hash(DEV_PLATFORM_API_SECRET)

    if platform is None:
        session.add(
            Platform(
                name=DEV_PLATFORM_NAME,
                description="Deterministic local platform for Broker integration",
                api_key=DEV_PLATFORM_API_KEY,
                api_secret_hash=secret_hash,
                is_active=True,
            )
        )
    else:
        platform.name = DEV_PLATFORM_NAME
        platform.description = "Deterministic local platform for Broker integration"
        platform.api_secret_hash = secret_hash
        platform.is_active = True
        platform.revoked_at = None
        session.add(platform)

    session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        if not session.exec(select(Admin)).first():
            session.add(Admin(username="admin", password_hash=pwd_context.hash("admin")))
            session.commit()
        ensure_dev_platform(session)
    yield


app = FastAPI(title="Lynx Admin Panel Backend", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)
app.include_router(api_router)
