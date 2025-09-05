from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.utils.auth_utils import get_hashed_password, verify_password
from app.vo import admin_vo, role_vo


class AdminDao:
    def __init__(self, db: Session):
        self.db = db

    def get_admin_by_id(self, admin_id: int) -> admin_vo.Admin:
        get_by_id = self.db.query(admin_vo.Admin).filter(admin_vo.Admin.id == admin_id).first()
        if not get_by_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return get_by_id

    def fetch_admin(self, admin_data) -> admin_vo.Admin:
        get_admin = self.db.query(admin_vo.Admin).filter(admin_vo.Admin.email == admin_data.username).first()
        if not get_admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        if not get_admin or not verify_password(admin_data.password, get_admin.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Credentials"
            )

        return get_admin

    def create_admin(self, admin_data) -> admin_vo.Admin:
        if not admin_data.email or not admin_data.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Details not provided.",
            )

        check_user_exists = self.db.query(admin_vo.Admin).filter(admin_vo.Admin.email == admin_data.email).first()
        if check_user_exists:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User with {admin_data.email} already exists"
            )

        user_role = self.db.query(role_vo.Role).filter(role_vo.Role.role_type == "user").first()
        if not user_role:
            user_role = role_vo.Role(role_type="user")
            self.db.add(user_role)
            self.db.commit()
            self.db.refresh(user_role)

        hashed_password = get_hashed_password(admin_data.password)
        insert_admin = admin_vo.Admin(name=admin_data.name,
                                      email=admin_data.email,
                                      password=hashed_password,
                                      role_id=user_role.role_id)
        self.db.add(insert_admin)
        self.db.commit()
        self.db.refresh(insert_admin)

        return insert_admin
