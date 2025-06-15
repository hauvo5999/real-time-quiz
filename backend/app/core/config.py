from pydantic_settings import BaseSettings
from typing import Optional, List, Dict, Any
from pathlib import Path
import os

# Get the base directory of the project
BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    # API settings
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Real-Time Quiz API"
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 30 minutes
    
    # Database settings
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5433")
    DB_USER: str = os.getenv("DB_USER", "hauvo")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "hauvo")
    DB_NAME: str = os.getenv("DB_NAME", "real-time-quiz")
    
    # Redis settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    
    # WebSocket settings
    WS_PING_INTERVAL: int = 20000        # 20 seconds
    WS_PING_TIMEOUT: int = 20000         # 20 seconds
    WS_CLOSE_TIMEOUT: int = 5000         # 5 seconds
    WS_MAX_MESSAGE_SIZE: int = 1048576   # 1MB
    
    class Config:
        env_file = os.path.join(BASE_DIR, ".env")
        case_sensitive = True

settings = Settings()

# Tortoise ORM Configuration
TORTOISE_ORM = {
    "connections": {
        "default": f"postgres://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    },
    "apps": {
        "models": {
            "models": [
                # "aerich.models",
                "app.models.user",
                "app.models.quiz",
                "app.models.question",
                "app.models.answer",
                "app.models.answer_attempt",
            ],
            "default_connection": "default",
        }
    }
}

# Redis connection URL
REDIS_URL = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
if settings.REDIS_PASSWORD:
    REDIS_URL = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"

# Redis Pub/Sub settings
REDIS_PUBSUB_HOST: str = os.getenv("REDIS_PUBSUB_HOST", "localhost")
REDIS_PUBSUB_PORT: int = int(os.getenv("REDIS_PUBSUB_PORT", "6380"))
REDIS_PUBSUB_PASSWORD: Optional[str] = os.getenv("REDIS_PUBSUB_PASSWORD", None)
REDIS_PUBSUB_CHANNEL_PREFIX: str = "quiz:"
REDIS_PUBSUB_MAX_LISTENERS: int = 1000
REDIS_PUBSUB_RECONNECT_INTERVAL: int = 5000
REDIS_PUBSUB_RECONNECT_MAX_ATTEMPTS: int = 10

# Redis Pub/Sub connection URL
REDIS_PUBSUB_URL = f"redis://{REDIS_PUBSUB_HOST}:{REDIS_PUBSUB_PORT}/{settings.REDIS_DB}"
if REDIS_PUBSUB_PASSWORD:
    REDIS_PUBSUB_URL = f"redis://:{REDIS_PUBSUB_PASSWORD}@{REDIS_PUBSUB_HOST}:{REDIS_PUBSUB_PORT}/{settings.REDIS_DB}"

# WebSocket configuration dictionary
WEBSOCKET_CONFIG = {
    "port": 8080,
    "path": "/ws",
    "heartbeat_interval": 30000,  # 30 seconds
    "heartbeat_timeout": 5000,    # 5 seconds
    "max_payload": 1048576,       # 1MB
    "max_connections": 10000,
    "allowed_origins": [
        "*",
        # "http://localhost:3000"
    ],
    "ping_interval": settings.WS_PING_INTERVAL,
    "ping_timeout": settings.WS_PING_TIMEOUT,
    "close_timeout": settings.WS_CLOSE_TIMEOUT,
    "max_message_size": settings.WS_MAX_MESSAGE_SIZE,
}