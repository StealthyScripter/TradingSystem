"""
Test configuration and fixtures for Investment Portfolio API tests
"""

import pytest
import os
import asyncio
from typing import Generator, Dict, Any
from unittest.mock import patch, MagicMock
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Import app components
from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings
from app.models.portfolio import Account, Asset, MarketData, PortfolioSnapshot
from app.services.portfolio_service import PortfolioService
from app.services.market_data import MarketDataService

# Test configuration
TEST_DATABASE_URL = "sqlite:///./test_portfolio.db"
PRODUCTION_SAFE_MODE = os.getenv("PRODUCTION_SAFE_MODE", "false").lower() == "true"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_database_engine():
    """Create test database engine"""
    if PRODUCTION_SAFE_MODE:
        # In production safe mode, use a completely isolated test database
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            test_db_url = f"sqlite:///{tmp.name}"
    else:
        test_db_url = TEST_DATABASE_URL

    engine = create_engine(
        test_db_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False  # Set to True for SQL debugging
    )

    # Create tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Cleanup
    if not PRODUCTION_SAFE_MODE:
        Base.metadata.drop_all(bind=engine)
        if os.path.exists("test_portfolio.db"):
            os.remove("test_portfolio.db")

@pytest.fixture(scope="function")
def test_db_session(test_database_engine) -> Generator[Session, None, None]:
    """Create test database session"""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_database_engine
    )

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture(scope="function")
def test_client(test_db_session) -> TestClient:
    """Create test client with database override"""
    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    yield client

    app.dependency_overrides.clear()

@pytest.fixture
def mock_authenticated_user():
    """Mock authenticated user for testing protected endpoints"""
    mock_user = {
        "sub": "test_user_12345",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User"
    }

    def mock_get_current_user():
        return mock_user

    return mock_user

@pytest.fixture
def sample_account_data():
    """Sample account data for testing"""
    return {
        "name": "Test Investment Account",
        "account_type": "brokerage",
        "description": "Test account for portfolio testing",
        "currency": "USD"
    }

@pytest.fixture
def sample_asset_data():
    """Sample asset data for testing"""
    return {
        "symbol": "TEST",
        "shares": 100,
        "avg_cost": 50.0,
        "current_price": 55.0,
        "asset_type": "stock"
    }

@pytest.fixture
def sample_portfolio_data(test_db_session, mock_authenticated_user):
    """Create sample portfolio data for testing"""
    # Create test account
    account = Account(
        clerk_user_id=mock_authenticated_user["sub"],
        name="Test Portfolio",
        account_type="brokerage",
        description="Test portfolio for unit tests",
        currency="USD",
        is_active=True
    )
    test_db_session.add(account)
    test_db_session.commit()
    test_db_session.refresh(account)

    # Create test assets
    test_assets = [
        {
            "symbol": "AAPL",
            "shares": 10,
            "avg_cost": 150.0,
            "current_price": 155.0,
            "asset_type": "stock"
        },
        {
            "symbol": "MSFT",
            "shares": 5,
            "avg_cost": 300.0,
            "current_price": 310.0,
            "asset_type": "stock"
        },
        {
            "symbol": "BTC-USD",
            "shares": 0.1,
            "avg_cost": 40000.0,
            "current_price": 42000.0,
            "asset_type": "crypto"
        }
    ]

    assets = []
    for asset_data in test_assets:
        asset = Asset(
            account_id=account.id,
            symbol=asset_data["symbol"],
            shares=asset_data["shares"],
            avg_cost=asset_data["avg_cost"],
            current_price=asset_data["current_price"],
            asset_type=asset_data["asset_type"],
            currency="USD",
            is_active=True
        )
        test_db_session.add(asset)
        assets.append(asset)

    test_db_session.commit()

    return {
        "account": account,
        "assets": assets,
        "user": mock_authenticated_user
    }

