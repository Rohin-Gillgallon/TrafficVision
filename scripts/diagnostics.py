import asyncio
from sqlalchemy import select, func
from src.db.crud import AsyncSessionLocal
from src.db.models import Detection


async def diagnostics():
    async with AsyncSessionLocal() as session:
        # Count unique cameras
        res_cnt = await session.execute(
            select(func.count(func.distinct(Detection.camera_id)))
        )
        unique_cams = res_cnt.scalar()
        print(f"Total Unique Cameras in DB: {unique_cams}")

        # Count detections with images
        res_img = await session.execute(
            select(func.count(Detection.id)).where(Detection.image_url.isnot(None))
        )
        img_cnt = res_img.scalar()
        print(f"Detections with image_url: {img_cnt}")

        # Sample latest camera with image
        res_sample = await session.execute(
            select(Detection.camera_id, Detection.image_url)
            .where(Detection.image_url.isnot(None))
            .order_by(Detection.detected_at.desc())
            .limit(5)
        )
        print("\nLatest detections with images:")
        for row in res_sample.all():
            print(f" - {row.camera_id}: {row.image_url}")


if __name__ == "__main__":
    asyncio.run(diagnostics())
