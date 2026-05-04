from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel

class Platform(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    api_key: str = Field(index=True, unique=True)
    api_secret: str  # hashed
    is_active: bool = Field(default=True)
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
