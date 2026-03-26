from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    tfl_api_key: str
    database_url: str
    redis_url: str
    poll_interval_seconds: int = 300
    yolo_model: str = "yolov8n.pt"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # This allows TFL_API_KEY to map to tfl_api_key
        extra="ignore",
    )


settings = Settings()
