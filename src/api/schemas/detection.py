from pydantic import BaseModel, Field
from datetime import datetime


class DetectionResponse(BaseModel):
    id: str
    camera_id: str
    lat: float
    lon: float
    vehicle_class: str
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: list[float]
    detected_at: datetime
    image_url: str | None = None
    model_config = {"from_attributes": True}


class CameraStats(BaseModel):
    camera_id: str
    name: str | None = None
    tfl_id: str | None = None
    lat: float
    lon: float
    total_detections: int
    last_seen: datetime | None = None
    image_url: str | None = None
    rsu_id: str | None = None
    vehicle_count_30s: int = 0


class CameraCreate(BaseModel):
    camera_id: str
    name: str | None = None
    tfl_id: str | None = None
    rsu_id: str
    x: float
    y: float
    lat: float
    lon: float
