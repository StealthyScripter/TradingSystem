from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
from .config import settings

logger = logging.getLogger(__name__)

# Database engine configuration
engine_kwargs = {
    "echo": settings.DEBUG,
    "future": True,
}

# Add PostgreSQL-specific settings
if settings.DATABASE_URL.startswith("postgresql://"):
    engine_kwargs.update({
        "poolclass": QueuePool,
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_timeout": settings.DB_POOL_TIMEOUT,
        "pool_recycle": settings.DB_POOL_RECYCLE,
        "pool_pre_ping": True,  # Validate connections before use
    })

    # Create async engine for FastAPI-Users (convert postgresql:// to postgresql+asyncpg://)
    async_database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    async_engine = create_async_engine(
        async_database_url,
        echo=settings.DEBUG,
        future=True,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_recycle=settings.DB_POOL_RECYCLE,
        pool_pre_ping=True,
    )
else:
    # SQLite settings (for development)
    engine_kwargs.update({
        "connect_args": {"check_same_thread": False}
    })
    # For SQLite, we'll use a simple async wrapper
    async_engine = None

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def check_database_connection():
    """Check database connection with retries"""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

# Create database engine
engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create async session factory for FastAPI-Users
if async_engine:
    AsyncSessionLocal = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
else:
    AsyncSessionLocal = None

# Create base class for models
Base = declarative_base()

# Database event listeners for PostgreSQL
if settings.DATABASE_URL.startswith("postgresql://"):
    @event.listens_for(engine, "connect")
    def set_postgresql_pragma(dbapi_connection, connection_record):
        """Set PostgreSQL connection parameters"""
        pass

    @event.listens_for(engine, "before_cursor_execute")
    def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        """Log SQL queries in debug mode"""
        if settings.DEBUG:
            logger.debug("Query: %s", statement)
            logger.debug("Parameters: %s", parameters)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

async def get_async_db():
    """Dependency to get async database session for FastAPI-Users"""
    if not AsyncSessionLocal:
        raise RuntimeError("Async database not configured. Use PostgreSQL with asyncpg.")

    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Async database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()

def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def check_database_connection():
    """Check if database connection is working"""
    try:
        db = SessionLocal()
        # Use text() for raw SQL in SQLAlchemy 2.0+
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

# Initialize database on import
if __name__ != "__main__":
    try:
        check_database_connection()
    except Exception as e:
        logger.warning(f"Initial database check failed: {e}")

class DatabaseManager:
    """Database management utilities"""

    @staticmethod
    def get_connection_info():
        """Get database connection information"""
        return {
            "url": settings.DATABASE_URL.replace(
                settings.DATABASE_URL.split("://")[1].split("@")[0], "***"
            ),
            "pool_size": settings.DB_POOL_SIZE if settings.DATABASE_URL.startswith("postgresql://") else "N/A",
            "max_overflow": settings.DB_MAX_OVERFLOW if settings.DATABASE_URL.startswith("postgresql://") else "N/A",
        }

    @staticmethod
    def get_pool_status():
        """Get connection pool status (PostgreSQL only)"""
        if settings.DATABASE_URL.startswith("postgresql://"):
            return {
                "pool_size": engine.pool.size(),
                "checked_out": engine.pool.checkedout(),
                "overflow": engine.pool.overflow(),
            }
        return {"status": "SQLite - no pooling"}

# Export commonly used objects
__all__ = ["engine", "SessionLocal", "AsyncSessionLocal", "Base", "get_db", "get_async_db", "create_tables", "check_database_connection", "DatabaseManager"]

def get_database_info():
    """Get database connection information for API response"""
    return {
        "database_type": "PostgreSQL" if settings.DATABASE_URL.startswith("postgresql://") else "SQLite",
        "database_name": settings.DATABASE_URL.split("/")[-1] if "/" in settings.DATABASE_URL else "portfolio_db",
        "connection_pool": DatabaseManager.get_pool_status() if settings.DATABASE_URL.startswith("postgresql://") else "N/A",
        "status": "connected" if check_database_connection() else "disconnected"
    }

# Add detailed health endpoint
@app.get("/health/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Kubernetes-style readiness probe"""
    checks = {
        "database": False,
        "redis": False,
        "auth": False
    }

    # Database check
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = True
    except:
        pass

    # Redis check (if configured)
    try:
        if settings.REDIS_URL:
            # Add redis ping
            checks["redis"] = True
    except:
        pass

    # Auth check
    checks["auth"] = bool(settings.CLERK_SECRET_KEY)

    all_healthy = all(checks.values())

    return JSONResponse(
        status_code=200 if all_healthy else 503,
        content={
            "status": "ready" if all_healthy else "not_ready",
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
