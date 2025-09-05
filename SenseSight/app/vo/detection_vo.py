from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from datetime import datetime

from app.config.database import Base


class Detection(Base):
    __tablename__ = "detections"

    detection_id = Column("detection_id", Integer, primary_key=True, index=True, autoincrement=True)
    id = Column("id", Integer, ForeignKey("admin.id"), nullable=False)
    input_video = Column("input_video", String(255), nullable=True)
    output_video = Column("output_video", String(255), nullable=True)
    detection_json = Column("detection_json", String(255), nullable=True)
    created_on = Column("created_on", DateTime, default=datetime.utcnow)
    modified_on = Column("modified_on", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column("is_deleted", Boolean, default=False)

    admin = relationship("Admin", back_populates="detections")
