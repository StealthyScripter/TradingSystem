from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional
from pathlib import Path
import os

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

    # Database Configuration - PostgreSQL ONLY
    DATABASE_URL: str = "postgresql://portfolio_user:portfolio_password@postgres:5432/portfolio_db"

    # PostgreSQL Pool Settings
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Validate PostgreSQL URL only
        if not self.DATABASE_URL.startswith("postgresql://"):
            raise ValueError("DATABASE_URL must use PostgreSQL format: postgresql://...")

        # Ensure Docker environment uses correct PostgreSQL URL
        if os.getenv("DOCKER_ENV") == "true":
            if not self.DATABASE_URL.startswith("postgresql://"):
                self.DATABASE_URL = "postgresql://portfolio_user:portfolio_password@postgres:5432/portfolio_db"

    # API Keys (optional)
    NEWS_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    # CORS Configuration - use string instead of List to avoid JSON parsing
    ALLOWED_ORIGINS: str = "http://localhost:3000,https://localhost:3000,http://frontend:3000"

    def get_allowed_origins(self) -> list[str]:
        """Convert ALLOWED_ORIGINS string to list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

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

    # Redis Configuration (optional)
    REDIS_URL: Optional[str] = "redis://redis:6379"
    CACHE_TTL: int = 300  # 5 minutes

    # Production Settings
    SENTRY_DSN: Optional[str] = None

    # Health Check Settings
    HEALTH_CHECK_TIMEOUT: int = 30

    # Configure Pydantic to read from .env file
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

def get_settings() -> Settings:
    """Get settings instance with caching"""
    return Settings()

def validate_production_config() -> None:
    """Validate production configuration"""
    settings = get_settings()

    errors = []

    if settings.ENVIRONMENT == "production":
        if settings.SECRET_KEY == "your-secret-key-change-in-production-abc123def456ghi789jkl":
            errors.append("SECRET_KEY must be changed in production")

        if settings.DEBUG:
            errors.append("DEBUG must be False in production")

        if not settings.DATABASE_URL.startswith("postgresql://"):
            errors.append("DATABASE_URL must use PostgreSQL in production")

    if errors:
        raise ValueError("Production configuration errors: " + "; ".join(errors))

settings = get_settings()