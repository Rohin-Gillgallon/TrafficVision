import httpx
from ultralytics import YOLO

from src.core.config import settings
from src.db.crud import save_detections
from src.worker.celery_app import celery_app

model = YOLO(settings.yolo_model)


def detect_vehicles(image_bytes: bytes) -> list[dict]:
    import io

    from PIL import Image

    img = Image.open(io.BytesIO(image_bytes))
    # Extremely sensitive threshold for low-res JamCams
    results = model.predict(img, conf=0.05, iou=0.45, imgsz=640)

    detections = []
    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            # Cars, motorcycles, buses, and trucks only.
            if label in ["car", "motorcycle", "bus", "truck"]:
                detections.append(
                    {
                        "class": label,
                        "confidence": float(box.conf[0]),
                        "bbox": box.xyxy[0].tolist(),
                    }
                )
    return detections


@celery_app.task(name="src.worker.detector.run_detection")
def run_detection(camera_id: str, image_url: str, lat: float, lon: float) -> None:
    if not image_url or not image_url.startswith("http"):
        print(f"Skipping invalid image URL for {camera_id}: {image_url}")
        return

    import asyncio

    with httpx.Client(timeout=10) as client:
        resp = client.get(image_url)
        resp.raise_for_status()
        image_bytes = resp.content

    detections = detect_vehicles(image_bytes)
    asyncio.run(save_detections(camera_id, lat, lon, detections, image_url=image_url))
