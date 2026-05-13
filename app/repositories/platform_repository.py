from datetime import datetime, timezone

from sqlmodel import Session, select

from app.db.base_repository import BaseRepository
from app.models.platform import Platform


class PlatformRepository(BaseRepository[Platform]):
    def __init__(self, session: Session):
        super().__init__(Platform, session)

    def find_by_name(self, name: str) -> Platform | None:
        statement = select(Platform).where(Platform.name == name)
        return self.session.exec(statement).first()

    def find_by_api_key(self, api_key: str) -> Platform | None:
        statement = select(Platform).where(Platform.api_key == api_key)
        return self.session.exec(statement).first()

    def find_active(self) -> list[Platform]:
        statement = select(Platform).where(Platform.is_active == True)
        return list(self.session.exec(statement).all())

    def revoke(self, platform: Platform) -> Platform:
        platform.is_active = False
        platform.revoked_at = datetime.now(timezone.utc)
        return self.update(platform)