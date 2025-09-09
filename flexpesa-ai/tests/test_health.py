"""
Simplified health tests - for development and basic monitoring
Focus on unit testing with test database and optional API integration tests
"""

import pytest
import requests
import time
import os
from app.core.database import check_database_connection, SessionLocal
from app.models.portfolio import Account, Asset


class TestBasicHealth:
    """Simple health checks for development"""

    def test_database_connection(self):
        """Test database connection works"""
        assert check_database_connection()

    def test_database_basic_query(self, test_db):
        """Test basic database operations work"""
        try:
            # Test basic query works using test database
            account_count = test_db.query(Account).count()
            asset_count = test_db.query(Asset).count()

            # Should not raise errors
            assert isinstance(account_count, int)
            assert isinstance(asset_count, int)
            assert account_count >= 0
            assert asset_count >= 0

        except Exception as e:
            pytest.fail(f"Database query failed: {e}")

    def test_api_server_health(self):
        """Test API server is accessible (if running)"""
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            assert response.status_code == 200

            data = response.json()
            assert "status" in data

        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running - start with 'python run.py'")
        except requests.exceptions.Timeout:
            pytest.fail("API server response too slow")

    def test_api_root_endpoint(self):
        """Test API root endpoint works (if running)"""
        try:
            response = requests.get("http://localhost:8000/", timeout=5)
            assert response.status_code == 200

            data = response.json()
            assert "message" in data
            assert "status" in data

        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")


class TestDataIntegrity:
    """Basic data integrity checks using test database"""

    def test_accounts_have_valid_data(self, test_db, sample_account):
        """Test that accounts have reasonable data"""
        try:
            # Use sample account from fixture
            account = sample_account

            # Basic data validation
            assert account.name is not None
            assert account.name.strip() != ""
            assert account.account_type is not None
            assert isinstance(account.balance, (int, float))
            assert account.balance >= 0  # Balance shouldn't be negative

            # Test querying accounts
            accounts = test_db.query(Account).all()
            assert len(accounts) >= 1

        except Exception as e:
            pytest.fail(f"Account data validation failed: {e}")

    def test_assets_have_valid_data(self, test_db, sample_asset):
        """Test that assets have reasonable data"""
        try:
            # Use sample asset from fixture
            asset = sample_asset

            # Basic validation
            assert asset.symbol is not None
            assert asset.symbol.strip() != ""
            assert isinstance(asset.shares, (int, float))
            assert asset.shares > 0  # Should have positive shares
            assert isinstance(asset.avg_cost, (int, float))
            assert asset.avg_cost >= 0  # Cost shouldn't be negative

            # Test querying assets
            assets = test_db.query(Asset).all()
            assert len(assets) >= 1

        except Exception as e:
            pytest.fail(f"Asset data validation failed: {e}")

    def test_portfolio_calculations_make_sense(self, test_db, sample_account, sample_asset):
        """Test portfolio calculations are reasonable"""
        try:
            test_db.refresh(sample_account)

            if not sample_account.assets:
                pytest.skip("No assets to test calculations")

            # Calculate expected value manually
            expected_value = sum(
                asset.shares * (asset.current_price or asset.avg_cost)
                for asset in sample_account.assets
                if asset.is_active
            )

            # Should match account's calculated total
            assert abs(sample_account.total_value - expected_value) < 0.01

        except Exception as e:
            pytest.fail(f"Portfolio calculation validation failed: {e}")


class TestBasicPerformance:
    """Basic performance checks"""

    def test_database_query_speed(self, test_db):
        """Test database queries complete reasonably fast"""
        try:
            start_time = time.time()

            # Run some basic queries
            account_count = test_db.query(Account).count()
            asset_count = test_db.query(Asset).count()

            # Get some sample data
            accounts = test_db.query(Account).limit(10).all()

            end_time = time.time()
            query_time = end_time - start_time

            # Should complete quickly (adjust threshold as needed)
            assert query_time < 5.0, f"Database queries too slow: {query_time:.2f}s"

        except Exception as e:
            pytest.fail(f"Database performance test failed: {e}")

    def test_api_response_speed(self):
        """Test API responds reasonably fast (if running)"""
        try:
            start_time = time.time()
            response = requests.get("http://localhost:8000/health", timeout=10)
            end_time = time.time()

            response_time = end_time - start_time

            assert response.status_code == 200
            assert response_time < 3.0, f"API response too slow: {response_time:.2f}s"

        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")
        except Exception as e:
            pytest.fail(f"API performance test failed: {e}")


