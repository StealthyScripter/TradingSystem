"""
End-to-end integration tests
Tests complete workflows and system integration
"""

import pytest
import asyncio
import time
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.schemas.portfolio import AccountCreate, AssetCreate
from app.services.portfolio_service import PortfolioService
from app.services.perfomance import PerformanceService
from conftest import (
    assert_valid_portfolio_response, 
    assert_valid_account_response,
    assert_valid_asset_response,
    skip_if_production
)


class TestCompletePortfolioWorkflow:
    """Test complete portfolio management workflow"""

    @patch('app.api.routes.get_current_user')
    def test_full_portfolio_creation_workflow(self, mock_auth, test_client, mock_market_data_service, mock_ai_service):
        """Test complete workflow: create account -> add assets -> get summary"""
        user_id = "workflow_test_user"
        mock_auth.return_value = {"sub": user_id, "email": "test@example.com"}
        
        # Step 1: Create account
        account_data = {
            "name": "Integration Test Account",
            "account_type": "brokerage"
        }
        
        account_response = test_client.post("/api/v1/accounts/", json=account_data)
        assert account_response.status_code == 200
        
        account = account_response.json()
        assert_valid_account_response(account)
        account_id = account["id"]
        
        # Step 2: Add multiple assets
        assets_to_add = [
            {"symbol": "AAPL", "shares": 100, "avg_cost": 150.0},
            {"symbol": "MSFT", "shares": 50, "avg_cost": 300.0},
            {"symbol": "GOOGL", "shares": 25, "avg_cost": 120.0}
        ]
        
        for asset_data in assets_to_add:
            asset_data["account_id"] = account_id
            asset_response = test_client.post("/api/v1/assets/", json=asset_data)
            assert asset_response.status_code == 200
            assert_valid_asset_response(asset_response.json())
        
        # Step 3: Update prices
        mock_market_data_service.get_current_prices.return_value = {
            "AAPL": 160.0,
            "MSFT": 320.0,
            "GOOGL": 130.0
        }
        
        price_response = test_client.post("/api/v1/portfolio/update-prices")
        assert price_response.status_code == 200
        
        price_data = price_response.json()
        assert price_data["updated_assets"] == 3
        
        # Step 4: Get portfolio summary
        summary_response = test_client.get("/api/v1/portfolio/summary")
        assert summary_response.status_code == 200
        
        summary = summary_response.json()
        assert_valid_portfolio_response(summary)
        
        # Verify data consistency
        assert len(summary["accounts"]) == 1
        assert len(summary["accounts"][0]["assets"]) == 3
        assert summary["summary"]["total_assets"] == 3
        assert summary["summary"]["total_value"] > 0

    @patch('app.api.routes.get_current_user')
    def test_multi_account_portfolio_workflow(self, mock_auth, test_client, mock_market_data_service, mock_ai_service):
        """Test workflow with multiple accounts"""
        user_id = "multi_account_user"
        mock_auth.return_value = {"sub": user_id, "email": "test@example.com"}
        
        # Create multiple accounts
        accounts_to_create = [
            {"name": "Brokerage Account", "account_type": "brokerage"},
            {"name": "Retirement Account", "account_type": "retirement"},
            {"name": "Trading Account", "account_type": "trading"}
        ]
        
        account_ids = []
        for account_data in accounts_to_create:
            response = test_client.post("/api/v1/accounts/", json=account_data)
            assert response.status_code == 200
            account_ids.append(response.json()["id"])
        
        # Add assets to different accounts
        assets_distribution = [
            {"account_index": 0, "symbol": "AAPL", "shares": 100, "avg_cost": 150.0},
            {"account_index": 0, "symbol": "MSFT", "shares": 50, "avg_cost": 300.0},
            {"account_index": 1, "symbol": "VTI", "shares": 200, "avg_cost": 220.0},
            {"account_index": 2, "symbol": "TSLA", "shares": 10, "avg_cost": 200.0},
            {"account_index": 2, "symbol": "BTC-USD", "shares": 0.5, "avg_cost": 40000.0}
        ]
        
        for asset_info in assets_distribution:
            asset_data = {
                "account_id": account_ids[asset_info["account_index"]],
                "symbol": asset_info["symbol"],
                "shares": asset_info["shares"],
                "avg_cost": asset_info["avg_cost"]
            }
            response = test_client.post("/api/v1/assets/", json=asset_data)
            assert response.status_code == 200
        
        # Get final portfolio summary
        summary_response = test_client.get("/api/v1/portfolio/summary")
        assert summary_response.status_code == 200
        
        summary = summary_response.json()
        assert len(summary["accounts"]) == 3
        assert summary["summary"]["total_accounts"] == 3
        assert summary["summary"]["total_assets"] == 5

    @patch('app.api.routes.get_current_user')
    def test_portfolio_with_price_updates_and_analysis(self, mock_auth, test_client, mock_market_data_service, mock_ai_service):
        """Test complete workflow including AI analysis"""
        user_id = "analysis_test_user"
        mock_auth.return_value = {"sub": user_id, "email": "test@example.com"}
        
        # Setup portfolio
        account_response = test_client.post("/api/v1/accounts/", json={
            "name": "Analysis Test Account",
            "account_type": "brokerage"
        })
        account_id = account_response.json()["id"]
        
        # Add assets
        test_client.post("/api/v1/assets/", json={
            "account_id": account_id,
            "symbol": "AAPL",
            "shares": 100,
            "avg_cost": 150.0
        })
        
        # Mock market data and AI
        mock_market_data_service.get_current_prices.return_value = {"AAPL": 180.0}
        mock_ai_service.analyze_portfolio_fast.return_value = {
            "recommendation": "HOLD",
            "confidence": 0.8,
            "risk_score": 3.5,
            "insights": ["Portfolio is well positioned"]
        }
        
        # Update prices
        price_response = test_client.post("/api/v1/portfolio/update-prices")
        assert price_response.status_code == 200
        
        # Get summary with analysis
        summary_response = test_client.get("/api/v1/portfolio/summary")
        assert summary_response.status_code == 200
        
        summary = summary_response.json()
        assert "analysis" in summary
        assert summary["analysis"]["recommendation"] == "HOLD"
        
        # Test individual asset analysis
        analysis_response = test_client.post("/api/v1/analysis/asset/AAPL")
        assert analysis_response.status_code == 200


