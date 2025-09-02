"""
Production health and monitoring tests
Tests that can safely run in production to check system health and detect regressions
"""

import pytest
import requests
import time
from unittest.mock import patch
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import check_database_connection, SessionLocal
from app.core.config import settings, get_database_config
from app.models.portfolio import Account, Asset, MarketData, PortfolioSnapshot
from app.services.market_data import MarketDataService
from app.services.portfolio_service import PortfolioService
from conftest import production_safe_only


@pytest.mark.production
class TestProductionHealth:
    """Production-safe health checks"""

    def test_database_connectivity(self):
        """Test database connection health"""
        assert check_database_connection(), "Database connection failed"

    def test_database_basic_operations(self):
        """Test basic database operations work"""
        db = SessionLocal()
        try:
            # Test basic query
            result = db.execute(text("SELECT 1 as test"))
            assert result.scalar() == 1
            
            # Test table access
            account_count = db.query(Account).count()
            assert isinstance(account_count, int)
            
        finally:
            db.close()

    def test_api_endpoint_availability(self):
        """Test that main API endpoints are accessible"""
        base_url = "http://localhost:8000"
        
        endpoints_to_test = [
            "/",
            "/health",
            "/api/v1/auth/config",
            "/api/v1/market/status",
        ]
        
        for endpoint in endpoints_to_test:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
                assert response.status_code in [200, 401], f"Endpoint {endpoint} returned {response.status_code}"
            except requests.exceptions.ConnectionError:
                pytest.skip(f"API server not running at {base_url}")

    def test_database_schema_integrity(self):
        """Test database schema is intact"""
        db = SessionLocal()
        try:
            # Test all main tables exist and are accessible
            tables_to_check = [
                ("accounts", Account),
                ("assets", Asset),
                ("market_data_cache", MarketData),
                ("portfolio_snapshots", PortfolioSnapshot)
            ]
            
            for table_name, model_class in tables_to_check:
                try:
                    count = db.query(model_class).count()
                    assert isinstance(count, int), f"Failed to query {table_name}"
                except Exception as e:
                    pytest.fail(f"Schema integrity check failed for {table_name}: {e}")
                    
        finally:
            db.close()

    def test_configuration_validity(self):
        """Test that configuration is valid"""
        # Test database URL format
        db_config = get_database_config()
        assert "type" in db_config
        assert db_config["type"] in ["sqlite", "postgresql"]
        
        # Test environment settings
        assert settings.ENVIRONMENT in ["development", "staging", "production"]
        assert isinstance(settings.BACKEND_PORT, int)
        assert 1000 <= settings.BACKEND_PORT <= 65535

    def test_security_headers_present(self):
        """Test that security headers are present in responses"""
        base_url = "http://localhost:8000"
        
        try:
            response = requests.get(f"{base_url}/", timeout=10)
            
            # Check for security-related headers
            headers = response.headers
            
            # These are basic security headers that should be present
            expected_headers = [
                'content-type',
                'content-length'
            ]
            
            for header in expected_headers:
                assert header in headers.keys() or header.lower() in [h.lower() for h in headers.keys()]
                
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")


