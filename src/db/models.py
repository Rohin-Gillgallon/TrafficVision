from sqlalchemy import Column, String, Float, JSON, DateTime, func
from sqlalchemy.orm import DeclarativeBase
from uuid import uuid4
import time


class Base(DeclarativeBase):
    pass


class Camera(Base):
    __tablename__ = "cameras"
    id = Column(String, primary_key=True)
    tfl_id = Column(String(100), nullable=True, index=True)
    name = Column(String(200), nullable=True)
    rsu_id = Column(String(100), nullable=False)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    # last_sync or simtime (real-time)
    simtime = Column(Float, default=lambda: time.time())


class Detection(Base):
    __tablename__ = "detections"
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    camera_id = Column(String, index=True, nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    detected_at = Column(DateTime, server_default=func.now(), index=True)
    vehicle_class = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    bbox = Column(JSON, nullable=False)
    frame_key = Column(String, nullable=True)
    image_url = Column(String, nullable=True)

    # Simulation fields (optional override)
    simtime = Column(Float, default=lambda: time.time())
