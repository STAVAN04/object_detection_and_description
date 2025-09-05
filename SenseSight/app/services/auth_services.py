from app.dao.admin_dao import AdminDao
from app.schemas.admin_schema import CreateAdmin


class AuthServices:
    def __init__(self, db):
        self.admin_dao = AdminDao(db)

    def get_admin_by_id(self, admin_id: int):
        return self.admin_dao.get_admin_by_id(admin_id)

    def authenticate_admin(self, admin_data):
        return self.admin_dao.fetch_admin(admin_data)

    def register_admin(self, admin_data: CreateAdmin):
        return self.admin_dao.create_admin(admin_data)
