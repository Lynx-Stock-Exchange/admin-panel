from sqlmodel import Session, select
from typing import Optional
from app.domain.platform import Platform
from app.data.base_repository import BaseRepository

class PlatformRepository(BaseRepository[Platform]):
    def __init__(self, session: Session):
        super().__init__(Platform, session)

    def find_by_api_key(self, api_key: str) -> Optional[Platform]:
        statement = select(Platform).where(Platform.api_key == api_key)
        return self.session.exec(statement).first()

    def get_all_active(self) -> list[Platform]:
        statement = select(Platform).where(Platform.is_active == True)
        return list(self.session.exec(statement).all())
