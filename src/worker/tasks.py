import asyncio

from src.db.crud import delete_old_detections
from src.worker.celery_app import celery_app


@celery_app.task(name="src.worker.tasks.cleanup_old_records")
def cleanup_old_records():
    """Delete detections older than 7 days."""
    count = asyncio.run(delete_old_detections(days=7))
    print(f"Cleanup complete: Deleted {count} records older than 7 days.")
    return count
