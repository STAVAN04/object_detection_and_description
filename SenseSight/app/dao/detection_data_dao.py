from sqlalchemy.orm import Session
from app.vo.detection_vo import Detection
from datetime import datetime

class DetectionDataDAO:
    def __init__(self, db: Session):
        self.db = db

    def create_detection(self, admin_id: int, detection_json: dict) -> Detection:
        try:
            print(type(detection_json))
            new_detection = Detection(
                id=admin_id,
                detection_json=detection_json,
                created_on=datetime.utcnow(),
                modified_on=datetime.utcnow()
            )
            self.db.add(new_detection)
            self.db.commit()
            self.db.refresh(new_detection)
            return new_detection
        except Exception as e:
            self.db.rollback()
            raise e

    def get_detections_by_admin(self, admin_id: int) -> list[Detection]:
        return self.db.query(Detection).filter(
            Detection.id == admin_id,
            Detection.is_deleted == False
        ).order_by(Detection.created_on.desc()).all()