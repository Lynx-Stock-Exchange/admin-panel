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


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        if not session.exec(select(Admin)).first():
            session.add(Admin(username="admin", password_hash=pwd_context.hash("admin")))
            session.commit()
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