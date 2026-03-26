# scripts/test_detection.py
import asyncio
import httpx
from src.worker.detector import detect_vehicles
from src.db.crud import save_detections
from src.core.config import settings


async def main():
    # Grab one real TfL camera frame
    url = "https://api.tfl.gov.uk/Place/Type/JamCam"
    async with httpx.AsyncClient() as client:
        cams = (await client.get(url, params={"app_key": settings.tfl_api_key})).json()

    cam = cams[0]
    image_url = next(
        (p["value"] for p in cam["additionalProperties"] if p["key"] == "imageUrl"),
        None,
    )
    if not image_url:
        image_url = cam["additionalProperties"][0]["value"]

    print(f"Cam ID: {cam['id']}, Lat: {cam['lat']}, Lon: {cam['lon']}")
    print(f"Fetching image from: {image_url}")

    if not image_url.startswith("http"):
        print(f"Error: Invalid image URL: {image_url}")
        return

    async with httpx.AsyncClient() as client:
        image_bytes = (await client.get(image_url)).content

    detections = detect_vehicles(image_bytes)
    print(f"Found {len(detections)} vehicles: {detections}")

    await save_detections(cam["id"], cam["lat"], cam["lon"], detections)
    print("Saved to DB!")


asyncio.run(main())