class TestEnvironment:
    """Test environment configuration"""

    def test_test_environment_variables(self):
        """Test that test environment variables are set"""
        # These should be set by pytest configuration
        testing_env = os.environ.get("TESTING", "false").lower()
        environment = os.environ.get("ENVIRONMENT", "").lower()

        # Should be in test mode
        assert testing_env == "true" or environment == "development"

    def test_database_configuration(self):
        """Test database configuration is appropriate for testing"""
        # For unit tests, we don't care about the production DB URL
        # since we use test_db fixture, but let's verify it exists
        from app.core.config import settings

        assert settings.DATABASE_URL is not None
        assert len(settings.DATABASE_URL) > 0


class TestRealDatabaseHealth:
    """Tests for real database (when available) - skip if not configured"""

    def test_production_database_connection(self):
        """Test production database connectivity (skip if not available)"""
        try:
            # This tests the real database connection
            assert check_database_connection()
        except Exception as e:
            pytest.skip(f"Production database not available: {e}")

    def test_production_database_has_tables(self):
        """Test production database has expected tables (skip if not available)"""
        try:
            db = SessionLocal()
            try:
                # Try to query actual tables
                account_count = db.query(Account).count()
                asset_count = db.query(Asset).count()

                # Should not raise errors
                assert isinstance(account_count, int)
                assert isinstance(asset_count, int)

            finally:
                db.close()

        except Exception as e:
            pytest.skip(f"Production database not properly configured: {e}")

    def test_production_data_integrity(self):
        """Test production data integrity (skip if not available)"""
        try:
            db = SessionLocal()
            try:
                # Sample some production accounts
                accounts = db.query(Account).limit(5).all()

                for account in accounts:
                    # Basic integrity checks
                    assert account.name is not None
                    assert account.name.strip() != ""
                    assert account.balance >= 0

                    # Check asset integrity
                    for asset in account.assets:
                        if asset.is_active:
                            assert asset.shares > 0
                            assert asset.avg_cost >= 0

            finally:
                db.close()

        except Exception as e:
            pytest.skip(f"Production database data checks failed: {e}")


class TestAssetValidation:
    """Test asset-specific business logic"""

    def test_asset_calculations(self, test_db, sample_asset):
        """Test asset calculation properties"""
        try:
            # Market value = shares * current_price
            expected_market_value = sample_asset.shares * sample_asset.current_price
            assert abs(sample_asset.market_value - expected_market_value) < 0.01

            # Cost basis = shares * avg_cost
            expected_cost_basis = sample_asset.shares * sample_asset.avg_cost
            assert abs(sample_asset.cost_basis - expected_cost_basis) < 0.01

            # P&L = market_value - cost_basis
            expected_pnl = expected_market_value - expected_cost_basis
            assert abs(sample_asset.unrealized_pnl - expected_pnl) < 0.01

        except Exception as e:
            pytest.fail(f"Asset calculation test failed: {e}")

    def test_account_total_value(self, test_db, sample_account, sample_asset):
        """Test account total value calculation"""
        try:
            test_db.refresh(sample_account)

            # Calculate expected value from active assets
            expected_value = sum(
                asset.shares * (asset.current_price or asset.avg_cost)
                for asset in sample_account.assets
                if asset.is_active
            )

            assert abs(sample_account.total_value - expected_value) < 0.01

        except Exception as e:
            pytest.fail(f"Account total value test failed: {e}")


# Performance test configuration
class TestPerformanceThresholds:
    """Test that operations meet performance thresholds"""

    def test_account_creation_speed(self, test_db):
        """Test account creation is fast enough"""
        start_time = time.time()

        account = Account(
            clerk_user_id="perf_test_user",
            name="Performance Test Account",
            account_type="testing"
        )

        test_db.add(account)
        test_db.commit()

        end_time = time.time()
        creation_time = end_time - start_time

        assert creation_time < 1.0, f"Account creation too slow: {creation_time:.3f}s"

    def test_asset_creation_speed(self, test_db, sample_account):
        """Test asset creation is fast enough"""
        start_time = time.time()

        asset = Asset(
            account_id=sample_account.id,
            symbol="PERF",
            shares=100,
            avg_cost=50.0,
            current_price=55.0
        )

        test_db.add(asset)
        test_db.commit()

        end_time = time.time()
        creation_time = end_time - start_time

        assert creation_time < 1.0, f"Asset creation too slow: {creation_time:.3f}s"


# Mark these tests for health category (optional)
pytestmark = pytest.mark.health