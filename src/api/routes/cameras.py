from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from src.api.schemas.detection import (
    CameraCreate,
    CameraStats,
)
from src.api.schemas.detection import (
    DetectionResponse as DetectionOut,
)
from src.db.crud import create_camera, get_busiest, get_history, get_latest

router = APIRouter(prefix="/cameras", tags=["cameras"])


@router.get("/", response_model=list[CameraStats])
async def get_all_cameras():
    return await get_busiest(limit=1000)


@router.post("/", response_model=CameraStats)
async def add_camera(cam: CameraCreate):
    try:
        new_cam = await create_camera(
            camera_id=cam.camera_id,
            rsu_id=cam.rsu_id,
            x=cam.x,
            y=cam.y,
            lat=cam.lat,
            lon=cam.lon,
        )
        # Return as part of stats (empty)
        return CameraStats(
            camera_id=new_cam.id,
            lat=new_cam.lat,
            lon=new_cam.lon,
            total_detections=0,
            last_seen=datetime.now(),
            rsu_id=new_cam.rsu_id,
            vehicle_count_30s=0,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{camera_id}")
async def remove_camera(camera_id: str):
    from src.db.crud import delete_camera

    success = await delete_camera(camera_id)
    if not success:
        raise HTTPException(status_code=404, detail="Camera not found")
    return {"status": "success"}


@router.get("/{camera_id}/latest", response_model=list[DetectionOut])
async def get_latest_detections(camera_id: str, limit: int = 20):
    return await get_latest(camera_id, limit)


@router.get("/{camera_id}/history", response_model=list[DetectionOut])
async def detection_history(
    camera_id: str,
    since: datetime = Query(..., description="ISO 8601 start time"),
    until: datetime = Query(..., description="ISO 8601 end time"),
):
    return await get_history(camera_id, since, until)


@router.get("/busiest", response_model=list[CameraStats])
async def get_busiest_cameras(limit: int = 50):
    return await get_busiest(limit)
