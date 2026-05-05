from sqlmodel import Session

from app.core.security import pwd_context
from app.db.session import engine
from app.models.admin import Admin
from app.repositories.admin_repository import AdminRepository
from app.repositories.platform_repository import PlatformRepository
from app.services.platform_service import PlatformService

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "changeme123"

PLATFORMS = [
    {"name": "Lynx Alpha", "description": "Primary trading platform"},
    {"name": "Lynx Beta", "description": "Secondary trading platform"},
]


def seed():
    with Session(engine) as session:
        admin_repo = AdminRepository(session)

        if not admin_repo.find_by_username(ADMIN_USERNAME):
            admin = Admin(
                username=ADMIN_USERNAME,
                password_hash=pwd_context.hash(ADMIN_PASSWORD),
            )
            admin_repo.create(admin)
            print(f"Admin created — username: {ADMIN_USERNAME}  password: {ADMIN_PASSWORD}")
        else:
            print(f"Admin '{ADMIN_USERNAME}' already exists, skipping.")

        platform_service = PlatformService(PlatformRepository(session))

        for p in PLATFORMS:
            try:
                platform, plain_secret = platform_service.create_platform(
                    name=p["name"], description=p["description"]
                )
                print(f"\nPlatform created — '{platform.name}'")
                print(f"  api_key:    {platform.api_key}")
                print(f"  api_secret: {plain_secret}  ← save this, it won't be shown again")
            except Exception as e:
                print(f"Platform '{p['name']}' skipped: {e}")


if __name__ == "__main__":
    seed()