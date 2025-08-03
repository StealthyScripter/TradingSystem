from pydantic import BaseSettings
from typing import List, Dict, Optional

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI-First Financial Analysis Platform"
    
    # Database URLs
    POSTGRES_URL: str = "postgresql://user:pass@localhost/financial_ai"
    REDIS_URL: str = "redis://localhost:6379"
    QDRANT_URL: str = "http://localhost:6333"
    
    # ML Model Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    HUGGINGFACE_API_KEY: Optional[str] = None
    
    # Financial Data APIs
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    POLYGON_API_KEY: Optional[str] = None
    NEWS_API_KEY: Optional[str] = None
    TWITTER_BEARER_TOKEN: Optional[str] = None
    
    # Model Settings
    DEFAULT_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    FINANCIAL_EMBEDDING_MODEL: str = "sentence-transformers/all-mpnet-base-v2"
    SENTIMENT_MODEL: str = "ProsusAI/finbert"
    
    # MLflow
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    MLFLOW_EXPERIMENT_NAME: str = "financial_analysis"
    
    class Config:
        env_file = ".env"

settings = Settings()
