from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator
from typing import Optional
from pathlib import Path
import os
import secrets

class Settings(BaseSettings):
    # Basic API Configuration
    PROJECT_NAME: str = "Investment Portfolio MVP"
    API_V1_STR: str = "/api/v1"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    DISABLE_RATE_LIMITING: bool = False

    # Server Configuration
    BACKEND_PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production-abc123def456ghi789jkl"

    # Development/Testing - ADD THIS SECTION
    DISABLE_AUTH: bool = False
    MOCK_USER_ID: str = "dev_user_12345"
    MOCK_USER_EMAIL: str = "dev@example.com"
    MOCK_USER_FIRST_NAME: str = "Dev"
    MOCK_USER_LAST_NAME: str = "User"

    @field_validator('SECRET_KEY')
    @classmethod
    def validate_secret_key(cls, v, info):
        if info.data.get('ENVIRONMENT') == 'production' and v == "your-secret-key-change-in-production-abc123def456ghi789jkl":
            # Generate a new secret key for production
            return secrets.token_urlsafe(32)
        return v

    # Clerk Authentication Configuration
    CLERK_SECRET_KEY: Optional[str] = None
    CLERK_PUBLISHABLE_KEY: Optional[str] = None
    CLERK_DOMAIN: str = "clerk.your-domain.com"  # Your Clerk domain

    @field_validator('CLERK_SECRET_KEY', 'CLERK_PUBLISHABLE_KEY')
    @classmethod
    def validate_clerk_config(cls, v, info):
        if info.data.get('ENVIRONMENT') == 'production' and not v:
            raise ValueError(f"{info.field_name} is required in production")
        return v

    # Database Configuration - PostgreSQL ONLY
    DATABASE_URL: str = "postgresql://portfolio_user:portfolio_password@localhost:5432/portfolio_db"

    # PostgreSQL Pool Settings
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600

    @field_validator('DATABASE_URL')
    @classmethod
    def validate_database_url(cls, v, info):
        import os
        
        # Allow SQLite for testing environment
        if os.getenv('TESTING') == 'true' or info.data.get('ENVIRONMENT') == 'testing':
            # Allow both PostgreSQL and SQLite in development/testing
            if v.startswith(("postgresql://", "sqlite:///")):
                return v
            raise ValueError("DATABASE_URL must use PostgreSQL (postgresql://) or SQLite (sqlite:///) format")

        if not v.startswith("postgresql://"):
            raise ValueError("DATABASE_URL must use PostgreSQL format: postgresql://...")
        return v

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Ensure Docker environment uses correct PostgreSQL URL
        if os.getenv("DOCKER_ENV") == "true":
            if "localhost" in self.DATABASE_URL:
                self.DATABASE_URL = self.DATABASE_URL.replace("localhost", "postgres")

    # API Keys (optional)
    NEWS_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    # CORS Configuration - use string instead of List to avoid JSON parsing
    ALLOWED_ORIGINS: str = "http://localhost:3000,https://localhost:3000,http://frontend:3000"

    def get_allowed_origins(self) -> list[str]:
        """Convert ALLOWED_ORIGINS string to list"""
        origins = [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

        # Add production origins based on environment
        if self.ENVIRONMENT == "production":
            # Add your production domains here
            production_origins = [
                "https://yourdomain.com",
                "https://www.yourdomain.com",
                "https://app.yourdomain.com"
            ]
            origins.extend(production_origins)

        return origins

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

    # File Upload Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: str = "csv,xlsx,json"

    def get_allowed_file_types(self) -> list[str]:
        """Get allowed file types as list"""
        return [ext.strip() for ext in self.ALLOWED_FILE_TYPES.split(",")]

    # Logging Configuration
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE_MAX_BYTES: int = 10 * 1024 * 1024  # 10MB
    LOG_FILE_BACKUP_COUNT: int = 5

    # Background Task Configuration
    CLEANUP_INTERVAL: int = 3600  # 1 hour
    PRICE_UPDATE_INTERVAL: int = 300  # 5 minutes

    # AI Analysis Configuration
    AI_ANALYSIS_TIMEOUT: int = 30  # seconds
    AI_MAX_SYMBOLS_PER_REQUEST: int = 20

    # Configure Pydantic to read from .env file
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        validate_default=True
    )

def get_settings() -> Settings:
    """Get settings instance with caching"""
    return Settings()

def validate_production_config() -> None:
    """Validate production configuration"""
    settings = get_settings()

    errors = []

    if settings.ENVIRONMENT == "production":
        # Security checks
        if settings.SECRET_KEY == "your-secret-key-change-in-production-abc123def456ghi789jkl":
            errors.append("SECRET_KEY must be changed in production")

        if settings.DEBUG:
            errors.append("DEBUG must be False in production")

        # Database checks
        if not settings.DATABASE_URL.startswith("postgresql://"):
            errors.append("DATABASE_URL must use PostgreSQL in production")

        if "localhost" in settings.DATABASE_URL:
            errors.append("DATABASE_URL should not use localhost in production")

        # Clerk authentication checks
        if not settings.CLERK_SECRET_KEY:
            errors.append("CLERK_SECRET_KEY is required in production")

        if not settings.CLERK_PUBLISHABLE_KEY:
            errors.append("CLERK_PUBLISHABLE_KEY is required in production")

        # CORS checks
        allowed_origins = settings.get_allowed_origins()
        if any("localhost" in origin for origin in allowed_origins):
            errors.append("ALLOWED_ORIGINS should not include localhost in production")

        # SSL/TLS checks
        if not any(origin.startswith("https://") for origin in allowed_origins):
            errors.append("Production should use HTTPS origins")

    if errors:
        raise ValueError("Production configuration errors: " + "; ".join(errors))

def get_database_config() -> dict:
    """Get database configuration details"""
    settings = get_settings()

    # Parse database URL for details
    db_url = settings.DATABASE_URL
    if "@" in db_url and "/" in db_url:
        try:
            # Extract components
            scheme = db_url.split("://")[0]
            rest = db_url.split("://")[1]
            auth_host = rest.split("/")[0]
            database = rest.split("/")[1]

            if "@" in auth_host:
                auth, host = auth_host.split("@")
                username = auth.split(":")[0]
                port = host.split(":")[1] if ":" in host else "5432"
                host = host.split(":")[0]
            else:
                username = "unknown"
                host = auth_host
                port = "5432"

            return {
                "type": scheme,
                "host": host,
                "port": port,
                "database": database,
                "username": username,
                "pool_size": settings.DB_POOL_SIZE,
                "max_overflow": settings.DB_MAX_OVERFLOW
            }
        except:
            pass

    return {
        "type": "postgresql",
        "url": db_url,
        "pool_size": settings.DB_POOL_SIZE
    }

def get_clerk_config() -> dict:
    """Get Clerk configuration for frontend"""
    settings = get_settings()

    return {
        "publishable_key": settings.CLERK_PUBLISHABLE_KEY,
        "domain": settings.CLERK_DOMAIN,
        "configured": bool(settings.CLERK_SECRET_KEY and settings.CLERK_PUBLISHABLE_KEY)
    }

settings = get_settings()

# Validate configuration on import for production
if settings.ENVIRONMENT == "production":
    try:
        validate_production_config()
    except ValueError as e:
        import logging
        logging.error(f"Production configuration validation failed: {e}")
        # Don't raise in production startup, but log the error
