import sys
import os
import time
import logging
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine, Base, check_database_connection
from app.models.portfolio import Account, Asset, MarketData, PortfolioSnapshot
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

        # Clear in proper order due to foreign keys
        db.query(PortfolioSnapshot).delete()
        db.query(MarketData).delete()
        db.query(Asset).delete()
        db.query(Account).delete()

        db.commit()
        logger.info("✅ Existing PostgreSQL data cleared")
    except Exception as e:
        logger.error(f"❌ Failed to clear existing PostgreSQL data: {e}")
        db.rollback()
        raise

def create_sample_data(db, create_demo_data=True):
    """Create sample portfolio data in PostgreSQL"""

    try:
        logger.info("Creating database schema and initial data...")

        if not create_demo_data:
            logger.info("✅ Database schema created - no demo data requested")
            return True

        # Demo user ID - in production, this would come from Clerk
        demo_clerk_user_id = "user_demo_12345"

        accounts_data = [
            {
                "name": "Wells Fargo Intuitive",
                "account_type": "brokerage",
                "description": "Primary investment account",
                "assets": [
                    {"symbol": "AAPL", "shares": 50, "avg_cost": 155.30, "asset_type": "stock"},
                    {"symbol": "MSFT", "shares": 25, "avg_cost": 285.20, "asset_type": "stock"},
                    {"symbol": "SPY", "shares": 15, "avg_cost": 420.50, "asset_type": "etf"},
                ]
            },
            {
                "name": "Stack Well",
                "account_type": "investment",
                "description": "Long-term growth account",
                "assets": [
                    {"symbol": "QQQ", "shares": 30, "avg_cost": 350.25, "asset_type": "etf"},
                    {"symbol": "VTI", "shares": 40, "avg_cost": 220.15, "asset_type": "etf"},
                    {"symbol": "NVDA", "shares": 5, "avg_cost": 520.80, "asset_type": "stock"},
                ]
            },
            {
                "name": "Cash App Investing",
                "account_type": "trading",
                "description": "Active trading account",
                "assets": [
                    {"symbol": "TSLA", "shares": 8, "avg_cost": 180.45, "asset_type": "stock"},
                    {"symbol": "AMD", "shares": 25, "avg_cost": 85.60, "asset_type": "stock"},
                    {"symbol": "GOOGL", "shares": 12, "avg_cost": 125.30, "asset_type": "stock"},
                ]
            },
            {
                "name": "Robinhood Crypto",
                "account_type": "crypto",
                "description": "Cryptocurrency holdings",
                "assets": [
                    {"symbol": "BTC-USD", "shares": 0.5, "avg_cost": 35000, "asset_type": "crypto"},
                    {"symbol": "ETH-USD", "shares": 2.5, "avg_cost": 2200, "asset_type": "crypto"},
                ]
            }
        ]

        logger.info("Creating demo portfolio data in PostgreSQL...")

        for account_data in accounts_data:
            # Create account
            account = Account(
                clerk_user_id=demo_clerk_user_id,
                name=account_data["name"],
                account_type=account_data["account_type"],
                description=account_data.get("description", ""),
                currency="USD",
                is_active=True
            )
            db.add(account)
            db.commit()
            db.refresh(account)

            logger.info(f"Created account in PostgreSQL: {account.name}")

            # Create assets for this account
            for asset_data in account_data["assets"]:
                asset = Asset(
                    account_id=account.id,
                    symbol=asset_data["symbol"],
                    shares=asset_data["shares"],
                    avg_cost=asset_data["avg_cost"],
                    current_price=asset_data["avg_cost"],  # Initialize with avg_cost
                    asset_type=asset_data.get("asset_type", "stock"),
                    currency="USD",
                    is_active=True
                )
                db.add(asset)
                logger.info(f"  Added asset to PostgreSQL: {asset.symbol}")

        db.commit()

        # Create initial market data cache
        logger.info("Creating initial market data cache...")
        create_initial_market_data(db)

        # Create initial portfolio snapshot
        logger.info("Creating initial portfolio snapshot...")
        create_initial_snapshot(db, demo_clerk_user_id)

        logger.info("✅ Sample data created successfully in PostgreSQL")

        # Print summary
        total_accounts = db.query(Account).count()
        total_assets = db.query(Asset).count()
        total_market_data = db.query(MarketData).count()

        logger.info(f"📊 PostgreSQL Summary:")
        logger.info(f"   - {total_accounts} accounts created")
        logger.info(f"   - {total_assets} assets created")
        logger.info(f"   - {total_market_data} market data entries cached")
        logger.info(f"   - Demo user ID: {demo_clerk_user_id}")

        return True

    except Exception as e:
        logger.error(f"❌ Failed to create sample data in PostgreSQL: {e}")
        db.rollback()
        return False