class TestServiceIntegration:
    """Test integration between services"""

    @pytest.mark.asyncio
    async def test_portfolio_service_with_performance_service(self, test_db_session, sample_portfolio_data, mock_market_data_service, mock_ai_service):
        """Test integration between portfolio and performance services"""
        portfolio_service = PortfolioService(test_db_session)
        performance_service = PerformanceService(test_db_session)
        
        user_id = sample_portfolio_data["user"]["sub"]
        
        # Update prices through portfolio service
        mock_market_data_service.get_current_prices.return_value = {
            "AAPL": 160.0,
            "MSFT": 320.0,
            "BTC-USD": 45000.0
        }
        
        await portfolio_service.update_prices(clerk_user_id=user_id)
        
        # Get performance analysis
        performance_data = await performance_service.get_all_portfolio_performance(clerk_user_id=user_id)
        
        assert isinstance(performance_data, list)
        if performance_data:  # If we have data
            portfolio_perf = performance_data[0]
            assert "total_return" in portfolio_perf
            assert "sharpe_ratio" in portfolio_perf

    @pytest.mark.asyncio
    async def test_market_data_service_integration(self, test_db_session, sample_portfolio_data, mock_ai_service):
        """Test real market data service integration"""
        from app.services.market_data import MarketDataService
        
        portfolio_service = PortfolioService(test_db_session)
        market_service = MarketDataService()
        
        # Test with mock market service
        with patch.object(market_service, 'get_current_prices') as mock_prices:
            mock_prices.return_value = {"AAPL": 155.0, "MSFT": 310.0}
            
            # Integration should work
            user_id = sample_portfolio_data["user"]["sub"]
            result = await portfolio_service.update_prices(clerk_user_id=user_id)
            
            assert "updated_assets" in result
            mock_prices.assert_called_once()

    @pytest.mark.asyncio
    async def test_ai_service_integration(self, test_db_session, sample_portfolio_data, mock_market_data_service):
        """Test AI service integration"""
        portfolio_service = PortfolioService(test_db_session)
        user_id = sample_portfolio_data["user"]["sub"]
        
        # Mock AI service responses
        with patch.object(portfolio_service.ai_service, 'analyze_portfolio_fast') as mock_ai:
            mock_ai.return_value = {
                "recommendation": "BUY",
                "confidence": 0.9,
                "analysis_type": "enhanced"
            }
            
            summary = await portfolio_service.get_portfolio_summary(clerk_user_id=user_id)
            
            assert summary["analysis"]["recommendation"] == "BUY"
            assert summary["analysis"]["confidence"] == 0.9
            mock_ai.assert_called_once()


