import asyncio
from sqlalchemy import select, func
from src.db.crud import AsyncSessionLocal
from src.db.models import Detection, Camera


async def diagnostics():
    async with AsyncSessionLocal() as session:
        # Check Camera table
        res_cam = await session.execute(select(func.count(Camera.id)))
        print(f"Total in Camera table: {res_cam.scalar()}")

        # Check Detection table
        res_det = await session.execute(select(func.count(Detection.id)))
        print(f"Total in Detection table: {res_det.scalar()}")

        # Test the query components
        from src.db.crud import get_busiest

        try:
            stats = await get_busiest(limit=10)
            print(f"get_busiest returned {len(stats)} results")
            for s in stats:
                print(
                    f" - {s['camera_id']} ({s.get('rsu_id')}): {s['total_detections']} detections"
                )
        except Exception as e:
            print(f"Error in get_busiest: {e}")


if __name__ == "__main__":
    asyncio.run(diagnostics())
