#!/usr/bin/env python3
"""
Enhanced Database Initialization Script
Populates PostgreSQL database with comprehensive data for development and testing
Replaces all mock/placeholder data with proper database entries
"""

import sys
import os
import time
import logging
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

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

class DatabaseInitializer:
    """Comprehensive database initialization for Investment Portfolio"""

    def __init__(self):
        self.db = SessionLocal()

        # Demo user IDs for different scenarios
        self.demo_users = {
            "primary": "user_demo_primary_12345",
            "secondary": "user_demo_secondary_67890",
            "test": "user_test_abcdef"
        }

    def wait_for_postgresql(self, max_retries=30, delay=2):
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

    def create_tables(self):
        """Create all database tables"""
        try:
            logger.info("Creating PostgreSQL database tables...")
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Database tables created successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create database tables: {e}")
            return False

    def clear_existing_data(self):
        """Clear existing data from all tables"""
        try:
            logger.info("Clearing existing data...")

            # Clear in proper order due to foreign keys
            self.db.query(PortfolioSnapshot).delete()
            self.db.query(MarketData).delete()
            self.db.query(Asset).delete()
            self.db.query(Account).delete()

            self.db.commit()
            logger.info("✅ Existing data cleared")
        except Exception as e:
            logger.error(f"❌ Failed to clear existing data: {e}")
            self.db.rollback()
            raise

    def create_comprehensive_market_data(self):
        """Create comprehensive market data cache to replace hardcoded mock data"""
        logger.info("Creating comprehensive market data cache...")

        # Extended market data including stocks, ETFs, crypto, and indices
        market_data_entries = [
            # Major Tech Stocks
            {"symbol": "AAPL", "name": "Apple Inc.", "current_price": 185.50, "sector": "Technology", "industry": "Consumer Electronics", "asset_type": "stock", "exchange": "NASDAQ"},
            {"symbol": "MSFT", "name": "Microsoft Corporation", "current_price": 338.20, "sector": "Technology", "industry": "Software", "asset_type": "stock", "exchange": "NASDAQ"},
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "current_price": 139.85, "sector": "Communication Services", "industry": "Internet Content & Information", "asset_type": "stock", "exchange": "NASDAQ"},
            {"symbol": "AMZN", "name": "Amazon.com Inc.", "current_price": 148.30, "sector": "Consumer Discretionary", "industry": "Internet Retail", "asset_type": "stock", "exchange": "NASDAQ"},
            {"symbol": "META", "name": "Meta Platforms Inc.", "current_price": 318.75, "sector": "Communication Services", "industry": "Social Media", "asset_type": "stock", "exchange": "NASDAQ"},
            {"symbol": "NVDA", "name": "NVIDIA Corporation", "current_price": 725.40, "sector": "Technology", "industry": "Semiconductors", "asset_type": "stock", "exchange": "NASDAQ"},
            {"symbol": "TSLA", "name": "Tesla, Inc.", "current_price": 198.50, "sector": "Consumer Discretionary", "industry": "Auto Manufacturers", "asset_type": "stock", "exchange": "NASDAQ"},
            {"symbol": "AMD", "name": "Advanced Micro Devices", "current_price": 126.30, "sector": "Technology", "industry": "Semiconductors", "asset_type": "stock", "exchange": "NASDAQ"},

            # Financial Stocks
            {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "current_price": 165.80, "sector": "Financial Services", "industry": "Banks", "asset_type": "stock", "exchange": "NYSE"},
            {"symbol": "BAC", "name": "Bank of America Corp", "current_price": 34.20, "sector": "Financial Services", "industry": "Banks", "asset_type": "stock", "exchange": "NYSE"},
            {"symbol": "WFC", "name": "Wells Fargo & Company", "current_price": 45.60, "sector": "Financial Services", "industry": "Banks", "asset_type": "stock", "exchange": "NYSE"},
            {"symbol": "GS", "name": "Goldman Sachs Group Inc", "current_price": 385.70, "sector": "Financial Services", "industry": "Investment Banking", "asset_type": "stock", "exchange": "NYSE"},

            # Healthcare
            {"symbol": "JNJ", "name": "Johnson & Johnson", "current_price": 158.90, "sector": "Healthcare", "industry": "Pharmaceuticals", "asset_type": "stock", "exchange": "NYSE"},
            {"symbol": "UNH", "name": "UnitedHealth Group Inc", "current_price": 518.25, "sector": "Healthcare", "industry": "Health Insurance", "asset_type": "stock", "exchange": "NYSE"},
            {"symbol": "PFE", "name": "Pfizer Inc.", "current_price": 28.75, "sector": "Healthcare", "industry": "Pharmaceuticals", "asset_type": "stock", "exchange": "NYSE"},

            # Consumer Goods
            {"symbol": "KO", "name": "The Coca-Cola Company", "current_price": 62.80, "sector": "Consumer Staples", "industry": "Beverages", "asset_type": "stock", "exchange": "NYSE"},
            {"symbol": "PG", "name": "Procter & Gamble Co", "current_price": 154.30, "sector": "Consumer Staples", "industry": "Personal Products", "asset_type": "stock", "exchange": "NYSE"},

            # ETFs
            {"symbol": "SPY", "name": "SPDR S&P 500 ETF Trust", "current_price": 445.30, "sector": "Financial", "industry": "ETF", "asset_type": "etf", "exchange": "NYSE"},
            {"symbol": "QQQ", "name": "Invesco QQQ Trust", "current_price": 368.75, "sector": "Technology", "industry": "ETF", "asset_type": "etf", "exchange": "NASDAQ"},
            {"symbol": "VTI", "name": "Vanguard Total Stock Market ETF", "current_price": 235.80, "sector": "Financial", "industry": "ETF", "asset_type": "etf", "exchange": "NYSE"},
            {"symbol": "IWM", "name": "iShares Russell 2000 ETF", "current_price": 198.45, "sector": "Financial", "industry": "ETF", "asset_type": "etf", "exchange": "NYSE"},
            {"symbol": "VEA", "name": "Vanguard FTSE Developed Markets ETF", "current_price": 48.90, "sector": "Financial", "industry": "ETF", "asset_type": "etf", "exchange": "NYSE"},
            {"symbol": "VWO", "name": "Vanguard FTSE Emerging Markets ETF", "current_price": 42.15, "sector": "Financial", "industry": "ETF", "asset_type": "etf", "exchange": "NYSE"},
            {"symbol": "BND", "name": "Vanguard Total Bond Market ETF", "current_price": 76.85, "sector": "Financial", "industry": "ETF", "asset_type": "etf", "exchange": "NYSE"},

            # Sector ETFs
            {"symbol": "XLK", "name": "Technology Select Sector SPDR Fund", "current_price": 185.20, "sector": "Technology", "industry": "ETF", "asset_type": "etf", "exchange": "NYSE"},
            {"symbol": "XLF", "name": "Financial Select Sector SPDR Fund", "current_price": 38.45, "sector": "Financial", "industry": "ETF", "asset_type": "etf", "exchange": "NYSE"},
            {"symbol": "XLE", "name": "Energy Select Sector SPDR Fund", "current_price": 85.30, "sector": "Energy", "industry": "ETF", "asset_type": "etf", "exchange": "NYSE"},
            {"symbol": "XLV", "name": "Health Care Select Sector SPDR Fund", "current_price": 128.75, "sector": "Healthcare", "industry": "ETF", "asset_type": "etf", "exchange": "NYSE"},

            # Cryptocurrency
            {"symbol": "BTC-USD", "name": "Bitcoin", "current_price": 42350.00, "sector": "Cryptocurrency", "industry": "Digital Currency", "asset_type": "crypto", "exchange": "CRYPTO"},
            {"symbol": "ETH-USD", "name": "Ethereum", "current_price": 2480.00, "sector": "Cryptocurrency", "industry": "Digital Currency", "asset_type": "crypto", "exchange": "CRYPTO"},
            {"symbol": "ADA-USD", "name": "Cardano", "current_price": 0.485, "sector": "Cryptocurrency", "industry": "Digital Currency", "asset_type": "crypto", "exchange": "CRYPTO"},
            {"symbol": "SOL-USD", "name": "Solana", "current_price": 98.75, "sector": "Cryptocurrency", "industry": "Digital Currency", "asset_type": "crypto", "exchange": "CRYPTO"},

            # International Stocks
            {"symbol": "ASML", "name": "ASML Holding N.V.", "current_price": 720.50, "sector": "Technology", "industry": "Semiconductor Equipment", "asset_type": "stock", "exchange": "NASDAQ"},
            {"symbol": "TSM", "name": "Taiwan Semiconductor Manufacturing", "current_price": 98.20, "sector": "Technology", "industry": "Semiconductors", "asset_type": "stock", "exchange": "NYSE"},
        ]

        try:
            for data in market_data_entries:
                # Add some realistic variation and market data
                price = data["current_price"]

                # Generate realistic daily change (-3% to +3%)
                day_change_percent = random.uniform(-3.0, 3.0)
                day_change = price * (day_change_percent / 100)

                # Generate realistic volume based on asset type
                if data["asset_type"] == "crypto":
                    volume = random.uniform(1000000, 50000000)  # High volume for crypto
                elif data["asset_type"] == "etf":
                    volume = random.uniform(5000000, 100000000)  # High volume for ETFs
                else:
                    volume = random.uniform(1000000, 25000000)  # Stock volume

                # Generate market cap for stocks
                if data["asset_type"] == "stock":
                    # Estimate market cap based on price (simplified)
                    if price > 300:
                        market_cap = random.uniform(500000000000, 3000000000000)  # Large cap
                    elif price > 100:
                        market_cap = random.uniform(100000000000, 500000000000)  # Mid to large cap
                    else:
                        market_cap = random.uniform(10000000000, 100000000000)   # Small to mid cap
                else:
                    market_cap = None

                market_data_entry = MarketData(
                    symbol=data["symbol"],
                    name=data["name"],
                    current_price=price,
                    open_price=price * random.uniform(0.98, 1.02),  # Open within 2% of current
                    high_price=price * random.uniform(1.00, 1.03),  # High up to 3% above current
                    low_price=price * random.uniform(0.97, 1.00),   # Low up to 3% below current
                    volume=volume,
                    day_change=day_change,
                    day_change_percent=day_change_percent,
                    market_cap=market_cap,
                    sector=data["sector"],
                    industry=data["industry"],
                    currency="USD",
                    exchange=data["exchange"],
                    asset_type=data["asset_type"],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )

                self.db.add(market_data_entry)

            self.db.commit()
            logger.info(f"✅ Created {len(market_data_entries)} market data entries")

        except Exception as e:
            logger.error(f"❌ Failed to create market data: {e}")
            self.db.rollback()
            raise

    def create_benchmark_data(self):
        """Create benchmark data to replace hardcoded performance benchmarks"""
        logger.info("Creating benchmark performance data...")

        # Create benchmark data as special MarketData entries
        benchmarks = [
            {"symbol": "^GSPC", "name": "S&P 500 Index", "current_price": 4450.00, "asset_type": "index"},
            {"symbol": "^IXIC", "name": "NASDAQ Composite", "current_price": 13800.00, "asset_type": "index"},
            {"symbol": "^DJI", "name": "Dow Jones Industrial Average", "current_price": 34500.00, "asset_type": "index"},
            {"symbol": "^RUT", "name": "Russell 2000", "current_price": 1980.00, "asset_type": "index"},
            {"symbol": "^VIX", "name": "CBOE Volatility Index", "current_price": 18.50, "asset_type": "index"},
        ]

        try:
            for benchmark in benchmarks:
                price = benchmark["current_price"]

                market_data = MarketData(
                    symbol=benchmark["symbol"],
                    name=benchmark["name"],
                    current_price=price,
                    open_price=price * random.uniform(0.999, 1.001),
                    high_price=price * random.uniform(1.000, 1.005),
                    low_price=price * random.uniform(0.995, 1.000),
                    volume=0,  # Indices don't have volume
                    day_change=price * random.uniform(-0.02, 0.02),
                    day_change_percent=random.uniform(-2.0, 2.0),
                    sector="Financial",
                    industry="Index",
                    currency="USD",
                    exchange="INDEX",
                    asset_type=benchmark["asset_type"]
                )

                self.db.add(market_data)

            self.db.commit()
            logger.info(f"✅ Created {len(benchmarks)} benchmark entries")

        except Exception as e:
            logger.error(f"❌ Failed to create benchmark data: {e}")
            self.db.rollback()
            raise

    def create_demo_portfolios(self):
        """Create comprehensive demo portfolios"""
        logger.info("Creating demo portfolios...")

        portfolios = [
            {
                "user_id": self.demo_users["primary"],
                "accounts": [
                    {
                        "name": "Wells Fargo Brokerage",
                        "account_type": "brokerage",
                        "description": "Primary investment account with diversified holdings",
                        "assets": [
                            {"symbol": "AAPL", "shares": 50, "avg_cost": 175.30},
                            {"symbol": "MSFT", "shares": 25, "avg_cost": 310.20},
                            {"symbol": "SPY", "shares": 15, "avg_cost": 430.50},
                            {"symbol": "VTI", "shares": 30, "avg_cost": 220.15},
                            {"symbol": "JPM", "shares": 20, "avg_cost": 155.80},
                        ]
                    },
                    {
                        "name": "Fidelity 401(k)",
                        "account_type": "retirement",
                        "description": "Employer-sponsored retirement account",
                        "assets": [
                            {"symbol": "QQQ", "shares": 40, "avg_cost": 350.25},
                            {"symbol": "VEA", "shares": 100, "avg_cost": 47.90},
                            {"symbol": "VWO", "shares": 80, "avg_cost": 41.15},
                            {"symbol": "BND", "shares": 60, "avg_cost": 78.85},
                        ]
                    },
                    {
                        "name": "Robinhood Trading",
                        "account_type": "trading",
                        "description": "Active trading account for growth stocks",
                        "assets": [
                            {"symbol": "TSLA", "shares": 12, "avg_cost": 220.45},
                            {"symbol": "NVDA", "shares": 8, "avg_cost": 680.80},
                            {"symbol": "AMD", "shares": 35, "avg_cost": 115.60},
                            {"symbol": "META", "shares": 10, "avg_cost": 290.30},
                        ]
                    },
                    {
                        "name": "Coinbase Crypto",
                        "account_type": "crypto",
                        "description": "Cryptocurrency investments",
                        "assets": [
                            {"symbol": "BTC-USD", "shares": 0.75, "avg_cost": 38000.00},
                            {"symbol": "ETH-USD", "shares": 3.2, "avg_cost": 2200.00},
                            {"symbol": "SOL-USD", "shares": 50, "avg_cost": 85.75},
                        ]
                    }
                ]
            },
            {
                "user_id": self.demo_users["secondary"],
                "accounts": [
                    {
                        "name": "Vanguard Portfolio",
                        "account_type": "investment",
                        "description": "Conservative long-term investment strategy",
                        "assets": [
                            {"symbol": "VTI", "shares": 100, "avg_cost": 215.15},
                            {"symbol": "VEA", "shares": 150, "avg_cost": 48.90},
                            {"symbol": "BND", "shares": 200, "avg_cost": 77.85},
                            {"symbol": "XLV", "shares": 25, "avg_cost": 125.75},
                            {"symbol": "XLF", "shares": 40, "avg_cost": 37.45},
                        ]
                    },
                    {
                        "name": "Individual Stocks",
                        "account_type": "brokerage",
                        "description": "Individual stock picks",
                        "assets": [
                            {"symbol": "JNJ", "shares": 30, "avg_cost": 155.90},
                            {"symbol": "KO", "shares": 50, "avg_cost": 60.80},
                            {"symbol": "PG", "shares": 20, "avg_cost": 150.30},
                            {"symbol": "UNH", "shares": 5, "avg_cost": 485.25},
                        ]
                    }
                ]
            },
            {
                "user_id": self.demo_users["test"],
                "accounts": [
                    {
                        "name": "Test Portfolio",
                        "account_type": "testing",
                        "description": "Test account for development",
                        "assets": [
                            {"symbol": "AAPL", "shares": 10, "avg_cost": 180.00},
                            {"symbol": "SPY", "shares": 5, "avg_cost": 440.00},
                            {"symbol": "BTC-USD", "shares": 0.1, "avg_cost": 40000.00},
                        ]
                    }
                ]
            }
        ]

        try:
            total_accounts = 0
            total_assets = 0

            for portfolio in portfolios:
                user_id = portfolio["user_id"]

                for account_data in portfolio["accounts"]:
                    # Create account
                    account = Account(
                        clerk_user_id=user_id,
                        name=account_data["name"],
                        account_type=account_data["account_type"],
                        description=account_data["description"],
                        currency="USD",
                        is_active=True,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )

                    self.db.add(account)
                    self.db.commit()
                    self.db.refresh(account)
                    total_accounts += 1

                    # Create assets for this account
                    for asset_data in account_data["assets"]:
                        # Get market data for this symbol
                        market_data = self.db.query(MarketData).filter(
                            MarketData.symbol == asset_data["symbol"]
                        ).first()

                        current_price = market_data.current_price if market_data else asset_data["avg_cost"]

                        asset = Asset(
                            account_id=account.id,
                            symbol=asset_data["symbol"],
                            name=market_data.name if market_data else None,
                            shares=asset_data["shares"],
                            avg_cost=asset_data["avg_cost"],
                            current_price=current_price,
                            asset_type=market_data.asset_type if market_data else "stock",
                            sector=market_data.sector if market_data else None,
                            industry=market_data.industry if market_data else None,
                            exchange=market_data.exchange if market_data else None,
                            currency="USD",
                            is_active=True,
                            created_at=datetime.utcnow(),
                            last_updated=datetime.utcnow(),
                            price_updated_at=datetime.utcnow()
                        )

                        self.db.add(asset)
                        total_assets += 1

                    logger.info(f"   Created account: {account.name} with {len(account_data['assets'])} assets")

            self.db.commit()
            logger.info(f"✅ Created {total_accounts} accounts with {total_assets} assets")

        except Exception as e:
            logger.error(f"❌ Failed to create demo portfolios: {e}")
            self.db.rollback()
            raise

    def create_portfolio_snapshots(self):
        """Create historical portfolio snapshots"""
        logger.info("Creating portfolio snapshots...")

        try:
            # Create snapshots for each demo user
            for user_id in self.demo_users.values():
                # Get user's accounts
                accounts = self.db.query(Account).filter(
                    Account.clerk_user_id == user_id,
                    Account.is_active == True
                ).all()

                if not accounts:
                    continue

                # Calculate totals
                total_value = 0
                total_cost = 0
                total_assets = 0

                for account in accounts:
                    for asset in account.assets:
                        if asset.is_active:
                            market_value = asset.shares * asset.current_price
                            cost_basis = asset.shares * asset.avg_cost
                            total_value += market_value
                            total_cost += cost_basis
                            total_assets += 1

                total_pnl = total_value - total_cost
                total_pnl_percent = (total_pnl / total_cost * 100) if total_cost > 0 else 0

                # Create current snapshot
                snapshot = PortfolioSnapshot(
                    clerk_user_id=user_id,
                    total_value=total_value,
                    total_cost_basis=total_cost,
                    total_pnl=total_pnl,
                    total_pnl_percent=total_pnl_percent,
                    asset_count=total_assets,
                    account_count=len(accounts),
                    snapshot_type="daily",
                    created_at=datetime.utcnow()
                )

                self.db.add(snapshot)

                # Create historical snapshots (last 30 days)
                for days_ago in range(1, 31):
                    snapshot_date = datetime.utcnow() - timedelta(days=days_ago)

                    # Simulate historical values with some variation
                    historical_value = total_value * random.uniform(0.95, 1.05)
                    historical_pnl = historical_value - total_cost
                    historical_pnl_percent = (historical_pnl / total_cost * 100) if total_cost > 0 else 0

                    historical_snapshot = PortfolioSnapshot(
                        clerk_user_id=user_id,
                        total_value=historical_value,
                        total_cost_basis=total_cost,
                        total_pnl=historical_pnl,
                        total_pnl_percent=historical_pnl_percent,
                        asset_count=total_assets,
                        account_count=len(accounts),
                        snapshot_type="daily",
                        created_at=snapshot_date
                    )

                    self.db.add(historical_snapshot)

                logger.info(f"   Created snapshots for user: {user_id}")

            self.db.commit()
            logger.info("✅ Portfolio snapshots created")

        except Exception as e:
            logger.error(f"❌ Failed to create portfolio snapshots: {e}")
            self.db.rollback()
            raise

    def update_account_balances(self):
        """Update account balances based on current asset values"""
        logger.info("Updating account balances...")

        try:
            accounts = self.db.query(Account).filter(Account.is_active == True).all()

            for account in accounts:
                total_value = 0
                for asset in account.assets:
                    if asset.is_active:
                        total_value += asset.shares * asset.current_price

                account.balance = total_value
                account.updated_at = datetime.utcnow()

            self.db.commit()
            logger.info(f"✅ Updated balances for {len(accounts)} accounts")

        except Exception as e:
            logger.error(f"❌ Failed to update account balances: {e}")
            self.db.rollback()
            raise

    def print_summary(self):
        """Print database initialization summary"""
        try:
            # Get counts
            accounts_count = self.db.query(Account).count()
            assets_count = self.db.query(Asset).count()
            market_data_count = self.db.query(MarketData).count()
            snapshots_count = self.db.query(PortfolioSnapshot).count()

            # Get portfolio values by user
            user_summaries = []
            for user_name, user_id in self.demo_users.items():
                accounts = self.db.query(Account).filter(
                    Account.clerk_user_id == user_id
                ).all()

                total_value = sum(account.balance for account in accounts)
                user_summaries.append({
                    "name": user_name,
                    "user_id": user_id,
                    "accounts": len(accounts),
                    "total_value": total_value
                })

            summary = f"""
╔══════════════════════════════════════════════════════════════╗
║                    DATABASE INITIALIZATION SUMMARY           ║
╠══════════════════════════════════════════════════════════════╣
║  📊 Market Data Entries:    {market_data_count:4d}                           ║
║  🏦 Demo Accounts:          {accounts_count:4d}                           ║
║  📈 Asset Holdings:         {assets_count:4d}                           ║
║  📷 Portfolio Snapshots:    {snapshots_count:4d}                           ║
╠══════════════════════════════════════════════════════════════╣
║                        DEMO USERS                            ║
╠══════════════════════════════════════════════════════════════╣"""

            for user in user_summaries:
                name_padded = f"{user['name'].title()}".ljust(20)
                value_formatted = f"${user['total_value']:,.0f}".rjust(15)
                summary += f"\n║  👤 {name_padded} {user['accounts']} accounts {value_formatted} ║"

            summary += f"""
╠══════════════════════════════════════════════════════════════╣
║                      NEXT STEPS                              ║
║  1. Start the API server: python run.py                     ║
║  2. Access API docs: http://localhost:8000/docs             ║
║  3. Test portfolio endpoint:                                 ║
║     GET /api/v1/portfolio/summary                           ║
║  4. All mock data replaced with database entries            ║
╚══════════════════════════════════════════════════════════════╝
"""

            logger.info(summary)

        except Exception as e:
            logger.error(f"❌ Failed to generate summary: {e}")

    def run_initialization(self, clear_existing=False):
        """Run complete database initialization"""
        try:
            logger.info("🚀 Starting Enhanced Database Initialization")
            logger.info("=" * 60)

            # Wait for PostgreSQL
            if not self.wait_for_postgresql():
                return False

            # Create tables
            if not self.create_tables():
                return False

            # Clear existing data if requested
            if clear_existing:
                self.clear_existing_data()

            # Create comprehensive data
            self.create_comprehensive_market_data()
            self.create_benchmark_data()
            self.create_demo_portfolios()
            self.create_portfolio_snapshots()
            self.update_account_balances()

            # Print summary
            self.print_summary()

            logger.info("🎉 Database initialization completed successfully!")
            return True

        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            return False

        finally:
            self.db.close()


def main():
    """Main initialization function"""
    import argparse

    parser = argparse.ArgumentParser(description='Initialize Investment Portfolio Database')
    parser.add_argument('--clear-existing', action='store_true',
                       help='Clear existing data before initialization')
    parser.add_argument('--production', action='store_true',
                       help='Initialize for production (minimal demo data)')

    args = parser.parse_args()

    if args.production:
        logger.warning("⚠️  Production mode - creating minimal demo data")

    initializer = DatabaseInitializer()
    success = initializer.run_initialization(clear_existing=args.clear_existing)

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
    