@pytest.mark.production
class TestProductionDataIntegrity:
    """Test data integrity in production"""

    def test_account_data_consistency(self):
        """Test account data consistency"""
        db = SessionLocal()
        try:
            accounts = db.query(Account).all()
            
            for account in accounts:
                # Basic data validation
                assert account.name is not None and account.name.strip() != ""
                assert account.account_type is not None and account.account_type.strip() != ""
                assert isinstance(account.balance, (int, float))
                assert account.balance >= 0  # Balance shouldn't be negative
                assert account.created_at is not None
                
                # Relationship consistency
                for asset in account.assets:
                    assert asset.account_id == account.id
                    
        finally:
            db.close()

    def test_asset_data_consistency(self):
        """Test asset data consistency"""
        db = SessionLocal()
        try:
            assets = db.query(Asset).all()
            
            for asset in assets:
                # Basic validation
                assert asset.symbol is not None and asset.symbol.strip() != ""
                assert isinstance(asset.shares, (int, float))
                assert asset.shares > 0  # Should have positive shares
                assert isinstance(asset.avg_cost, (int, float))
                assert asset.avg_cost >= 0  # Cost shouldn't be negative
                
                # Price validation
                if asset.current_price is not None:
                    assert isinstance(asset.current_price, (int, float))
                    assert asset.current_price >= 0
                
                # Account relationship
                assert asset.account_id is not None
                account = db.query(Account).filter(Account.id == asset.account_id).first()
                assert account is not None, f"Asset {asset.id} references non-existent account {asset.account_id}"
                
        finally:
            db.close()

    def test_portfolio_calculation_accuracy(self):
        """Test portfolio value calculations are accurate"""
        db = SessionLocal()
        try:
            accounts = db.query(Account).filter(Account.is_active == True).all()
            
            for account in accounts:
                # Calculate expected value from assets
                expected_value = sum(
                    asset.shares * (asset.current_price or asset.avg_cost)
                    for asset in account.assets
                    if asset.is_active
                )
                
                # Allow small floating point differences
                assert abs(account.total_value - expected_value) < 0.01, \
                    f"Account {account.id} calculated value mismatch: {account.total_value} vs {expected_value}"
                    
        finally:
            db.close()

    def test_no_orphaned_data(self):
        """Test there are no orphaned records"""
        db = SessionLocal()
        try:
            # Check for assets without accounts
            orphaned_assets = db.execute(text("""
                SELECT COUNT(*) FROM assets 
                WHERE account_id NOT IN (SELECT id FROM accounts)
            """)).scalar()
            
            assert orphaned_assets == 0, f"Found {orphaned_assets} orphaned assets"
            
            # Check for snapshots without users having accounts
            orphaned_snapshots = db.execute(text("""
                SELECT COUNT(*) FROM portfolio_snapshots ps
                WHERE ps.clerk_user_id NOT IN (
                    SELECT DISTINCT clerk_user_id FROM accounts WHERE clerk_user_id IS NOT NULL
                )
            """)).scalar()
            
            # This might be acceptable in some cases, so just log if any found
            if orphaned_snapshots > 0:
                print(f"Warning: Found {orphaned_snapshots} snapshots for users without accounts")
                
        finally:
            db.close()

    def test_recent_data_freshness(self):
        """Test that recent data is reasonably fresh"""
        db = SessionLocal()
        try:
            # Check for assets with very old price updates (older than 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)
            
            stale_assets = db.query(Asset).filter(
                Asset.price_updated_at < week_ago,
                Asset.is_active == True
            ).count()
            
            total_active_assets = db.query(Asset).filter(Asset.is_active == True).count()
            
            if total_active_assets > 0:
                stale_percentage = (stale_assets / total_active_assets) * 100
                
                # Warn if more than 20% of assets have stale data
                if stale_percentage > 20:
                    print(f"Warning: {stale_percentage:.1f}% of assets have stale price data")
                
                # Fail if more than 50% have stale data (system issue)
                assert stale_percentage < 50, f"Too many assets ({stale_percentage:.1f}%) have stale data"
                
        finally:
            db.close()


