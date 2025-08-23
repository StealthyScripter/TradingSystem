from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional
from pathlib import Path

class Settings(BaseSettings):
    # Basic API Configuration
    PROJECT_NAME: str = "Investment Portfolio MVP"
    API_V1_STR: str = "/api/v1"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production-abc123def456ghi789jkl"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 1 week

    DATABASE_URL: str = "sqlite:///./data/portfolio.db"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure data directory exists
        if self.DATABASE_URL.startswith("sqlite:///"):
            db_path = Path(self.DATABASE_URL.replace("sqlite:///", ""))
            db_path.parent.mkdir(parents=True, exist_ok=True)

    # API Keys (optional)
    NEWS_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    # CORS Configuration
    ALLOWED_ORIGINS: str = "http://localhost:3000,https://localhost:3000"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 100

    # Market Data Configuration
    MARKET_DATA_UPDATE_INTERVAL: int = 300  # 5 minutes
    MARKET_DATA_BATCH_SIZE: int = 10

    # Server Configuration
    MAX_CONNECTIONS: int = 100
    KEEP_ALIVE_TIMEOUT: int = 5
    LOG_LEVEL: str = "INFO"

    # Configure Pydantic to read from .env file and allow case-insensitive field names
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields not defined in the model
    )

settings = Settings()