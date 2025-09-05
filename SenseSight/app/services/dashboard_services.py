from app.dao.dashboard_dao import DashboardDAO
from app.schemas.dashboard_schema import UpdateProfile


class DashboardServices:
    def __init__(self, db):
        self.dashboard_dao = DashboardDAO(db)

    def admin_update_profile(self, admin_id: int, admin_data: UpdateProfile):
        return self.dashboard_dao.edit_profile(admin_id, admin_data)
