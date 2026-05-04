from app.data.stub_store import stub_store


class AdminRepository:
    def find_by_username(self, username: str) -> dict | None:
        return stub_store.admins.get(username)

    def find_by_id(self, admin_id: str) -> dict | None:
        for admin in stub_store.admins.values():
            if admin["id"] == admin_id:
                return admin

        return None


admin_repository = AdminRepository()