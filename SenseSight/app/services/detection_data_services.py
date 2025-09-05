import json
from typing import Dict
from app.dao.detection_data_dao import DetectionDataDAO
from app.vo.detection_vo import Detection


class DataFetchStoreHistoryService:
    def __init__(self, db):
        self.detection_dao = DetectionDataDAO(db)

    def store_detection_data(self, admin_id: int, detection_data: dict) -> Detection:
        json_data = json.dumps(detection_data)
        return self.detection_dao.create_detection(admin_id, json_data)

    def fetch_detection_history(self, admin_id: int) -> Dict[str, int]:
        detections = self.detection_dao.get_detections_by_admin(admin_id)
        object_counts = {}
        for detection in detections:
            if detection.detection_json:
                try:
                    data = json.loads(detection.detection_json)
                    for obj, count in data.get('object_count').items():
                        object_counts[obj] = object_counts.get(obj, 0) + count
                except json.JSONDecodeError:
                    continue

        return object_counts