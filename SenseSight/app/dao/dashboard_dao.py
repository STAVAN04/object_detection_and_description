from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.vo import admin_vo
from app.utils.auth_utils import get_hashed_password


class DashboardDAO:
    def __init__(self, db: Session):
        self.db = db

    def edit_profile(self, admin_id: int, admin_data) -> admin_vo.Admin:
        get_admin = self.db.query(admin_vo.Admin).filter(admin_vo.Admin.id == admin_id).first()

        if not get_admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if not any([admin_data.name, admin_data.email, admin_data.newPassword]):
            return get_admin

        if admin_data.name:
            get_admin.name = admin_data.name
        if admin_data.email:
            get_admin.email = admin_data.email
        if admin_data.newPassword:
            get_admin.password = get_hashed_password(admin_data.newPassword)

        self.db.commit()
        self.db.refresh(get_admin)

        return get_admin
