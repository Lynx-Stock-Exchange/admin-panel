from sqlmodel import Session, select

from app.db.base_repository import BaseRepository
from app.models.admin import Admin


class AdminRepository(BaseRepository[Admin]):
    def __init__(self, session: Session):
        super().__init__(Admin, session)

    def find_by_username(self, username: str) -> Admin | None:
        statement = select(Admin).where(Admin.username == username)
        return self.session.exec(statement).first()