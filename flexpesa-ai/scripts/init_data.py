#!/usr/bin/env python3
"""
Enhanced Database Initialization Script for Investment Portfolio API
Supports both development (mock auth) and production (Clerk) modes
Creates comprehensive test data aligned with the current architecture
"""

import sys
import os
import time
import logging
import json
import random
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from decimal import Decimal

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine, Base, check_database_connection
from app.models.portfolio import Account, Asset, MarketData, PortfolioSnapshot
from app.services.market_data import MarketDataService
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedDatabaseInitializer:
    """Enhanced database initialization with realistic market data and portfolios"""

    def __init__(self, mode: str = "demo"):
        """
        Initialize with different modes:
        - minimal: Basic data for testing
        - demo: Comprehensive demo data for development
        - production: Clean schema only
        """
        self.mode = mode
        self.db = SessionLocal()
        self.market_service = MarketDataService(self.db)

        # User configurations based on auth mode
        if settings.DISABLE_AUTH:
            # Development mode with mock users
            self.demo_users = {
                "primary": settings.MOCK_USER_ID,
                "diversified": "user_demo_diversified_67890",
                "conservative": "user_demo_conservative_11111",
                "aggressive": "user_demo_aggressive_22222",
                "crypto": "user_demo_crypto_33333"
            }
        else:
            # Production mode - these would be real Clerk user IDs
            self.demo_users = {
                "primary": "user_2example_clerk_id_1",
                "diversified": "user_2example_clerk_id_2",
                "conservative": "user_2example_clerk_id_3",
                "aggressive": "user_2example_clerk_id_4",
                "crypto": "user_2example_clerk_id_5"
            }

    async def wait_for_database(self, max_retries: int = 30, delay: int = 2) -> bool:
        """Wait for database connection with proper async handling"""
        logger.info("⏳ Waiting for database connection...")

        for attempt in range(max_retries):
            try:
                if check_database_connection():
                    logger.info("✅ Database connection established")
                    return True
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Database not ready (attempt {attempt + 1}/{max_retries}): {e}")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"❌ Failed to connect after {max_retries} attempts")
                    return False
        return False

    def create_tables(self) -> bool:
        """Create all database tables"""
        try:
            logger.info("🔧 Creating database tables...")
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Database tables created successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create tables: {e}")
            return False

    def clear_existing_data(self):
        """Clear existing data in proper order"""
        try:
            logger.info("🧹 Clearing existing data...")

            # Clear in correct order due to foreign key constraints
            tables_to_clear = [
                (PortfolioSnapshot, "portfolio snapshots"),
                (Asset, "assets"),
                (Account, "accounts"),
                (MarketData, "market data")
            ]

            total_deleted = 0
            for table_class, description in tables_to_clear:
                count = self.db.query(table_class).count()
                if count > 0:
                    self.db.query(table_class).delete()
                    total_deleted += count
                    logger.info(f"   Cleared {count} {description}")

            self.db.commit()
            logger.info(f"✅ Cleared {total_deleted} total records")

        except Exception as e:
            logger.error(f"❌ Failed to clear data: {e}")
            self.db.rollback()
            raise

    def create_comprehensive_market_data(self):
        """Create realistic market data cache"""
        logger.info("📊 Creating comprehensive market data...")

        # Comprehensive market data with realistic prices
        market_data_sets = {
            "large_cap_stocks": [
                {"symbol": "AAPL", "name": "Apple Inc.", "price": 185.50, "sector": "Technology", "industry": "Consumer Electronics"},
                {"symbol": "MSFT", "name": "Microsoft Corporation", "price": 338.20, "sector": "Technology", "industry": "Software"},
                {"symbol": "GOOGL", "name": "Alphabet Inc.", "price": 139.85, "sector": "Communication Services", "industry": "Internet Content"},
                {"symbol": "AMZN", "name": "Amazon.com Inc.", "price": 148.30, "sector": "Consumer Discretionary", "industry": "Internet Retail"},
                {"symbol": "NVDA", "name": "NVIDIA Corporation", "price": 725.40, "sector": "Technology", "industry": "Semiconductors"},
                {"symbol": "META", "name": "Meta Platforms Inc.", "price": 318.75, "sector": "Communication Services", "industry": "Social Media"},
                {"symbol": "TSLA", "name": "Tesla, Inc.", "price": 198.50, "sector": "Consumer Discretionary", "industry": "Auto Manufacturers"},
                {"symbol": "BRK.B", "name": "Berkshire Hathaway Inc.", "price": 345.20, "sector": "Financial Services", "industry": "Insurance"},
            ],
            "financial_stocks": [
                {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "price": 165.80, "sector": "Financial Services", "industry": "Banks"},
                {"symbol": "BAC", "name": "Bank of America Corp", "price": 34.20, "sector": "Financial Services", "industry": "Banks"},
                {"symbol": "WFC", "name": "Wells Fargo & Company", "price": 45.60, "sector": "Financial Services", "industry": "Banks"},
                {"symbol": "GS", "name": "Goldman Sachs Group Inc", "price": 385.70, "sector": "Financial Services", "industry": "Investment Banking"},
                {"symbol": "V", "name": "Visa Inc.", "price": 245.80, "sector": "Financial Services", "industry": "Payment Systems"},
                {"symbol": "MA", "name": "Mastercard Incorporated", "price": 385.90, "sector": "Financial Services", "industry": "Payment Systems"},
            ],
            "healthcare_stocks": [
                {"symbol": "JNJ", "name": "Johnson & Johnson", "price": 158.90, "sector": "Healthcare", "industry": "Pharmaceuticals"},
                {"symbol": "UNH", "name": "UnitedHealth Group Inc", "price": 518.25, "sector": "Healthcare", "industry": "Health Insurance"},
                {"symbol": "PFE", "name": "Pfizer Inc.", "price": 28.75, "sector": "Healthcare", "industry": "Pharmaceuticals"},
                {"symbol": "ABBV", "name": "AbbVie Inc.", "price": 142.50, "sector": "Healthcare", "industry": "Pharmaceuticals"},
                {"symbol": "TMO", "name": "Thermo Fisher Scientific", "price": 548.30, "sector": "Healthcare", "industry": "Life Sciences"},
            ],
            "consumer_stocks": [
                {"symbol": "KO", "name": "The Coca-Cola Company", "price": 62.80, "sector": "Consumer Staples", "industry": "Beverages"},
                {"symbol": "PG", "name": "Procter & Gamble Co", "price": 154.30, "sector": "Consumer Staples", "industry": "Personal Products"},
                {"symbol": "WMT", "name": "Walmart Inc.", "price": 158.75, "sector": "Consumer Staples", "industry": "Retail"},
                {"symbol": "HD", "name": "The Home Depot Inc.", "price": 325.80, "sector": "Consumer Discretionary", "industry": "Home Improvement"},
                {"symbol": "MCD", "name": "McDonald's Corporation", "price": 285.40, "sector": "Consumer Discretionary", "industry": "Restaurants"},
            ],
            "broad_market_etfs": [
                {"symbol": "SPY", "name": "SPDR S&P 500 ETF Trust", "price": 445.30, "sector": "Financial", "industry": "ETF"},
                {"symbol": "QQQ", "name": "Invesco QQQ Trust", "price": 368.75, "sector": "Technology", "industry": "ETF"},
                {"symbol": "VTI", "name": "Vanguard Total Stock Market ETF", "price": 235.80, "sector": "Financial", "industry": "ETF"},
                {"symbol": "IWM", "name": "iShares Russell 2000 ETF", "price": 198.45, "sector": "Financial", "industry": "ETF"},
                {"symbol": "EFA", "name": "iShares MSCI EAFE ETF", "price": 78.90, "sector": "Financial", "industry": "ETF"},
                {"symbol": "VWO", "name": "Vanguard FTSE Emerging Markets ETF", "price": 42.15, "sector": "Financial", "industry": "ETF"},
            ],
            "sector_etfs": [
                {"symbol": "XLK", "name": "Technology Select Sector SPDR Fund", "price": 185.20, "sector": "Technology", "industry": "ETF"},
                {"symbol": "XLF", "name": "Financial Select Sector SPDR Fund", "price": 38.45, "sector": "Financial", "industry": "ETF"},
                {"symbol": "XLE", "name": "Energy Select Sector SPDR Fund", "price": 85.30, "sector": "Energy", "industry": "ETF"},
                {"symbol": "XLV", "name": "Health Care Select Sector SPDR Fund", "price": 128.75, "sector": "Healthcare", "industry": "ETF"},
                {"symbol": "XLI", "name": "Industrial Select Sector SPDR Fund", "price": 108.65, "sector": "Industrials", "industry": "ETF"},
                {"symbol": "XLP", "name": "Consumer Staples Select Sector SPDR Fund", "price": 75.40, "sector": "Consumer Staples", "industry": "ETF"},
            ],
            "bond_etfs": [
                {"symbol": "BND", "name": "Vanguard Total Bond Market ETF", "price": 76.85, "sector": "Financial", "industry": "ETF"},
                {"symbol": "AGG", "name": "iShares Core U.S. Aggregate Bond ETF", "price": 102.45, "sector": "Financial", "industry": "ETF"},
                {"symbol": "TLT", "name": "iShares 20+ Year Treasury Bond ETF", "price": 95.30, "sector": "Financial", "industry": "ETF"},
                {"symbol": "HYG", "name": "iShares iBoxx $ High Yield Corporate Bond ETF", "price": 82.15, "sector": "Financial", "industry": "ETF"},
            ],
            "cryptocurrency": [
                {"symbol": "BTC-USD", "name": "Bitcoin", "price": 42350.00, "sector": "Cryptocurrency", "industry": "Digital Currency"},
                {"symbol": "ETH-USD", "name": "Ethereum", "price": 2480.00, "sector": "Cryptocurrency", "industry": "Digital Currency"},
                {"symbol": "ADA-USD", "name": "Cardano", "price": 0.485, "sector": "Cryptocurrency", "industry": "Digital Currency"},
                {"symbol": "SOL-USD", "name": "Solana", "price": 98.75, "sector": "Cryptocurrency", "industry": "Digital Currency"},
                {"symbol": "MATIC-USD", "name": "Polygon", "price": 0.825, "sector": "Cryptocurrency", "industry": "Digital Currency"},
            ]
        }

        try:
            total_created = 0

            for category, securities in market_data_sets.items():
                logger.info(f"   Creating {category.replace('_', ' ').title()}: {len(securities)} securities")

                for security in securities:
                    price = security["price"]

                    # Generate realistic market data
                    day_change_pct = random.uniform(-3.0, 3.0)
                    day_change = price * (day_change_pct / 100)

                    # Generate volume based on asset type
                    if "crypto" in category:
                        volume = random.uniform(1000000, 100000000)
                    elif "etf" in category:
                        volume = random.uniform(5000000, 200000000)
                    else:
                        volume = random.uniform(500000, 50000000)

                    # Generate market cap for stocks
                    market_cap = None
                    if security.get("sector") not in ["Financial", "Cryptocurrency"]:
                        if price > 300:
                            market_cap = random.uniform(500e9, 3000e9)  # Mega cap
                        elif price > 100:
                            market_cap = random.uniform(50e9, 500e9)   # Large cap
                        elif price > 20:
                            market_cap = random.uniform(2e9, 50e9)     # Mid cap
                        else:
                            market_cap = random.uniform(0.3e9, 2e9)    # Small cap

                    market_data = MarketData(
                        symbol=security["symbol"],
                        name=security["name"],
                        current_price=price,
                        open_price=price * random.uniform(0.98, 1.02),
                        high_price=price * random.uniform(1.00, 1.04),
                        low_price=price * random.uniform(0.96, 1.00),
                        volume=volume,
                        day_change=day_change,
                        day_change_percent=day_change_pct,
                        market_cap=market_cap,
                        sector=security["sector"],
                        industry=security["industry"],
                        currency="USD",
                        exchange=self._determine_exchange(security["symbol"]),
                        asset_type=self._determine_asset_type(security["symbol"]),
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )

                    self.db.add(market_data)
                    total_created += 1

            # Add benchmark indices
            benchmarks = [
                {"symbol": "^GSPC", "name": "S&P 500 Index", "price": 4450.00},
                {"symbol": "^IXIC", "name": "NASDAQ Composite", "price": 13800.00},
                {"symbol": "^DJI", "name": "Dow Jones Industrial Average", "price": 34500.00},
                {"symbol": "^RUT", "name": "Russell 2000", "price": 1980.00},
                {"symbol": "^VIX", "name": "CBOE Volatility Index", "price": 18.50},
            ]

            for benchmark in benchmarks:
                market_data = MarketData(
                    symbol=benchmark["symbol"],
                    name=benchmark["name"],
                    current_price=benchmark["price"],
                    open_price=benchmark["price"] * random.uniform(0.999, 1.001),
                    high_price=benchmark["price"] * random.uniform(1.000, 1.005),
                    low_price=benchmark["price"] * random.uniform(0.995, 1.000),
                    volume=0,
                    day_change=benchmark["price"] * random.uniform(-0.02, 0.02),
                    day_change_percent=random.uniform(-2.0, 2.0),
                    sector="Financial",
                    industry="Index",
                    currency="USD",
                    exchange="INDEX",
                    asset_type="index"
                )
                self.db.add(market_data)
                total_created += 1

            self.db.commit()
            logger.info(f"✅ Created {total_created} market data entries")

        except Exception as e:
            logger.error(f"❌ Failed to create market data: {e}")
            self.db.rollback()
            raise

    def create_realistic_portfolios(self):
        """Create diverse, realistic portfolios for different user types"""
        logger.info("👥 Creating realistic demo portfolios...")

        portfolio_configs = {
            "primary": {
                "name": "Balanced Growth Investor",
                "accounts": [
                    {
                        "name": "Fidelity Brokerage",
                        "type": "brokerage",
                        "description": "Primary investment account with diversified large-cap holdings",
                        "assets": [
                            {"symbol": "AAPL", "shares": 50, "avg_cost": 175.30},
                            {"symbol": "MSFT", "shares": 30, "avg_cost": 310.20},
                            {"symbol": "GOOGL", "shares": 25, "avg_cost": 135.50},
                            {"symbol": "AMZN", "shares": 20, "avg_cost": 145.80},
                            {"symbol": "JPM", "shares": 40, "avg_cost": 155.90},
                            {"symbol": "JNJ", "shares": 35, "avg_cost": 160.25},
                            {"symbol": "SPY", "shares": 25, "avg_cost": 430.50},
                        ]
                    },
                    {
                        "name": "Vanguard 401(k)",
                        "type": "retirement",
                        "description": "Employer 401(k) with broad market exposure",
                        "assets": [
                            {"symbol": "VTI", "shares": 50, "avg_cost": 220.15},
                            {"symbol": "EFA", "shares": 80, "avg_cost": 76.90},
                            {"symbol": "VWO", "shares": 100, "avg_cost": 41.15},
                            {"symbol": "BND", "shares": 75, "avg_cost": 78.85},
                        ]
                    }
                ]
            },
            "diversified": {
                "name": "Diversified Value Investor",
                "accounts": [
                    {
                        "name": "Schwab Portfolio",
                        "type": "investment",
                        "description": "Value-focused diversified portfolio across sectors",
                        "assets": [
                            {"symbol": "BRK.B", "shares": 15, "avg_cost": 335.20},
                            {"symbol": "V", "shares": 20, "avg_cost": 235.80},
                            {"symbol": "WMT", "shares": 30, "avg_cost": 150.75},
                            {"symbol": "HD", "shares": 15, "avg_cost": 315.60},
                            {"symbol": "KO", "shares": 60, "avg_cost": 60.80},
                            {"symbol": "XLF", "shares": 100, "avg_cost": 37.45},
                            {"symbol": "XLV", "shares": 40, "avg_cost": 125.75},
                        ]
                    }
                ]
            },
            "conservative": {
                "name": "Conservative Income Investor",
                "accounts": [
                    {
                        "name": "TD Ameritrade Income",
                        "type": "investment",
                        "description": "Conservative portfolio focused on dividends and bonds",
                        "assets": [
                            {"symbol": "JNJ", "shares": 50, "avg_cost": 155.90},
                            {"symbol": "PG", "shares": 40, "avg_cost": 150.30},
                            {"symbol": "KO", "shares": 80, "avg_cost": 62.80},
                            {"symbol": "BND", "shares": 200, "avg_cost": 77.85},
                            {"symbol": "AGG", "shares": 150, "avg_cost": 103.45},
                            {"symbol": "XLP", "shares": 60, "avg_cost": 74.40},
                        ]
                    }
                ]
            },
            "aggressive": {
                "name": "Growth-Focused Tech Investor",
                "accounts": [
                    {
                        "name": "Robinhood Growth",
                        "type": "trading",
                        "description": "High-growth tech and innovation focused",
                        "assets": [
                            {"symbol": "NVDA", "shares": 15, "avg_cost": 680.80},
                            {"symbol": "TSLA", "shares": 25, "avg_cost": 220.45},
                            {"symbol": "META", "shares": 20, "avg_cost": 290.30},
                            {"symbol": "QQQ", "shares": 30, "avg_cost": 350.25},
                            {"symbol": "XLK", "shares": 50, "avg_cost": 175.20},
                        ]
                    }
                ]
            },
            "crypto": {
                "name": "Digital Asset Enthusiast",
                "accounts": [
                    {
                        "name": "Coinbase Holdings",
                        "type": "crypto",
                        "description": "Cryptocurrency investment portfolio",
                        "assets": [
                            {"symbol": "BTC-USD", "shares": 1.25, "avg_cost": 38000.00},
                            {"symbol": "ETH-USD", "shares": 5.5, "avg_cost": 2200.00},
                            {"symbol": "SOL-USD", "shares": 75, "avg_cost": 85.75},
                            {"symbol": "ADA-USD", "shares": 2000, "avg_cost": 0.45},
                            {"symbol": "MATIC-USD", "shares": 1500, "avg_cost": 0.75},
                        ]
                    },
                    {
                        "name": "Traditional Hedge",
                        "type": "brokerage",
                        "description": "Traditional assets to balance crypto exposure",
                        "assets": [
                            {"symbol": "SPY", "shares": 20, "avg_cost": 440.00},
                            {"symbol": "GS", "shares": 5, "avg_cost": 375.70},
                        ]
                    }
                ]
            }
        }

        try:
            total_accounts = 0
            total_assets = 0

            for user_type, user_data in portfolio_configs.items():
                if user_type not in self.demo_users:
                    continue

                user_id = self.demo_users[user_type]
                logger.info(f"   Creating portfolio for {user_data['name']} ({user_type})")

                for account_config in user_data["accounts"]:
                    # Create account
                    account = Account(
                        clerk_user_id=user_id,
                        name=account_config["name"],
                        account_type=account_config["type"],
                        description=account_config["description"],
                        currency="USD",
                        is_active=True,
                        created_at=datetime.utcnow() - timedelta(days=random.randint(30, 365)),
                        updated_at=datetime.utcnow()
                    )

                    self.db.add(account)
                    self.db.commit()
                    self.db.refresh(account)
                    total_accounts += 1

                    # Create assets for this account
                    for asset_config in account_config["assets"]:
                        market_data = self.db.query(MarketData).filter(
                            MarketData.symbol == asset_config["symbol"]
                        ).first()

                        if not market_data:
                            logger.warning(f"Market data not found for {asset_config['symbol']}")
                            continue

                        # Calculate realistic purchase dates
                        purchase_date = datetime.utcnow() - timedelta(
                            days=random.randint(1, 180)
                        )

                        asset = Asset(
                            account_id=account.id,
                            symbol=asset_config["symbol"],
                            name=market_data.name,
                            shares=asset_config["shares"],
                            avg_cost=asset_config["avg_cost"],
                            current_price=market_data.current_price,
                            asset_type=market_data.asset_type,
                            sector=market_data.sector,
                            industry=market_data.industry,
                            exchange=market_data.exchange,
                            currency="USD",
                            is_active=True,
                            created_at=purchase_date,
                            last_updated=datetime.utcnow(),
                            price_updated_at=datetime.utcnow()
                        )

                        self.db.add(asset)
                        total_assets += 1

                logger.info(f"      Created {len(user_data['accounts'])} accounts")

            self.db.commit()
            logger.info(f"✅ Created {total_accounts} accounts with {total_assets} assets")

        except Exception as e:
            logger.error(f"❌ Failed to create portfolios: {e}")
            self.db.rollback()
            raise

    async def create_historical_snapshots(self):
        """Create realistic historical portfolio snapshots"""
        logger.info("📸 Creating historical portfolio snapshots...")

        try:
            # Create snapshots for each user
            for user_id in self.demo_users.values():
                accounts = self.db.query(Account).filter(
                    Account.clerk_user_id == user_id,
                    Account.is_active == True
                ).all()

                if not accounts:
                    continue

                # Calculate current portfolio value
                current_value = 0
                current_cost = 0
                asset_count = 0

                for account in accounts:
                    for asset in account.assets:
                        if asset.is_active:
                            current_value += asset.shares * asset.current_price
                            current_cost += asset.shares * asset.avg_cost
                            asset_count += 1

                # Create 60 days of historical snapshots
                for days_ago in range(60):
                    snapshot_date = datetime.utcnow() - timedelta(days=days_ago)

                    # Simulate realistic market movements
                    # Recent volatility decreases as we go back in time
                    daily_volatility = random.uniform(0.005, 0.025)  # 0.5% to 2.5% daily
                    market_factor = 1 + random.gauss(0, daily_volatility)

                    # Add some trend (slight upward bias over time for older snapshots)
                    trend_factor = 1 + (days_ago * 0.0001)  # Slight upward bias

                    historical_value = current_value * market_factor * trend_factor
                    historical_pnl = historical_value - current_cost
                    historical_pnl_pct = (historical_pnl / current_cost * 100) if current_cost > 0 else 0

                    snapshot = PortfolioSnapshot(
                        clerk_user_id=user_id,
                        total_value=historical_value,
                        total_cost_basis=current_cost,
                        total_pnl=historical_pnl,
                        total_pnl_percent=historical_pnl_pct,
                        asset_count=asset_count,
                        account_count=len(accounts),
                        snapshot_type="daily",
                        created_at=snapshot_date
                    )

                    self.db.add(snapshot)

                # Add some weekly and monthly snapshots
                for weeks_ago in range(1, 26):  # 6 months of weekly
                    snapshot_date = datetime.utcnow() - timedelta(weeks=weeks_ago)
                    market_factor = 1 + random.gauss(0, 0.05)  # Weekly volatility

                    historical_value = current_value * market_factor
                    historical_pnl = historical_value - current_cost
                    historical_pnl_pct = (historical_pnl / current_cost * 100) if current_cost > 0 else 0

                    snapshot = PortfolioSnapshot(
                        clerk_user_id=user_id,
                        total_value=historical_value,
                        total_cost_basis=current_cost,
                        total_pnl=historical_pnl,
                        total_pnl_percent=historical_pnl_pct,
                        asset_count=asset_count,
                        account_count=len(accounts),
                        snapshot_type="weekly",
                        created_at=snapshot_date
                    )

                    self.db.add(snapshot)

            self.db.commit()

            # Get snapshot count
            total_snapshots = self.db.query(PortfolioSnapshot).count()
            logger.info(f"✅ Created {total_snapshots} historical snapshots")

        except Exception as e:
            logger.error(f"❌ Failed to create snapshots: {e}")
            self.db.rollback()
            raise

    def update_account_balances(self):
        """Update account balances based on current asset values"""
        logger.info("💰 Updating account balances...")

        try:
            accounts = self.db.query(Account).filter(Account.is_active == True).all()

            for account in accounts:
                total_value = sum(
                    asset.shares * asset.current_price
                    for asset in account.assets
                    if asset.is_active
                )
                account.balance = total_value
                account.updated_at = datetime.utcnow()

            self.db.commit()
            logger.info(f"✅ Updated balances for {len(accounts)} accounts")

        except Exception as e:
            logger.error(f"❌ Failed to update balances: {e}")
            self.db.rollback()
            raise

    def _determine_exchange(self, symbol: str) -> str:
        """Determine exchange from symbol"""
        if symbol.endswith("-USD"):
            return "CRYPTO"
        elif symbol.startswith("^"):
            return "INDEX"
        elif symbol in ["SPY", "QQQ", "VTI", "IWM", "EFA", "VWO", "BND", "AGG", "TLT", "HYG"]:
            return "NYSE"
        elif symbol in ["XLK", "XLF", "XLE", "XLV", "XLI", "XLP"]:
            return "NYSE"
        else:
            return random.choice(["NYSE", "NASDAQ"])

    def _determine_asset_type(self, symbol: str) -> str:
        """Determine asset type from symbol"""
        if symbol.endswith("-USD"):
            return "crypto"
        elif symbol.startswith("^"):
            return "index"
        elif symbol in ["SPY", "QQQ", "VTI", "IWM", "EFA", "VWO", "BND", "AGG", "TLT", "HYG", "XLK", "XLF", "XLE", "XLV", "XLI", "XLP"]:
            return "etf"
        else:
            return "stock"

    def generate_summary_report(self):
        """Generate comprehensive initialization summary"""
        try:
            # Get database statistics
            stats = {
                "market_data": self.db.query(MarketData).count(),
                "accounts": self.db.query(Account).count(),
                "assets": self.db.query(Asset).count(),
                "snapshots": self.db.query(PortfolioSnapshot).count()
            }

            # Get user portfolio summaries
            user_summaries = []
            for user_type, user_id in self.demo_users.items():
                accounts = self.db.query(Account).filter(
                    Account.clerk_user_id == user_id
                ).all()

                total_value = sum(account.balance for account in accounts)
                user_summaries.append({
                    "type": user_type,
                    "user_id": user_id,
                    "accounts": len(accounts),
                    "total_value": total_value
                })

            # Generate report
            report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      ENHANCED DATABASE INITIALIZATION SUMMARY                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Mode:                    {self.mode.upper()}                                 ║
