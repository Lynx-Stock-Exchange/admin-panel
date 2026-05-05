from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class Platform(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: str | None = Field(default=None)
    api_key: str = Field(index=True, unique=True)
    api_secret_hash: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    revoked_at: datetime | None = Field(default=None)