@pytest.fixture
def mock_market_data_service():
    """Mock market data service to avoid external API calls during testing"""
    with patch('app.services.portfolio_service.MarketDataService') as mock_service:
        mock_instance = MagicMock()
        mock_instance.get_current_prices.return_value = {
            'AAPL': 155.50,
            'MSFT': 310.20,
            'GOOGL': 140.30,
            'TSLA': 200.00,
            'BTC-USD': 42500.00,
            'ETH-USD': 2600.00,
            'TEST': 55.00
        }
        mock_service.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_ai_service():
    """Mock AI service for testing without external dependencies"""
    with patch('app.services.portfolio_service.LightweightAIService') as mock_ai:
        mock_instance = MagicMock()
        mock_instance.analyze_portfolio_fast.return_value = {
            "total_value": 10000.0,
            "diversity_score": 0.7,
            "risk_score": 3.5,
            "sentiment_score": 0.2,
            "technical_score": 0.1,
            "recommendation": "HOLD",
            "confidence": 0.8,
            "insights": [
                "Portfolio is well diversified",
                "Market sentiment is slightly positive",
                "Technical indicators suggest stability"
            ],
            "analysis_type": "test"
        }
        mock_instance.analyze_asset_fast.return_value = {
            "symbol": "TEST",
            "recommendation": "HOLD",
            "confidence": 0.7
        }
        mock_ai.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def portfolio_service(test_db_session, mock_market_data_service, mock_ai_service):
    """Create portfolio service instance for testing"""
    return PortfolioService(test_db_session)

# Test data generators
def create_test_market_data(symbols: list = None) -> Dict[str, Dict[str, Any]]:
    """Generate test market data"""
    if symbols is None:
        symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "BTC-USD"]

    market_data = {}
    base_prices = {
        "AAPL": 155.50,
        "MSFT": 310.20,
        "GOOGL": 140.30,
        "TSLA": 200.00,
        "BTC-USD": 42500.00,
        "ETH-USD": 2600.00
    }

    for symbol in symbols:
        price = base_prices.get(symbol, 100.00)
        market_data[symbol] = {
            "symbol": symbol,
            "current_price": price,
            "day_change": price * 0.02,  # 2% change
            "day_change_percent": 2.0,
            "volume": 1000000,
            "market_cap": price * 1000000
        }

    return market_data

# Test configuration helpers
def is_production_environment() -> bool:
    """Check if running in production environment"""
    return settings.ENVIRONMENT == "production"

def skip_if_production(reason: str = "Skipped in production environment"):
    """Decorator to skip tests in production"""
    return pytest.mark.skipif(
        is_production_environment() and not PRODUCTION_SAFE_MODE,
        reason=reason
    )

def production_safe_only(reason: str = "Only runs in production safe mode"):
    """Decorator to only run tests in production safe mode"""
    return pytest.mark.skipif(
        not PRODUCTION_SAFE_MODE,
        reason=reason
    )

# Custom assertions
def assert_valid_portfolio_response(response_data: Dict[str, Any]):
    """Assert that portfolio response has valid structure"""
    required_fields = ["user_id", "accounts", "summary", "analysis", "last_updated"]
    for field in required_fields:
        assert field in response_data, f"Missing required field: {field}"

    # Check summary structure
    summary = response_data["summary"]
    summary_fields = ["total_value", "total_cost_basis", "total_pnl", "total_accounts", "total_assets"]
    for field in summary_fields:
        assert field in summary, f"Missing summary field: {field}"
        assert isinstance(summary[field], (int, float)), f"Invalid type for {field}"

def assert_valid_account_response(response_data: Dict[str, Any]):
    """Assert that account response has valid structure"""
    required_fields = ["id", "name", "account_type", "balance", "assets"]
    for field in required_fields:
        assert field in response_data, f"Missing required field: {field}"

    assert isinstance(response_data["balance"], (int, float))
    assert isinstance(response_data["assets"], list)

def assert_valid_asset_response(response_data: Dict[str, Any]):
    """Assert that asset response has valid structure"""
    required_fields = ["id", "symbol", "shares", "avg_cost", "current_price", "account_id"]
    for field in required_fields:
        assert field in response_data, f"Missing required field: {field}"

    assert isinstance(response_data["shares"], (int, float))
    assert isinstance(response_data["avg_cost"], (int, float))
    assert isinstance(response_data["current_price"], (int, float))

# Test markers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.production = pytest.mark.production
pytest.mark.slow = pytest.mark.slow
