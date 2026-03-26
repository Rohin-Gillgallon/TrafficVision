# 🚦 TrafficVision: Real-Time AI Traffic Monitoring

[![CI](https://github.com/rohin/TrafficVision/actions/workflows/ci.yml/badge.svg)](https://github.com/rohin/TrafficVision/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)
![YOLOv8](https://img.shields.io/badge/YOLO-v8-orange.svg)

TrafficVision is a high-performance traffic analysis system that leverages TfL (Transport for London) JamCams and YOLOv8 computer vision to provide real-time vehicle counts and monitoring across London's road network.

---

## 🏗️ Architecture

TrafficVision is built with a distributed, event-driven architecture designed for high throughput and low-latency visualization.

- **Data Ingestion**: Celery Beat schedules periodic polling of the TfL API.
- **Processing Pipeline**: Celery Workers fetch camera streams, execute YOLOv8 inference, and count vehicle classes.
- **Storage Layer**: PostgreSQL with PostGIS handles spatial queries and historical detection metadata.
- **API Engine**: FastAPI provides a robust, auto-documented interface for the frontend.
- **Frontend Dashboard**: A modern React (Vite) interface with real-time updates and interactive HUD.

---

## 🚀 One-Command Setup

Get the entire stack (API, Frontend, Workers, Redis, DB) running in seconds.

### 1. Start Orchestration
```bash
docker compose up -d
```

### 2. Initialize Database
Once the containers are running, initialize the schema and seed initial camera metadata:
```bash
python -c "import asyncio; from src.db.crud import init_db; asyncio.run(init_db())"
```

### 3. Access Dashboard
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Metrics**: http://localhost:8000/metrics

---

## 📡 API Endpoints

The API is fully compliant with OpenAPI specs. Below are common usage examples:

### Camera Registry
**Get all monitors and their current statistics:**
```bash
curl http://localhost:8000/cameras/
```

**Get top 50 busiest junctions:**
```bash
curl http://localhost:8000/cameras/busiest?limit=50
```

### Real-Time Data
**Get latest 20 detections for a specific camera:**
```bash
curl http://localhost:8000/cameras/JamCam_00001.04250/latest
```

### Historical Analysis
**Query historical data within a time range:**
```bash
curl "http://localhost:8000/cameras/JamCam_00001.04250/history?since=2024-03-26T00:00:00&until=2024-03-27T00:00:00"
```

---

## 🛠️ Technology Choices

| Technology | Reasoning |
| :--- | :--- |
| **FastAPI** | Selected for its superior performance, native async support, and automatic OpenAPI/Swagger generation. |
| **YOLOv8** | The industry standard for real-time object detection, offering the best balance of speed and accuracy for vehicle identification. |
| **Celery + Redis** | Provides a robust, distributed task queue capable of handling high-frequency polling and heavy vision processing without blocking the API. |
| **PostgreSQL + PostGIS** | Relational excellence combined with spatial capabilities, allowing us to map camera locations and query based on geographical proximity. |
| **React + Vite** | High-velocity frontend development with a minimal footprint and lightning-fast HMR (Hot Module Replacement). |

---

## 🧪 Testing & Quality

We maintain high standards through automated CI/CD:

```bash
# Run linting
ruff check src/

# Run formatting
black --check src/

# Run test suite
pytest tests/
```