class TestErrorHandlingIntegration:
    """Test error handling across integrated systems"""

    @patch('app.api.routes.get_current_user')
    def test_cascading_error_handling(self, mock_auth, test_client, mock_market_data_service, mock_ai_service):
        """Test how errors cascade through the system"""
        user_id = "error_test_user"
        mock_auth.return_value = {"sub": user_id, "email": "test@example.com"}
        
        # Create account successfully
        account_response = test_client.post("/api/v1/accounts/", json={
            "name": "Error Test Account",
            "account_type": "brokerage"
        })
        assert account_response.status_code == 200
        account_id = account_response.json()["id"]
        
        # Add asset successfully
        test_client.post("/api/v1/assets/", json={
            "account_id": account_id,
            "symbol": "TEST",
            "shares": 100,
            "avg_cost": 100.0
        })
        
        # Mock market data service failure
        mock_market_data_service.get_current_prices.return_value = {}
        
        # Price update should handle failure gracefully
        price_response = test_client.post("/api/v1/portfolio/update-prices")
        assert price_response.status_code == 200
        
        price_data = price_response.json()
        assert price_data["updated_assets"] == 0  # None updated due to failure
        assert len(price_data["failed_symbols"]) > 0
        
        # Portfolio summary should still work with AI fallback
        mock_ai_service.analyze_portfolio_fast.side_effect = Exception("AI service down")
        
        summary_response = test_client.get("/api/v1/portfolio/summary")
        assert summary_response.status_code == 200
        
        summary = summary_response.json()
        assert "analysis" in summary
        assert summary["analysis"]["analysis_type"] == "basic"  # Fallback

    @patch('app.api.routes.get_current_user')
    def test_database_error_handling(self, mock_auth, test_client):
        """Test database error handling"""
        mock_auth.return_value = {"sub": "db_error_user", "email": "test@example.com"}
        
        # Test with database connection issues
        with patch('app.core.database.SessionLocal') as mock_session:
            mock_session.side_effect = Exception("Database connection failed")
            
            # Should return 500 error, not crash
            response = test_client.get("/api/v1/portfolio/summary")
            assert response.status_code == 500

    @patch('app.api.routes.get_current_user')
    def test_authentication_error_handling(self, mock_auth, test_client):
        """Test authentication error handling"""
        # Test with auth failure
        mock_auth.side_effect = Exception("Auth service down")
        
        response = test_client.get("/api/v1/portfolio/summary")
        assert response.status_code == 401


