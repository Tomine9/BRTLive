from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    """Application settings"""

    # App
    APP_NAME: str = "BRT Live API"
    DEBUG: bool = False
    VERSION: str = "1.0.0"

    # Database (sync for Alembic migrations)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://user:password@localhost:5432/brtlive"
    )

    # Async Database (for FastAPI endpoints)
    ASYNC_DATABASE_URL: str = os.getenv(
        "ASYNC_DATABASE_URL",
        "postgresql+asyncpg://user:password@localhost:5432/brtlive"
    )

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8080"]

    # WebSocket
    WS_MESSAGE_QUEUE_SIZE: int = 100
    WS_HEARTBEAT_INTERVAL: int = 30

    # Pagination
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 1000

    # Location tracking
    LOCATION_UPDATE_INTERVAL: int = 10  # seconds
    ACTIVE_BUS_THRESHOLD_MINUTES: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
