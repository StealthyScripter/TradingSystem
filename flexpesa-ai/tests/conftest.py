"""
Test configuration
Handles import path and database validation issues
"""

import pytest
import os
import sys
from pathlib import Path

# Add project root to Python path FIRST
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set test environment BEFORE importing app (this is critical)
os.environ.update({
    "TESTING": "true",
    "ENVIRONMENT": "testing",
    "DEBUG": "true",
    "DISABLE_AUTH": "true",
    "DATABASE_URL": "sqlite:///:memory:",
    "MOCK_USER_ID": "test_user_123",
    "MOCK_USER_EMAIL": "test@example.com",
    "MOCK_USER_FIRST_NAME": "Test",
    "MOCK_USER_LAST_NAME": "User"
})

# Import after path and environment are set
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# Import app components
from app.main import app
from app.core.database import get_db, Base
from app.models.portfolio import Account, Asset

@pytest.fixture(scope="function")
def test_db():
    """Create clean test database for each test"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        # Clean up
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_client(test_db):
    """Create test client with database override"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    # Clean up overrides
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
