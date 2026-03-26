# src/db/crud.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, and_, func, desc
import sqlalchemy
from datetime import datetime, timedelta
from uuid import uuid4
from src.db.models import Base, Detection, Camera
from sqlalchemy.pool import NullPool
from src.core.config import settings
from contextlib import asynccontextmanager
from typing import AsyncGenerator

engine = create_async_engine(
    settings.database_url,
    echo=False,
    poolclass=NullPool,  # Disable pooling to avoid issues with repeated asyncio.run calls
)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def save_detections(
    camera_id: str,
    lat: float,
    lon: float,
    detections: list[dict],
    frame_key: str | None = None,
    image_url: str | None = None,
    simtime: float | None = None,
) -> None:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Ensure camera exists in metadata table if it has coords
            res = await session.execute(select(Camera).where(Camera.id == camera_id))
            if not res.scalar():
                session.add(
                    Camera(
                        id=camera_id,
                        rsu_id=camera_id.replace("JamCams_", ""),
                        tfl_id=camera_id if camera_id.startswith("JamCams") else None,
                        x=0.0,
                        y=0.0,
                        lat=lat,
                        lon=lon,
                    )
                )

            if not detections:
                session.add(
                    Detection(
                        id=str(uuid4()),
                        camera_id=camera_id,
                        lat=lat,
                        lon=lon,
                        vehicle_class="none",
                        confidence=0.0,
                        bbox=[0, 0, 0, 0],
                        image_url=image_url,
                        simtime=simtime or datetime.now().timestamp(),
                    )
                )
            else:
                for d in detections:
                    session.add(
                        Detection(
                            id=str(uuid4()),
                            camera_id=camera_id,
                            lat=lat,
                            lon=lon,
                            vehicle_class=d.get("class", "unknown"),
                            confidence=d.get("confidence", 1.0),
                            bbox=d.get("bbox", []),
                            frame_key=frame_key,
                            image_url=image_url,
                            simtime=simtime or datetime.now().timestamp(),
                        )
                    )


async def create_camera(
    camera_id: str,
    rsu_id: str,
    x: float,
    y: float,
    lat: float,
    lon: float,
    name: str | None = None,
    tfl_id: str | None = None,
) -> Camera:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Check if exists
            res = await session.execute(select(Camera).where(Camera.id == camera_id))
            existing = res.scalar()
            if existing:
                existing.rsu_id = rsu_id
                existing.name = name
                existing.tfl_id = tfl_id
                existing.x = x
                existing.y = y
                existing.lat = lat
                existing.lon = lon
                return existing

            cam = Camera(
                id=camera_id,
                rsu_id=rsu_id,
                name=name,
                tfl_id=tfl_id,
                x=x,
                y=y,
                lat=lat,
                lon=lon,
            )
            session.add(cam)
            return cam


async def get_busiest(limit: int = 50) -> list[dict]:
    async with AsyncSessionLocal() as session:
        # Create a subquery to get the latest NON-NULL image_url for each camera
        latest_image_subquery = (
            select(
                Detection.camera_id,
                Detection.image_url,
                func.row_number()
                .over(
                    partition_by=Detection.camera_id,
                    order_by=Detection.detected_at.desc(),
                )
                .label("rn"),
            )
            .where(Detection.image_url.isnot(None))
            .subquery()
        )

        thirty_secs_ago = datetime.now() - timedelta(seconds=30)

        # Subquery for 30-second vehicle count
        count_30s_subquery = (
            select(Detection.camera_id, func.count(Detection.id).label("count_30s"))
            .where(Detection.detected_at >= thirty_secs_ago)
            .group_by(Detection.camera_id)
            .subquery()
        )

        # Base query from Camera table to ensure all registered cameras are shown
        result = await session.execute(
            select(
                Camera.id.label("camera_id"),
                Camera.name,
                Camera.tfl_id,
                Camera.lat,
                Camera.lon,
                Camera.rsu_id,
                func.count(Detection.id).label("total_detections"),
                func.max(Detection.detected_at).label("last_seen"),
                latest_image_subquery.c.image_url,
                func.coalesce(count_30s_subquery.c.count_30s, 0).label(
                    "vehicle_count_30s"
                ),
            )
            .outerjoin(Detection, Camera.id == Detection.camera_id)
            .outerjoin(
                latest_image_subquery,
                and_(
                    Camera.id == latest_image_subquery.c.camera_id,
                    latest_image_subquery.c.rn == 1,
                ),
            )
            .outerjoin(count_30s_subquery, Camera.id == count_30s_subquery.c.camera_id)
            .group_by(
                Camera.id,
                Camera.name,
                Camera.tfl_id,
                Camera.lat,
                Camera.lon,
                Camera.rsu_id,
                latest_image_subquery.c.image_url,
                count_30s_subquery.c.count_30s,
            )
            .order_by(desc("total_detections"), Camera.id)
            .limit(limit)
        )
        return [row._asdict() for row in result.all()]


async def get_latest(camera_id: str, limit: int = 20) -> list[Detection]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Detection)
            .where(Detection.camera_id == camera_id)
            .order_by(Detection.detected_at.desc())
            .limit(limit)
        )
        data = result.scalars().all()
        return data  # Explicit return


async def get_history(
    camera_id: str, since: datetime, until: datetime
) -> list[Detection]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Detection)
            .where(
                and_(
                    Detection.camera_id == camera_id,
                    Detection.detected_at >= since,
                    Detection.detected_at <= until,
                )
            )
            .order_by(Detection.detected_at.desc())
        )
        return result.scalars().all()


async def delete_camera(camera_id: str) -> bool:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await session.execute(
                sqlalchemy.delete(Camera).where(Camera.id == camera_id)
            )
            await session.execute(
                sqlalchemy.delete(Detection).where(Detection.camera_id == camera_id)
            )
            return True


async def delete_old_detections(days: int = 7) -> int:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            cutoff = datetime.now() - timedelta(days=days)
            result = await session.execute(
                sqlalchemy.delete(Detection).where(Detection.detected_at < cutoff)
            )
            return result.rowcount


async def get_latest_with_elapsed(camera_id: str):
    async with AsyncSessionLocal() as session:
        earliest = func.min(Detection.simtime).over()
        elapsed_col = (Detection.simtime - earliest).label("elapsed_seconds")
        query = select(Detection, elapsed_col).where(Detection.camera_id == camera_id)
        result = await session.execute(query)

        return [{"data": row[0], "elapsed": row[1]} for row in result.all()]
