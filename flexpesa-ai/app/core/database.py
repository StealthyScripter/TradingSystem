from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
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
else:
    # SQLite settings (for development)
    engine_kwargs.update({
        "connect_args": {"check_same_thread": False}
    })

# Create database engine
engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Database event listeners for PostgreSQL
if settings.DATABASE_URL.startswith("postgresql://"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
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
__all__ = ["engine", "SessionLocal", "Base", "get_db", "create_tables", "check_database_connection", "DatabaseManager"]
