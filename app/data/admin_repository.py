from sqlmodel import Session, select
from typing import Optional
from app.domain.admin import Admin
from app.data.base_repository import BaseRepository

class AdminRepository(BaseRepository[Admin]):
    def __init__(self, session: Session):
        super().__init__(Admin, session)

    def find_by_username(self, username: str) -> Optional[Admin]:
        statement = select(Admin).where(Admin.username == username)
        return self.session.exec(statement).first()

    def find_by_email(self, email: str) -> Optional[Admin]:
        statement = select(Admin).where(Admin.email == email)
        return self.session.exec(statement).first()
