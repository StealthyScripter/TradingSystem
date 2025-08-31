from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base, get_database_info
from app.api.routes import router
from app.api.auth_routes import router as auth_router

# Create PostgreSQL database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Investment Portfolio Management with PostgreSQL",
    version="1.0.0"
)

# Enable CORS for frontend - PostgreSQL only setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth_router, prefix="/api/v1")
app.include_router(router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    db_info = get_database_info()
    return {
        "message": "Investment Portfolio MVP API - PostgreSQL",
        "status": "running",
        "database": db_info,
        "endpoints": {
            "portfolio_summary": "/api/v1/portfolio/summary",
            "update_prices": "/api/v1/portfolio/update-prices",
            "accounts": "/api/v1/accounts/",
            "assets": "/api/v1/assets/"
        }
    }
