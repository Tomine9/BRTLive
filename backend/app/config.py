from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/brtlive"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # App Settings
    APP_NAME: str = "BRTLive"
    DEBUG: bool = False
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # External APIs
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    SMS_API_KEY: Optional[str] = None
    
    # Background Tasks
    LOCATION_UPDATE_INTERVAL: int = 30  # seconds
    ETA_CALCULATION_INTERVAL: int = 60  # seconds
    
    class Config:
        env_file = ".env"


settings = Settings()
    