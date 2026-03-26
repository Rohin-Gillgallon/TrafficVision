from celery import Celery

from src.core.config import settings

celery_app = Celery(
    "traffic_vision",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["src.worker.poller", "src.worker.detector", "src.worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "poll-tfl-cameras-every-5-minutes": {
            "task": "src.worker.poller.pollTFLCameras",
            "schedule": settings.poll_interval_seconds,
        },
        "cleanup-detections-daily": {
            "task": "src.worker.tasks.cleanup_old_records",
            "schedule": 86400.0,  # 24 hours in seconds
        },
    },
)
