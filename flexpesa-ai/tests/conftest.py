"""
Basic test configuration and fixtures
Simple setup for testing core functionality
"""

import pytest
import os
import tempfile
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# Import app components
from app.main import app
from app.core.database import get_db, Base
from app.models.portfolio import Account, Asset

# Test configuration
TEST_DATABASE_URL = "sqlite:///./test_portfolio.db"

@pytest.fixture(scope="function")
def test_db():
    """Create test database"""
    # Use in-memory SQLite for tests
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def test_client(test_db):
    """Create test client with database override"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    yield client

    app.dependency_overrides.clear()

@pytest.fixture
def sample_user():
    """Sample user data for testing"""
    return {
        "sub": "test_user_123",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User"
    }

@pytest.fixture
def sample_account(test_db, sample_user):
    """Create sample account for testing"""
    account = Account(
        clerk_user_id=sample_user["sub"],
        name="Test Account",
        account_type="brokerage",
        description="Test account for basic tests",
        currency="USD",
        is_active=True
    )
    test_db.add(account)
    test_db.commit()
    test_db.refresh(account)
    return account

@pytest.fixture
def sample_asset(test_db, sample_account):
    """Create sample asset for testing"""
    asset = Asset(
        account_id=sample_account.id,
        symbol="AAPL",
        shares=10,
        avg_cost=150.0,
        current_price=155.0,
        asset_type="stock",
        currency="USD",
        is_active=True
    )
    test_db.add(asset)
    test_db.commit()
    test_db.refresh(asset)
    return asset

# Helper functions
def assert_account_valid(account_data):
    """Assert account data is valid"""
    required_fields = ["id", "name", "account_type"]
    for field in required_fields:
        assert field in account_data
        assert account_data[field] is not None

def assert_asset_valid(asset_data):
    """Assert asset data is valid"""
    required_fields = ["id", "symbol", "shares", "avg_cost", "account_id"]
    for field in required_fields:
        assert field in asset_data
        assert asset_data[field] is not None