def create_initial_market_data(db):
    """Create initial market data cache"""
    try:
        market_data_samples = [
            {"symbol": "AAPL", "name": "Apple Inc.", "current_price": 185.50, "sector": "Technology", "asset_type": "stock"},
            {"symbol": "MSFT", "name": "Microsoft Corporation", "current_price": 338.20, "sector": "Technology", "asset_type": "stock"},
            {"symbol": "SPY", "name": "SPDR S&P 500 ETF", "current_price": 445.30, "sector": "Financial", "asset_type": "etf"},
            {"symbol": "QQQ", "name": "Invesco QQQ Trust", "current_price": 368.75, "sector": "Technology", "asset_type": "etf"},
            {"symbol": "VTI", "name": "Vanguard Total Stock Market", "current_price": 235.80, "sector": "Financial", "asset_type": "etf"},
            {"symbol": "NVDA", "name": "NVIDIA Corporation", "current_price": 725.40, "sector": "Technology", "asset_type": "stock"},
            {"symbol": "TSLA", "name": "Tesla, Inc.", "current_price": 198.50, "sector": "Consumer Cyclical", "asset_type": "stock"},
            {"symbol": "AMD", "name": "Advanced Micro Devices", "current_price": 126.30, "sector": "Technology", "asset_type": "stock"},
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "current_price": 139.85, "sector": "Communication Services", "asset_type": "stock"},
            {"symbol": "BTC-USD", "name": "Bitcoin", "current_price": 42350.00, "sector": "Cryptocurrency", "asset_type": "crypto"},
            {"symbol": "ETH-USD", "name": "Ethereum", "current_price": 2480.00, "sector": "Cryptocurrency", "asset_type": "crypto"},
        ]

        for data in market_data_samples:
            market_data = MarketData(
                symbol=data["symbol"],
                name=data["name"],
                current_price=data["current_price"],
                sector=data["sector"],
                asset_type=data["asset_type"],
                currency="USD",
                day_change=0.0,
                day_change_percent=0.0
            )
            db.add(market_data)

        db.commit()
        logger.info("✅ Initial market data cache created")

    except Exception as e:
        logger.warning(f"Failed to create market data cache: {e}")

def create_initial_snapshot(db, clerk_user_id):
    """Create initial portfolio snapshot"""
    try:
        # Calculate portfolio totals
        accounts = db.query(Account).filter(
            Account.clerk_user_id == clerk_user_id
        ).all()

        total_value = 0
        total_cost = 0
        total_assets = 0

        for account in accounts:
            for asset in account.assets:
                market_value = asset.shares * asset.current_price
                cost_basis = asset.shares * asset.avg_cost
                total_value += market_value
                total_cost += cost_basis
                total_assets += 1

        total_pnl = total_value - total_cost
        total_pnl_percent = (total_pnl / total_cost * 100) if total_cost > 0 else 0

        snapshot = PortfolioSnapshot(
            clerk_user_id=clerk_user_id,
            total_value=total_value,
            total_cost_basis=total_cost,
            total_pnl=total_pnl,
            total_pnl_percent=total_pnl_percent,
            asset_count=total_assets,
            account_count=len(accounts),
            snapshot_type="daily"
        )

        db.add(snapshot)
        db.commit()

        logger.info(f"✅ Initial portfolio snapshot created: ${total_value:,.2f} total value")

    except Exception as e:
        logger.warning(f"Failed to create portfolio snapshot: {e}")

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
    logger.info(f"Clerk Domain: {settings.CLERK_DOMAIN}")

def main():
    """Main initialization function for PostgreSQL"""
    import argparse

    parser = argparse.ArgumentParser(description='Initialize Investment Portfolio Database')
    parser.add_argument('--no-demo-data', action='store_true',
                       help='Skip creating demo data (production use)')
    parser.add_argument('--clear-existing', action='store_true',
                       help='Clear existing data before initialization')

    args = parser.parse_args()

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
        # Clear existing data if requested
        if args.clear_existing:
            clear_existing_data(db)

        # Create sample data (unless disabled)
        create_demo_data = not args.no_demo_data
        if not create_sample_data(db, create_demo_data):
            logger.error("❌ PostgreSQL database initialization failed - could not create data")
            return 1

    except Exception as e:
        logger.error(f"❌ PostgreSQL database initialization failed: {e}")
        return 1
    finally:
        db.close()

    logger.info("=" * 60)
    logger.info("🎉 PostgreSQL Database initialization completed successfully!")
    logger.info("")

    if not args.no_demo_data:
        logger.info("Demo Data Created:")
        logger.info("- Demo User ID: user_demo_12345")
        logger.info("- 4 investment accounts with realistic holdings")
        logger.info("- Market data cache populated")
        logger.info("- Initial portfolio snapshot created")
        logger.info("")

    logger.info("Next steps:")
    if settings.ENVIRONMENT == "production":
        logger.info("1. Configure Clerk authentication keys")
        logger.info("2. Set up proper CORS origins for your domain")
        logger.info("3. Update SECRET_KEY for production security")
        logger.info("4. Start the API server: gunicorn app.main:app")
    else:
        logger.info("1. Configure Clerk authentication keys in .env")
        logger.info("2. Start the API server: python run.py")

    logger.info("3. Access API documentation: http://localhost:8000/docs")
    logger.info("4. Test the portfolio endpoint: http://localhost:8000/api/v1/portfolio/summary")
    logger.info("")
    logger.info("API Endpoints:")
    logger.info("- Authentication: /api/v1/auth/profile")
    logger.info("- Portfolio Summary: /api/v1/portfolio/summary")
    logger.info("- Create Account: /api/v1/accounts/")
    logger.info("- Add Asset: /api/v1/assets/")
    logger.info("- Update Prices: /api/v1/portfolio/update-prices")
    logger.info("- Performance Analytics: /api/v1/portfolios/performance")

    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
    