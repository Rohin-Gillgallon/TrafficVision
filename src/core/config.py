from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    tfl_api_key: str
    database_url: str
    redis_url: str
    poll_interval_seconds: int = 300
    yolo_model: str = "yolov8n.pt"

    class Config:
        env_file = ".env"


settings = Settings()
