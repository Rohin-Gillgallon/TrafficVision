from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from src.api.routes.cameras import router as cameraRouter

app = FastAPI(
    title="TrafficVision API",
    description="Real-time traffic analysis using YOLO and TfL data",
    version="1.0.0",
)

app.include_router(cameraRouter)
Instrumentator().instrument(app).expose(app)


@app.get("/health")
async def health():
    return {"status": "ok"}
