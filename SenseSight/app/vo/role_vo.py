from sqlalchemy import Column, Integer, VARCHAR
from sqlalchemy.orm import relationship

from app.config.database import Base


class Role(Base):
    __tablename__ = 'roles'

    role_id = Column("role_id", Integer, primary_key=True, index=True)
    role_type = Column("role_type", VARCHAR(6), unique=True, nullable=False, default="user")

    admin = relationship("Admin", back_populates="role", cascade="all, delete-orphan")