║  Authentication:          {'DISABLED (Mock Users)' if settings.DISABLE_AUTH else 'ENABLED (Clerk)'}    ║
║  Database:                {settings.DATABASE_URL.split('/')[-1]}              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                             DATA CREATED                                     ║
║  📊 Market Data Entries:  {stats['market_data']:4d}                          ║
║  🏦 Demo Accounts:        {stats['accounts']:4d}                             ║
║  📈 Asset Holdings:       {stats['assets']:4d}                               ║
║  📸 Portfolio Snapshots:  {stats['snapshots']:4d}                            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                          DEMO USER PORTFOLIOS                               ║
╠══════════════════════════════════════════════════════════════════════════════╣"""

            for user in user_summaries:
                user_type_padded = f"{user['type'].title()}".ljust(15)
                accounts_padded = f"{user['accounts']} accts".ljust(8)
                value_formatted = f"${user['total_value']:,.0f}".rjust(12)
                report += f"\n║  👤 {user_type_padded} {accounts_padded} {value_formatted}                ║"

            report += f"""
╠══════════════════════════════════════════════════════════════════════════════╣
║                             API ENDPOINTS                                    ║
║  Portfolio Summary:       GET /api/v1/portfolio/summary                     ║
║  Update Prices:          POST /api/v1/portfolio/update-prices               ║
║  Create Account:         POST /api/v1/accounts/                             ║
║  Add Asset:              POST /api/v1/assets/                               ║
║  Performance Analytics:   GET /api/v1/portfolios/performance                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                            NEXT STEPS                                       ║
║  1. Start API server:     python run.py                                     ║
║  2. View documentation:   http://localhost:8000/docs                        ║
║  3. Test portfolio API:   http://localhost:8000/api/v1/portfolio/summary    ║
║  4. Update prices:        POST /api/v1/portfolio/update-prices              ║
{"║  5. Configure Clerk:      Set DISABLE_AUTH=false in .env                    ║" if settings.DISABLE_AUTH else ""}
╚══════════════════════════════════════════════════════════════════════════════╝
"""

            logger.info(report)

        except Exception as e:
            logger.error(f"❌ Failed to generate summary: {e}")

    async def run_initialization(self, clear_existing: bool = False) -> bool:
        """Run complete initialization process"""
        try:
            logger.info("🚀 Starting Enhanced Database Initialization")
            logger.info(f"Mode: {self.mode.upper()}")
            logger.info(f"Authentication: {'DISABLED (Mock Users)' if settings.DISABLE_AUTH else 'ENABLED (Clerk)'}")
            logger.info("=" * 80)

            # Step 1: Wait for database
            if not await self.wait_for_database():
                return False

            # Step 2: Create tables
            if not self.create_tables():
                return False

            # Step 3: Clear existing data if requested
            if clear_existing:
                self.clear_existing_data()

            # Step 4: Create data based on mode
            if self.mode in ["demo", "comprehensive"]:
                self.create_comprehensive_market_data()
                self.create_realistic_portfolios()
                await self.create_historical_snapshots()
                self.update_account_balances()
            elif self.mode == "minimal":
                # Create minimal data for testing
                self.create_comprehensive_market_data()  # Still need market data
                self.create_realistic_portfolios()
                self.update_account_balances()

            # Step 5: Generate summary
            self.generate_summary_report()

            logger.info("🎉 Database initialization completed successfully!")
            return True

        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            return False
        finally:
            self.db.close()


async def main():
    """Main initialization function with async support"""
    import argparse

    parser = argparse.ArgumentParser(description='Enhanced Investment Portfolio Database Initialization')
    parser.add_argument('--clear-existing', action='store_true',
                       help='Clear existing data before initialization')
    parser.add_argument('--mode', choices=['minimal', 'demo', 'comprehensive'],
                       default='demo', help='Initialization mode')
    parser.add_argument('--production', action='store_true',
                       help='Production mode (clean schema only)')

    args = parser.parse_args()

    if args.production:
        logger.warning("⚠️  Production mode - creating clean schema only")
        mode = "production"
    else:
        mode = args.mode

    initializer = EnhancedDatabaseInitializer(mode=mode)
    success = await initializer.run_initialization(clear_existing=args.clear_existing)

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
    