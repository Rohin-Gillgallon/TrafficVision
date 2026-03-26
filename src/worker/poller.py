import asyncio

import httpx
from sqlalchemy import select

from src.core.config import settings
from src.db.crud import get_session
from src.db.models import Camera
from src.worker.celery_app import celery_app
from src.worker.detector import run_detection


@celery_app.task
def pollTFLCameras() -> None:
    # 1. Get IDs of cameras we actually care about (RSUs + manually added)
    async def get_target_map():
        async with get_session() as session:
            # We need the custom ID (piccadilly) and the TFL ID (JamCams_xxx)
            res = await session.execute(select(Camera.id, Camera.tfl_id))
            return {r[1]: r[0] for r in res.all() if r[1]}

    tfl_map = asyncio.run(get_target_map())
    if not tfl_map:
        return

    url = "https://api.tfl.gov.uk/Place/Type/JamCam"
    params = {"app_key": settings.tfl_api_key}

    with httpx.Client(timeout=15) as client:
        resp = client.get(url, params=params)
        resp.raise_for_status()
        all_cameras = resp.json()

    # 2. Only run detection for cameras in our database map
    for cam in all_cameras:
        if cam["id"] in tfl_map:
            custom_id = tfl_map[cam["id"]]
            imageURL = next(
                (
                    p["value"]
                    for p in cam["additionalProperties"]
                    if p["key"] == "imageUrl"
                ),
                None,
            )
            if imageURL:
                run_detection.delay(custom_id, imageURL, cam["lat"], cam["lon"])
