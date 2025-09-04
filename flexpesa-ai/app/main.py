from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base, get_database_info, check_database_connection
from app.api.routes import router
from app.middleware.clerk_auth import ClerkAuthMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.logging import LoggingMiddleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Starting Investment Portfolio API")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")

    # Check database connection
    if not check_database_connection():
        logger.error("❌ Database connection failed!")
        raise Exception("Database connection failed")

    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created/verified")
    except Exception as e:
        logger.error(f"❌ Database table creation failed: {e}")
        raise

    logger.info("✅ Application startup complete")
    yield

    # Shutdown
    logger.info("👋 Shutting down Investment Portfolio API")

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Investment Portfolio Management API with PostgreSQL, Real-time Market Data, and AI Analysis",
    version=settings.VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Security Middleware - Add trusted hosts for production
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["yourdomain.com", "*.yourdomain.com", "localhost"]
    )

# Compression Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Custom Rate Limiting Middleware
app.add_middleware(RateLimitMiddleware)

# Custom Logging Middleware
app.add_middleware(LoggingMiddleware)

# Clerk Authentication Middleware - CONDITIONAL
if not settings.DISABLE_AUTH:
    app.add_middleware(ClerkAuthMiddleware)
    logger.info("🔒 Clerk authentication ENABLED")
else:
    logger.warning("⚠️  Authentication DISABLED - using mock user")
    logger.warning(f"   Mock User ID: {settings.MOCK_USER_ID}")
    logger.warning(f"   Mock Email: {settings.MOCK_USER_EMAIL}")

# CORS Middleware - Enhanced configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-CSRF-Token",
        "X-Custom-Header",
        "Access-Control-Allow-Credentials",
        "Access-Control-Allow-Origin"
    ],
    expose_headers=["X-Total-Count", "X-Rate-Limit-Remaining"],
    max_age=86400,  # 24 hours
)

# Global Exception Handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Global HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "timestamp": time.time()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    # Don't expose internal errors in production
    if settings.ENVIRONMENT == "production":
        message = "Internal server error"
    else:
        message = str(exc)

    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": message,
            "status_code": 500,
            "timestamp": time.time()
        }
    )

# Health Check Endpoints
@app.get("/")
def root():
    """API root endpoint with system information"""
    db_info = get_database_info()
    return {
        "message": "Investment Portfolio MVP API",
        "status": "running",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_info,
        "features": {
            "real_time_data": True,
            "ai_analysis": bool(settings.GEMINI_API_KEY),
            "portfolio_tracking": True,
            "authentication": "clerk",
            "database": "postgresql"
        },
        "endpoints": {
            "portfolio_summary": f"{settings.API_V1_STR}/portfolio/summary",
            "update_prices": f"{settings.API_V1_STR}/portfolio/update-prices",
            "accounts": f"{settings.API_V1_STR}/accounts/",
            "assets": f"{settings.API_V1_STR}/assets/",
            "performance": f"{settings.API_V1_STR}/portfolios/performance",
            "docs": "/docs" if settings.DEBUG else "disabled_in_production"
        }
    }

@app.get("/health")
def health_check():
    """Detailed health check endpoint"""
    try:
        db_healthy = check_database_connection()

        return {
            "status": "healthy" if db_healthy else "unhealthy",
            "timestamp": time.time(),
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "checks": {
                "database": "healthy" if db_healthy else "unhealthy",
                "api": "healthy"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": time.time(),
                "error": str(e) if settings.DEBUG else "Service unavailable"
            }
        )

@app.get("/metrics")
def get_metrics():
    """Basic metrics endpoint"""
    if settings.ENVIRONMENT == "production":
        raise HTTPException(status_code=404, detail="Not found")

    from app.core.database import DatabaseManager

    return {
        "database": DatabaseManager.get_pool_status(),
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "timestamp": time.time()
    }

# Include API routes
app.include_router(router, prefix=settings.API_V1_STR, tags=["api"])

# Startup event for additional initialization
@app.on_event("startup")
async def startup_event():
    """Additional startup tasks"""
    logger.info("🔧 Running additional startup tasks...")

    # Validate production configuration
    if settings.ENVIRONMENT == "production":
        from app.core.config import validate_production_config
        try:
            validate_production_config()
            logger.info("✅ Production configuration validated")
        except ValueError as e:
            logger.error(f"❌ Production configuration invalid: {e}")
            raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.BACKEND_PORT or 8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