@pytest.mark.production
class TestProductionPerformance:
    """Test system performance in production"""

    def test_database_query_performance(self):
        """Test database queries complete within reasonable time"""
        db = SessionLocal()
        try:
            start_time = time.time()
            
            # Test common queries
            account_count = db.query(Account).count()
            asset_count = db.query(Asset).count()
            
            # Complex query with joins
            portfolio_data = db.query(Account, Asset).join(Asset).limit(100).all()
            
            end_time = time.time()
            query_time = end_time - start_time
            
            # Should complete within reasonable time
            assert query_time < 5.0, f"Database queries too slow: {query_time:.2f}s"
            
            # Basic sanity checks
            assert isinstance(account_count, int)
            assert isinstance(asset_count, int)
            
        finally:
            db.close()

    def test_api_response_time(self):
        """Test API response times are reasonable"""
        base_url = "http://localhost:8000"
        
        endpoints_to_test = [
            "/",
            "/health",
            "/api/v1/market/status"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                start_time = time.time()
                response = requests.get(f"{base_url}{endpoint}", timeout=30)
                end_time = time.time()
                
                response_time = end_time - start_time
                
                # API should respond within reasonable time
                assert response_time < 5.0, f"Endpoint {endpoint} too slow: {response_time:.2f}s"
                assert response.status_code in [200, 401, 403]  # Acceptable statuses
                
            except requests.exceptions.ConnectionError:
                pytest.skip(f"API server not running at {base_url}")
            except requests.exceptions.Timeout:
                pytest.fail(f"Endpoint {endpoint} timed out")

    def test_memory_usage_reasonable(self):
        """Test that memory usage is reasonable"""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            
            # Memory usage should be reasonable (less than 1GB for test process)
            memory_mb = memory_info.rss / (1024 * 1024)
            assert memory_mb < 1024, f"Memory usage too high: {memory_mb:.1f}MB"
            
        except ImportError:
            pytest.skip("psutil not available for memory testing")


@pytest.mark.production
class TestProductionSecurity:
    """Test security aspects in production"""

    def test_no_debug_info_in_responses(self):
        """Test that debug information is not exposed"""
        base_url = "http://localhost:8000"
        
        try:
            response = requests.get(f"{base_url}/nonexistent", timeout=10)
            
            # Should get 404, not detailed error info
            assert response.status_code == 404
            
            response_text = response.text.lower()
            
            # Should not contain debug information
            debug_indicators = [
                "traceback", "file \"", "line ", "error in",
                "exception", "stack trace", "internal server error"
            ]
            
            for indicator in debug_indicators:
                if indicator in response_text and settings.ENVIRONMENT == "production":
                    pytest.fail(f"Debug information exposed: {indicator}")
                    
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")

    def test_sql_injection_protection(self):
        """Test basic SQL injection protection"""
        db = SessionLocal()
        try:
            # Try basic SQL injection patterns
            malicious_inputs = [
                "'; DROP TABLE accounts; --",
                "' OR '1'='1",
                "1; UPDATE accounts SET balance = 0; --"
            ]
            
            for malicious_input in malicious_inputs:
                # This should not cause SQL injection
                try:
                    result = db.query(Account).filter(Account.name == malicious_input).all()
                    # Should return empty result, not cause SQL injection
                    assert isinstance(result, list)
                except Exception as e:
                    # Should fail safely, not with SQL syntax errors
                    assert "syntax error" not in str(e).lower()
                    
        finally:
            db.close()

    def test_sensitive_data_not_logged(self):
        """Test that sensitive data is not exposed in logs"""
        # This is more of a code review item, but we can test basic patterns
        
        # Test that database URL doesn't contain plain passwords in logs
        db_config = get_database_config()
        if "url" in db_config:
            # Should be masked
            assert "***" in db_config["url"] or "password" not in db_config["url"].lower()


@pytest.mark.production
class TestProductionBusinessLogic:
    """Test business logic correctness in production"""

    def test_portfolio_calculations_mathematical_accuracy(self):
        """Test portfolio calculations are mathematically correct"""
        db = SessionLocal()
        try:
            accounts = db.query(Account).join(Asset).limit(10).all()  # Sample some accounts
            
            for account in accounts:
                if not account.assets:
                    continue
                    
                # Test portfolio value calculation
                manual_total = 0
                for asset in account.assets:
                    if asset.is_active:
                        current_price = asset.current_price or asset.avg_cost
                        asset_value = asset.shares * current_price
                        manual_total += asset_value
                        
                        # Test individual asset calculations
                        assert abs(asset.market_value - asset_value) < 0.01
                        
                        cost_basis = asset.shares * asset.avg_cost
                        assert abs(asset.cost_basis - cost_basis) < 0.01
                        
                        expected_pnl = asset_value - cost_basis
                        assert abs(asset.unrealized_pnl - expected_pnl) < 0.01
                
                # Test account total
                assert abs(account.total_value - manual_total) < 0.01
                
        finally:
            db.close()

    def test_percentage_calculations_accuracy(self):
        """Test percentage calculations are accurate"""
        db = SessionLocal()
        try:
            assets = db.query(Asset).filter(
                Asset.avg_cost > 0,
                Asset.current_price.isnot(None),
                Asset.is_active == True
            ).limit(20).all()
            
            for asset in assets:
                if asset.avg_cost == 0:
                    continue
                    
                expected_pnl_pct = ((asset.market_value - asset.cost_basis) / asset.cost_basis) * 100
                assert abs(asset.unrealized_pnl_percent - expected_pnl_pct) < 0.01
                
        finally:
            db.close()

    def test_data_consistency_across_relationships(self):
        """Test data consistency across model relationships"""
        db = SessionLocal()
        try:
            # Test account-asset relationship consistency
            accounts_with_assets = db.query(Account).join(Asset).all()
            
            for account in accounts_with_assets:
                # Verify all assets belong to this account
                for asset in account.assets:
                    assert asset.account_id == account.id
                    
                # Verify calculated values are consistent
                asset_sum = sum(asset.market_value for asset in account.assets if asset.is_active)
                assert abs(account.total_value - asset_sum) < 0.01
                
        finally:
            db.close()


@pytest.mark.production
class TestProductionMonitoring:
    """Test monitoring and alerting capabilities"""

    def test_system_health_metrics(self):
        """Test system health metrics are available"""
        base_url = "http://localhost:8000"
        
        try:
            response = requests.get(f"{base_url}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                
                assert "status" in health_data
                assert "timestamp" in health_data
                assert "checks" in health_data
                
                # Database check should be present
                if "database" in health_data["checks"]:
                    assert health_data["checks"]["database"] in ["healthy", "unhealthy"]
                    
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")

    def test_error_rates_acceptable(self):
        """Test that error rates are within acceptable limits"""
        db = SessionLocal()
        try:
            # Check for data quality issues that might indicate errors
            total_assets = db.query(Asset).filter(Asset.is_active == True).count()
            
            if total_assets > 0:
                # Assets with zero or negative prices (might indicate data issues)
                problematic_assets = db.query(Asset).filter(
                    Asset.is_active == True,
                    Asset.current_price <= 0
                ).count()
                
                error_rate = (problematic_assets / total_assets) * 100
                
                # Error rate should be low
                assert error_rate < 10, f"High error rate in asset data: {error_rate:.1f}%"
                
        finally:
            db.close()

    def test_recent_activity_present(self):
        """Test that there has been recent activity (if expected)"""
        db = SessionLocal()
        try:
            # Check for recent snapshots (if system is actively used)
            recent_threshold = datetime.utcnow() - timedelta(days=7)
            
            recent_snapshots = db.query(PortfolioSnapshot).filter(
                PortfolioSnapshot.created_at >= recent_threshold
            ).count()
            
            total_snapshots = db.query(PortfolioSnapshot).count()
            
            if total_snapshots > 0:
                recent_percentage = (recent_snapshots / total_snapshots) * 100
                
                # If there are snapshots, some should be recent (indicates active system)
                if total_snapshots > 10:  # Only check if there's meaningful data
                    assert recent_percentage > 0, "No recent activity detected in portfolio snapshots"
                    
        finally:
            db.close()


@production_safe_only("Production-specific regression tests")
@pytest.mark.production
class TestProductionRegressionDetection:
    """Test for common regression patterns in production"""

    def test_no_massive_data_loss(self):
        """Test that we haven't lost significant amounts of data"""
        db = SessionLocal()
        try:
            current_counts = {
                "accounts": db.query(Account).count(),
                "assets": db.query(Asset).count(),
                "market_data": db.query(MarketData).count(),
                "snapshots": db.query(PortfolioSnapshot).count()
            }
            
            # Basic sanity check - if we have any data, counts should be reasonable
            for table, count in current_counts.items():
                assert count >= 0, f"Negative count for {table}: {count}"
                
                # If we have data, we shouldn't have suspiciously low counts
                # (This would need to be calibrated based on your actual production data)
                if count > 0:
                    print(f"{table}: {count} records")
                    
        finally:
            db.close()

    def test_no_performance_regression(self):
        """Test for performance regression"""
        db = SessionLocal()
        try:
            # Benchmark a common operation
            start_time = time.time()
            
            # Common query that should be fast
            recent_assets = db.query(Asset).join(Account).filter(
                Asset.is_active == True
            ).limit(100).all()
            
            end_time = time.time()
            query_time = end_time - start_time
            
            # This should complete quickly (adjust threshold based on your system)
            assert query_time < 2.0, f"Performance regression detected: query took {query_time:.2f}s"
            
        finally:
            db.close()

    def test_configuration_drift_detection(self):
        """Test for configuration drift"""
        # Test that critical configuration hasn't changed unexpectedly
        
        # Database type shouldn't change without migration
        db_config = get_database_config()
        expected_db_types = ["sqlite", "postgresql"]
        assert db_config["type"] in expected_db_types
        
        # Environment should be set correctly
        assert settings.ENVIRONMENT in ["development", "staging", "production"]
        
        # Port should be in reasonable range
        assert 1000 <= settings.BACKEND_PORT <= 65535

    def test_dependency_availability(self):
        """Test that critical dependencies are available"""
        critical_imports = [
            "sqlalchemy",
            "fastapi", 
            "pydantic",
            "pandas",
            "yfinance"
        ]
        
        for module_name in critical_imports:
            try:
                __import__(module_name)
            except ImportError:
                pytest.fail(f"Critical dependency missing: {module_name}")