class TestDataConsistencyIntegration:
    """Test data consistency across integrated operations"""

    @patch('app.api.routes.get_current_user')
    def test_portfolio_value_consistency(self, mock_auth, test_client, mock_market_data_service, mock_ai_service):
        """Test portfolio value consistency across operations"""
        user_id = "consistency_test_user"
        mock_auth.return_value = {"sub": user_id, "email": "test@example.com"}
        
        # Create account and assets
        account_response = test_client.post("/api/v1/accounts/", json={
            "name": "Consistency Test",
            "account_type": "brokerage"
        })
        account_id = account_response.json()["id"]
        
        test_assets = [
            {"symbol": "AAPL", "shares": 100, "avg_cost": 150.0},
            {"symbol": "MSFT", "shares": 50, "avg_cost": 300.0}
        ]
        
        for asset_data in test_assets:
            asset_data["account_id"] = account_id
            test_client.post("/api/v1/assets/", json=asset_data)
        
        # Set consistent prices
        mock_market_data_service.get_current_prices.return_value = {
            "AAPL": 160.0,  # 100 * 160 = 16,000
            "MSFT": 320.0   # 50 * 320 = 16,000
        }
        
        # Update prices
        test_client.post("/api/v1/portfolio/update-prices")
        
        # Get summary and verify consistency
        summary_response = test_client.get("/api/v1/portfolio/summary")
        summary = summary_response.json()
        
        account_data = summary["accounts"][0]
        expected_value = (100 * 160.0) + (50 * 320.0)  # 32,000
        
        assert abs(account_data["balance"] - expected_value) < 0.01
        assert abs(summary["summary"]["total_value"] - expected_value) < 0.01

    @pytest.mark.asyncio
    async def test_concurrent_operations_consistency(self, test_db_session, sample_portfolio_data, mock_market_data_service, mock_ai_service):
        """Test data consistency with concurrent operations"""
        portfolio_service = PortfolioService(test_db_session)
        user_id = sample_portfolio_data["user"]["sub"]
        
        # Mock consistent market data
        mock_market_data_service.get_current_prices.return_value = {
            "AAPL": 160.0,
            "MSFT": 320.0,
            "BTC-USD": 45000.0
        }
        
        # Run concurrent operations
        tasks = [
            portfolio_service.update_prices(clerk_user_id=user_id),
            portfolio_service.get_portfolio_summary(clerk_user_id=user_id),
            portfolio_service.update_prices(clerk_user_id=user_id)  # Duplicate to test race conditions
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All operations should succeed
        for i, result in enumerate(results):
            assert not isinstance(result, Exception), f"Task {i} failed: {result}"
        
        # Final consistency check
        final_summary = await portfolio_service.get_portfolio_summary(clerk_user_id=user_id)
        assert final_summary["summary"]["total_value"] > 0


class TestPerformanceIntegration:
    """Test system performance with integrated operations"""

    @skip_if_production("Performance test with load")
    @patch('app.api.routes.get_current_user')
    def test_high_load_performance(self, mock_auth, test_client, mock_market_data_service, mock_ai_service):
        """Test system performance under load"""
        user_id = "performance_test_user"
        mock_auth.return_value = {"sub": user_id, "email": "test@example.com"}
        
        # Create account
        account_response = test_client.post("/api/v1/accounts/", json={
            "name": "Performance Test Account",
            "account_type": "brokerage"
        })
        account_id = account_response.json()["id"]
        
        # Add many assets
        symbols = [f"STOCK{i}" for i in range(50)]
        for i, symbol in enumerate(symbols):
            test_client.post("/api/v1/assets/", json={
                "account_id": account_id,
                "symbol": symbol,
                "shares": 10,
                "avg_cost": 100.0 + i
            })
        
        # Mock market data for all symbols
        mock_prices = {symbol: 110.0 + (i % 10) for i, symbol in enumerate(symbols)}
        mock_market_data_service.get_current_prices.return_value = mock_prices
        
        # Time the operations
        start_time = time.time()
        
        # Update prices
        price_response = test_client.post("/api/v1/portfolio/update-prices")
        assert price_response.status_code == 200
        
        # Get summary
        summary_response = test_client.get("/api/v1/portfolio/summary")
        assert summary_response.status_code == 200
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete within reasonable time
        assert total_time < 10.0, f"Operations too slow: {total_time:.2f}s"
        
        summary = summary_response.json()
        assert len(summary["accounts"][0]["assets"]) == 50

    @pytest.mark.asyncio
    async def test_service_performance_benchmarks(self, test_db_session, sample_portfolio_data, mock_market_data_service, mock_ai_service):
        """Test individual service performance benchmarks"""
        portfolio_service = PortfolioService(test_db_session)
        user_id = sample_portfolio_data["user"]["sub"]
        
        # Benchmark portfolio summary
        start_time = time.time()
        summary = await portfolio_service.get_portfolio_summary(clerk_user_id=user_id)
        summary_time = time.time() - start_time
        
        assert summary_time < 2.0, f"Portfolio summary too slow: {summary_time:.2f}s"
        
        # Benchmark price updates
        mock_market_data_service.get_current_prices.return_value = {
            "AAPL": 160.0, "MSFT": 320.0, "BTC-USD": 45000.0
        }
        
        start_time = time.time()
        update_result = await portfolio_service.update_prices(clerk_user_id=user_id)
        update_time = time.time() - start_time
        
        assert update_time < 5.0, f"Price update too slow: {update_time:.2f}s"


@pytest.mark.slow
class TestLongRunningIntegration:
    """Test long-running integration scenarios"""

    @skip_if_production("Long running test")
    @pytest.mark.asyncio
    async def test_extended_operation_stability(self, test_db_session, sample_portfolio_data, mock_market_data_service, mock_ai_service):
        """Test system stability over extended operations"""
        portfolio_service = PortfolioService(test_db_session)
        user_id = sample_portfolio_data["user"]["sub"]
        
        # Run multiple iterations of operations
        for iteration in range(10):
            # Vary prices to simulate market changes
            mock_market_data_service.get_current_prices.return_value = {
                "AAPL": 150.0 + (iteration * 5),
                "MSFT": 300.0 + (iteration * 10),
                "BTC-USD": 40000.0 + (iteration * 1000)
            }
            
            # Update prices
            await portfolio_service.update_prices(clerk_user_id=user_id)
            
            # Get summary
            summary = await portfolio_service.get_portfolio_summary(clerk_user_id=user_id)
            
            # Verify consistency
            assert summary["summary"]["total_value"] > 0
            assert len(summary["accounts"]) > 0
            
            # Brief pause to simulate realistic usage
            await asyncio.sleep(0.1)
        
        # Final consistency check
        final_summary = await portfolio_service.get_portfolio_summary(clerk_user_id=user_id)
        assert final_summary["status"] == "success"

    @skip_if_production("Memory intensive test")
    def test_memory_leak_detection(self, test_client):
        """Test for memory leaks over many operations"""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss
            
            # Perform many operations
            for i in range(100):
                response = test_client.get("/")
                assert response.status_code == 200
                
                # Check every 20 iterations
                if i % 20 == 0:
                    current_memory = process.memory_info().rss
                    memory_growth = current_memory - initial_memory
                    
                    # Memory growth should be reasonable
                    assert memory_growth < 100 * 1024 * 1024, f"Excessive memory growth: {memory_growth/1024/1024:.1f}MB"
            
            final_memory = process.memory_info().rss
            total_growth = final_memory - initial_memory
            
            # Total memory growth should be minimal
            assert total_growth < 50 * 1024 * 1024, f"Memory leak detected: {total_growth/1024/1024:.1f}MB growth"
            
        except ImportError:
            pytest.skip("psutil not available for memory testing")
