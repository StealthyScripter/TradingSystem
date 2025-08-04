from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Investment Portfolio MVP"
    API_V1_STR: str = "/api/v1"
    
    # Single Database (SQLite for MVP)
    DATABASE_URL: str = "sqlite:///./data/portfolio.db"
    
    # Optional API keys (not required for basic functionality)
    NEWS_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()