import sys
import os
import time
import logging
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine, Base, check_database_connection
from app.models.portfolio import Account, Asset
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def wait_for_postgresql(max_retries=30, delay=2):
    """Wait for PostgreSQL database to be ready"""
    logger.info("Waiting for PostgreSQL connection...")

    for attempt in range(max_retries):
        try:
            if check_database_connection():
                logger.info("✅ PostgreSQL connection established")
                return True
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"PostgreSQL not ready (attempt {attempt + 1}/{max_retries}): {e}")
                time.sleep(delay)
            else:
                logger.error(f"Failed to connect to PostgreSQL after {max_retries} attempts")
                return False

    return False

def create_postgresql_tables():
    """Create all PostgreSQL database tables"""
    try:
        logger.info("Creating PostgreSQL database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ PostgreSQL database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create PostgreSQL database tables: {e}")
        return False

def clear_existing_data(db):
    """Clear existing data from PostgreSQL tables"""
    try:
        logger.info("Clearing existing PostgreSQL data...")
        db.query(Asset).delete()
        db.query(Account).delete()
        db.commit()
        logger.info("✅ Existing PostgreSQL data cleared")
    except Exception as e:
        logger.error(f"❌ Failed to clear existing PostgreSQL data: {e}")
        db.rollback()
        raise

def create_sample_data(db):
    """Create sample portfolio data in PostgreSQL"""

    accounts_data = [
        {
            "name": "Wells Fargo Intuitive",
            "account_type": "brokerage",
            "assets": [
                {"symbol": "AAPL", "shares": 50, "avg_cost": 155.30},
                {"symbol": "MSFT", "shares": 25, "avg_cost": 285.20},
                {"symbol": "SPY", "shares": 15, "avg_cost": 420.50},
            ]
        },
        {
            "name": "Stack Well",
            "account_type": "investment",
            "assets": [
                {"symbol": "QQQ", "shares": 30, "avg_cost": 350.25},
                {"symbol": "VTI", "shares": 40, "avg_cost": 220.15},
                {"symbol": "NVDA", "shares": 5, "avg_cost": 520.80},
            ]
        },
        {
            "name": "Cash App Investing",
            "account_type": "trading",
            "assets": [
                {"symbol": "TSLA", "shares": 8, "avg_cost": 180.45},
                {"symbol": "AMD", "shares": 25, "avg_cost": 85.60},
                {"symbol": "GOOGL", "shares": 12, "avg_cost": 125.30},
            ]
        },
        {
            "name": "Robinhood",
            "account_type": "crypto",
            "assets": [
                {"symbol": "BTC-USD", "shares": 0.5, "avg_cost": 35000},
                {"symbol": "ETH-USD", "shares": 2.5, "avg_cost": 2200},
            ]
        }
    ]

    try:
        logger.info("Creating sample portfolio data in PostgreSQL...")

        for account_data in accounts_data:
            # Create account
            account = Account(
                name=account_data["name"],
                account_type=account_data["account_type"]
            )
            db.add(account)
            db.commit()
            db.refresh(account)

            logger.info(f"Created account in PostgreSQL: {account.name}")

            # Create assets for this account
            for asset_data in account_data["assets"]:
                asset = Asset(account_id=account.id, **asset_data)
                db.add(asset)
                logger.info(f"  Added asset to PostgreSQL: {asset.symbol}")

        db.commit()
        logger.info("✅ Sample data created successfully in PostgreSQL")

        # Print summary
        total_accounts = db.query(Account).count()
        total_assets = db.query(Asset).count()

        logger.info(f"📊 PostgreSQL Summary: {total_accounts} accounts, {total_assets} assets created")

        return True

    except Exception as e:
        logger.error(f"❌ Failed to create sample data in PostgreSQL: {e}")
        db.rollback()
        return False

def print_connection_info():
    """Print PostgreSQL database connection information"""
    masked_url = settings.DATABASE_URL
    if "@" in masked_url:
        # Mask password in URL
        parts = masked_url.split("://")
        if len(parts) == 2:
            scheme = parts[0]
            rest = parts[1]
            if "@" in rest:
                auth, host_db = rest.split("@", 1)
                user = auth.split(":")[0]
                masked_url = f"{scheme}://{user}:***@{host_db}"

    logger.info(f"PostgreSQL Database URL: {masked_url}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

def main():
    """Main initialization function for PostgreSQL"""
    logger.info("🚀 Investment Portfolio PostgreSQL Database Initialization")
    logger.info("=" * 60)

    # Print connection info
    print_connection_info()

    # Wait for PostgreSQL (important for Docker)
    if not wait_for_postgresql():
        logger.error("❌ PostgreSQL database initialization failed - could not connect")
        return 1

    # Create PostgreSQL tables
    if not create_postgresql_tables():
        logger.error("❌ PostgreSQL database initialization failed - could not create tables")
        return 1

    # Initialize data
    db = SessionLocal()
    try:
        # Clear existing data
        clear_existing_data(db)

        # Create sample data
        if not create_sample_data(db):
            logger.error("❌ PostgreSQL database initialization failed - could not create sample data")
            return 1

    except Exception as e:
        logger.error(f"❌ PostgreSQL database initialization failed: {e}")
        return 1
    finally:
        db.close()

    logger.info("=" * 60)
    logger.info("🎉 PostgreSQL Database initialization completed successfully!")
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Start the API server: python run.py")
    logger.info("2. Access API documentation: http://localhost:8000/docs")
    logger.info("3. Test the portfolio endpoint: http://localhost:8000/api/v1/portfolio/summary")
    logger.info("")
    logger.info("PostgreSQL API Endpoints:")
    logger.info("- Portfolio Summary: GET /api/v1/portfolio/summary")
    logger.info("- Create Account: POST /api/v1/accounts/")
    logger.info("- Add Asset: POST /api/v1/assets/")
    logger.info("- Update Prices: POST /api/v1/portfolio/update-prices")

    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
