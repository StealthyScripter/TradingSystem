"""
Production Database Initialization Script
Creates clean database schema without sample data
"""

import sys
import os
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.core.database import SessionLocal, engine, Base
from app.models.portfolio import Account, Asset
from app.core.config import settings, validate_production_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_database_schema():
    """Create all database tables"""
    try:
        logger.info("Creating database schema...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database schema created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create database schema: {e}")
        return False

def verify_database():
    """Verify database connectivity and schema"""
    try:
        db = SessionLocal()

        # Test basic queries
        account_count = db.query(Account).count()
        asset_count = db.query(Asset).count()

        logger.info(f"Database verification:")
        logger.info(f"  - Accounts table: ✅ ({account_count} records)")
        logger.info(f"  - Assets table: ✅ ({asset_count} records)")

        db.close()
        return True

    except Exception as e:
        logger.error(f"❌ Database verification failed: {e}")
        return False

def create_data_directory():
    """Create data directory if it doesn't exist"""
    try:
        data_dir = project_root / "data"
        data_dir.mkdir(exist_ok=True)

        # Create logs directory for production
        logs_dir = project_root / "logs"
        logs_dir.mkdir(exist_ok=True)

        logger.info("✅ Data directories created")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to create directories: {e}")
        return False

def check_environment_setup():
    """Check if environment is properly configured"""
    try:
        logger.info("Checking environment configuration...")

        # Check required environment variables
        required_vars = []
        optional_vars = ["GEMINI_API_KEY"]

        # Check if .env file exists
        env_file = project_root / ".env"
        if not env_file.exists():
            logger.warning("⚠️ .env file not found - create one for configuration")

            # Create sample .env file
            sample_env = """
# Investment Portfolio API Configuration

# Environment (development, staging, production)
ENVIRONMENT=development

# Database URL (SQLite for development, PostgreSQL for production)
DATABASE_URL=sqlite:///./data/portfolio.db

# Security
SECRET_KEY=your-secret-key-change-in-production-$(openssl rand -hex 32)
DEBUG=true

# AI Services (Optional but recommended)
GEMINI_API_KEY=your-gemini-api-key-here

# CORS Origins (comma-separated)
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
""".strip()

            with open(env_file, 'w') as f:
                f.write(sample_env)

            logger.info("✅ Sample .env file created")

        # Validate production settings if in production
        if settings.ENVIRONMENT == "production":
            try:
                validate_production_config()
                logger.info("✅ Production configuration valid")
            except ValueError as e:
                logger.error(f"❌ Production configuration invalid: {e}")
                return False

        logger.info(f"Environment: {settings.ENVIRONMENT}")
        logger.info(f"Database: {settings.DATABASE_URL}")
        logger.info(f"AI Enabled: {'Yes' if settings.GEMINI_API_KEY else 'No'}")

        return True

    except Exception as e:
        logger.error(f"❌ Environment check failed: {e}")
        return False

def create_admin_user():
    """Create default admin configurations (if needed in future)"""
    # Placeholder for future admin user functionality
    logger.info("✅ Admin configuration ready")
    return True

def main():
    """Main initialization function"""
    logger.info("🚀 Initializing Investment Portfolio Database")
    logger.info("=" * 60)

    success = True

    # Step 1: Check environment
    if not check_environment_setup():
        success = False

    # Step 2: Create directories
    if success and not create_data_directory():
        success = False

    # Step 3: Create database schema
    if success and not create_database_schema():
        success = False

    # Step 4: Verify database
    if success and not verify_database():
        success = False

    # Step 5: Setup admin (future)
    if success and not create_admin_user():
        success = False

    logger.info("=" * 60)

    if success:
        logger.info("🎉 Database initialization completed successfully!")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Configure your .env file with proper API keys")
        logger.info("2. Start the API server: python run.py")
        logger.info("3. Access API documentation: http://localhost:8000/docs")
        logger.info("4. Start adding your investment accounts and assets")
        logger.info("")
        logger.info("API Endpoints:")
        logger.info("- Portfolio Summary: GET /api/v1/portfolio/summary")
        logger.info("- Create Account: POST /api/v1/accounts/")
        logger.info("- Add Asset: POST /api/v1/assets/")
        logger.info("- Update Prices: POST /api/v1/portfolio/update-prices")
        return 0
    else:
        logger.error("❌ Database initialization failed!")
        logger.error("Please check the errors above and try again.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
