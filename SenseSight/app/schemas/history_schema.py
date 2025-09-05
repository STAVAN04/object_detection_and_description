from pydantic import BaseModel
from typing import Optional


class DetectionCreate(BaseModel):
    id: int
    input_video: str
    output_video: Optional[str] = None
    detection_json: dict


class ObjectCountSchema(BaseModel):
    object_count: dict