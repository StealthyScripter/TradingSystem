from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api.routes import router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Simple Investment Portfolio Management",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "message": "Investment Portfolio MVP API",
        "endpoints": {
            "portfolio_summary": "/api/v1/portfolio/summary",
            "update_prices": "/api/v1/portfolio/update-prices",
            "accounts": "/api/v1/accounts/",
            "assets": "/api/v1/assets/"
        }
    }
