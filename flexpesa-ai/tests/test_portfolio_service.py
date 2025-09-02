"""
Portfolio service tests
Tests the core portfolio management service functionality
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.services.portfolio_service import PortfolioService
from app.schemas.portfolio import AccountCreate, AssetCreate
from app.models.portfolio import Account, Asset, MarketData, PortfolioSnapshot
from conftest import skip_if_production


class TestPortfolioServiceBasic:
    """Test basic portfolio service operations"""

    def test_portfolio_service_initialization(self, test_db_session, mock_market_data_service, mock_ai_service):
        """Test portfolio service initialization"""
        service = PortfolioService(test_db_session)
        
        assert service.db == test_db_session
        assert service.market_data is not None
        assert service.ai_service is not None

    def test_create_account(self, test_db_session, mock_market_data_service, mock_ai_service):
        """Test creating an account through the service"""
        service = PortfolioService(test_db_session)
        user_id = "test_user_123"
        
        account_data = AccountCreate(
            name="Test Investment Account",
            account_type="brokerage"
        )
        
        result = service.create_account(account_data, user_id)
        
        assert result.name == "Test Investment Account"
        assert result.account_type == "brokerage"
        assert result.clerk_user_id == user_id
        assert result.id is not None

    def test_create_account_with_description(self, test_db_session, mock_market_data_service, mock_ai_service):
        """Test creating account with description"""
        service = PortfolioService(test_db_session)
        user_id = "test_user_123"
        
        # Create account data with description
        account_data = AccountCreate(
            name="Retirement Account",
            account_type="retirement"
        )
        account_data.description = "401k rollover account"
        
        result = service.create_account(account_data, user_id)
        
        assert result.description == "401k rollover account"

    def test_create_duplicate_account_allowed(self, test_db_session, mock_market_data_service, mock_ai_service):
        """Test that duplicate account names are allowed"""
        service = PortfolioService(test_db_session)
        user_id = "test_user_123"
        
        account_data = AccountCreate(
            name="Duplicate Account",
            account_type="brokerage"
        )
        
        # Create first account
        result1 = service.create_account(account_data, user_id)
        
        # Create second account with same name
        result2 = service.create_account(account_data, user_id)
        
        assert result1.id != result2.id
        assert result1.name == result2.name

    @pytest.mark.asyncio
    async def test_add_asset_new(self, test_db_session, mock_market_data_service, mock_ai_service):
        """Test adding a new asset to account"""
        service = PortfolioService(test_db_session)
        user_id = "test_user_123"
        
        # Create account first
        account_data = AccountCreate(name="Test Account", account_type="brokerage")
        account = service.create_account(account_data, user_id)
        
        # Add asset
        asset_data = AssetCreate(
            account_id=account.id,
            symbol="AAPL",
            shares=100,
            avg_cost=150.0
        )
        
        result = await service.add_asset(asset_data)
        
        assert result.symbol == "AAPL"
        assert result.shares == 100
        assert result.avg_cost == 150.0
        assert result.account_id == account.id

    @pytest.mark.asyncio
    async def test_add_asset_existing(self, test_db_session, mock_market_data_service, mock_ai_service):
        """Test adding to existing asset position"""
        service = PortfolioService(test_db_session)
        user_id = "test_user_123"
        
        # Create account
        account_data = AccountCreate(name="Test Account", account_type="brokerage")
        account = service.create_account(account_data, user_id)
        
        # Add initial position
        asset_data1 = AssetCreate(
            account_id=account.id,
            symbol="AAPL",
            shares=100,
            avg_cost=150.0
        )
        await service.add_asset(asset_data1)
        
        # Add to existing position
        asset_data2 = AssetCreate(
            account_id=account.id,
            symbol="AAPL",  # Same symbol
            shares=50,
            avg_cost=160.0
        )
        result = await service.add_asset(asset_data2)
        
        # Should have combined position with average cost
        # (100 * 150 + 50 * 160) / 150 = 153.33
        expected_avg_cost = (100 * 150.0 + 50 * 160.0) / 150
        
        assert result.shares == 150
        assert abs(result.avg_cost - expected_avg_cost) < 0.01

    @pytest.mark.asyncio
    async def test_add_asset_inactive_account(self, test_db_session, mock_market_data_service, mock_ai_service):
        """Test adding asset to inactive account fails"""
        service = PortfolioService(test_db_session)
        user_id = "test_user_123"
        
        # Create account and make it inactive
        account_data = AccountCreate(name="Test Account", account_type="brokerage")
        account = service.create_account(account_data, user_id)
        account.is_active = False
        test_db_session.commit()
        
        # Try to add asset
        asset_data = AssetCreate(
            account_id=account.id,
            symbol="AAPL",
            shares=100,
            avg_cost=150.0
        )
        
        with pytest.raises(ValueError, match="Account not found or inactive"):
            await service.add_asset(asset_data)

    @pytest.mark.asyncio
    async def test_add_asset_nonexistent_account(self, test_db_session, mock_market_data_service, mock_ai_service):
        """Test adding asset to nonexistent account fails"""
        service = PortfolioService(test_db_session)
        
        asset_data = AssetCreate(
            account_id=99999,  # Non-existent
            symbol="AAPL",
            shares=100,
            avg_cost=150.0
        )
        
        with pytest.raises(ValueError, match="Account not found or inactive"):
            await service.add_asset(asset_data)


class TestPortfolioServicePriceUpdates:
    """Test price update functionality"""

    @pytest.mark.asyncio
    async def test_update_prices_user_assets(self, test_db_session, sample_portfolio_data, mock_market_data_service, mock_ai_service):
        """Test updating prices for user's assets"""
        service = PortfolioService(test_db_session)
        user_id = sample_portfolio_data["user"]["sub"]
        
        # Mock market data service
        mock_market_data_service.get_current_prices.return_value = {
            "AAPL": 160.0,
            "MSFT": 320.0,
            "BTC-USD": 45000.0
        }
        
        result = await service.update_prices(clerk_user_id=user_id)
        
        assert "updated_assets" in result
        assert "total_assets" in result
        assert result["updated_assets"] > 0
        
        # Verify prices were updated
        asset = test_db_session.query(Asset).filter(Asset.symbol == "AAPL").first()
        assert asset.current_price == 160.0

    @pytest.mark.asyncio
    async def test_update_prices_no_assets(self, test_db_session, mock_market_data_service, mock_ai_service):
        """Test updating prices with no assets"""
        service = PortfolioService(test_db_session)
        user_id = "nonexistent_user"
        
        result = await service.update_prices(clerk_user_id=user_id)
        
        assert result["updated_assets"] == 0
        assert result["total_assets"] == 0

    @pytest.mark.asyncio
    async def test_update_prices_market_data_failure(self, test_db_session, sample_portfolio_data, mock_market_data_service, mock_ai_service):
        """Test price update when market data fails"""
        service = PortfolioService(test_db_session)
        user_id = sample_portfolio_data["user"]["sub"]
        
        # Mock market data service to return empty results
        mock_market_data_service.get_current_prices.return_value = {}
        
        result = await service.update_prices(clerk_user_id=user_id)
        
        assert result["updated_assets"] == 0
        assert len(result["failed_symbols"]) > 0

    @pytest.mark.asyncio
    async def test_update_prices_partial_failure(self, test_db_session, sample_portfolio_data, mock_market_data_service, mock_ai_service):
        """Test price update with partial failures"""
        service = PortfolioService(test_db_session)
        user_id = sample_portfolio_data["user"]["sub"]
        
        # Mock partial success
        mock_market_data_service.get_current_prices.return_value = {
            "AAPL": 160.0,
            "MSFT": 0.0,  # Failed to get price
            "BTC-USD": 45000.0
        }
        
        result = await service.update_prices(clerk_user_id=user_id)
        
        assert result["updated_assets"] == 2  # AAPL and BTC-USD
        assert "MSFT" in result["failed_symbols"]

    @pytest.mark.asyncio
    async def test_update_account_balances(self, test_db_session, sample_portfolio_data, mock_market_data_service, mock_ai_service):
        """Test that account balances are updated after price updates"""
        service = PortfolioService(test_db_session)
        user_id = sample_portfolio_data["user"]["sub"]
        account = sample_portfolio_data["account"]
        
        original_balance = account.balance
        
        # Mock updated prices
        mock_market_data_service.get_current_prices.return_value = {
            "AAPL": 200.0,  # Significant increase
            "MSFT": 400.0,
            "BTC-USD": 50000.0
        }
        
        await service.update_prices(clerk_user_id=user_id)
        
        # Refresh account
        test_db_session.refresh(account)
        
        # Balance should be updated
        assert account.balance != original_balance
        assert account.balance > original_balance  # Prices increased


class TestPortfolioServiceSummary:
    """Test portfolio summary functionality"""

    @pytest.mark.asyncio
    async def test_get_portfolio_summary(self, test_db_session, sample_portfolio_data, mock_market_data_service, mock_ai_service):
        """Test getting complete portfolio summary"""
        service = PortfolioService(test_db_session)
        user_id = sample_portfolio_data["user"]["sub"]
        
        result = await service.get_portfolio_summary(clerk_user_id=user_id)
        
        assert "user_id" in result
        assert "accounts" in result
        assert "summary" in result
        assert "analysis" in result
        assert result["user_id"] == user_id
        assert len(result["accounts"]) == 1

    @pytest.mark.asyncio
    async def test_portfolio_summary_calculations(self, test_db_session, sample_portfolio_data, mock_market_data_service, mock_ai_service):
        """Test portfolio summary calculations are correct"""
        service = PortfolioService(test_db_session)
        user_id = sample_portfolio_data["user"]["sub"]
        
        result = await service.get_portfolio_summary(clerk_user_id=user_id)
        
        summary = result["summary"]
        account = result["accounts"][0]
        
        # Verify calculations
        assert summary["total_value"] == account["balance"]
        assert summary["total_accounts"] == 1
        assert summary["total_assets"] == len(account["assets"])

    @pytest.mark.asyncio
    async def test_portfolio_summary_empty_portfolio(self, test_db_session, mock_market_data_service, mock_ai_service):
        """Test portfolio summary with empty portfolio"""
        service = PortfolioService(test_db_session)
        user_id = "empty_user"
        
        result = await service.get_portfolio_summary(clerk_user_id=user_id)
        
        assert result["accounts"] == []
        assert result["summary"]["total_value"] == 0
        assert result["summary"]["total_accounts"] == 0

    @pytest.mark.asyncio
    async def test_portfolio_summary_ai_analysis_integration(self, test_db_session, sample_portfolio_data, mock_market_data_service, mock_ai_service):
        """Test AI analysis integration in portfolio summary"""
        service = PortfolioService(test_db_session)
        user_id = sample_portfolio_data["user"]["sub"]
        
        # Mock AI service response
        mock_ai_service.analyze_portfolio_fast.return_value = {
            "recommendation": "HOLD",
            "confidence": 0.8,
            "risk_score": 3.5
        }
        
        result = await service.get_portfolio_summary(clerk_user_id=user_id)
        
        assert "analysis" in result
        assert result["analysis"]["recommendation"] == "HOLD"
        assert result["analysis"]["confidence"] == 0.8

    @pytest.mark.asyncio
    async def test_portfolio_summary_ai_failure_fallback(self, test_db_session, sample_portfolio_data, mock_market_data_service):
        """Test fallback when AI analysis fails"""
        service = PortfolioService(test_db_session)
        user_id = sample_portfolio_data["user"]["sub"]
        
        # Mock AI service to raise exception
        with patch.object(service, 'ai_service') as mock_ai:
            mock_ai.analyze_portfolio_fast.side_effect = Exception("AI service down")
            
            result = await service.get_portfolio_summary(clerk_user_id=user_id)
        
        assert "analysis" in result
        assert result["analysis"]["analysis_type"] == "basic"


class TestPortfolioServiceMarketData:
    """Test market data integration"""

    @pytest.mark.asyncio
    async def test_get_or_fetch_market_data_cached(self, test_db_session, mock_market_data_service, mock_ai_service):
        """Test getting cached market data"""
        service = PortfolioService(test_db_session)
        
        # Create cached market data
        cached_data = MarketData(
            symbol="AAPL",
            name="Apple Inc.",
            current_price=155.0,
            sector="Technology"
        )
        test_db_session.add(cached_data)
        test_db_session.commit()
        
        result = await service._get_or_fetch_market_data("AAPL")
        
        assert result is not None
        assert result.symbol == "AAPL"
        assert result.current_price == 155.0

    @pytest.mark.asyncio
    async def test_get_or_fetch_market_data_fresh(self, test_db_session, mock_market_data_service, mock_ai_service):
        """Test fetching fresh market data"""
        service = PortfolioService(test_db_session)
        
        # Mock market data service
        mock_market_data_service.get_current_prices.return_value = {"MSFT": 320.0}
        
        result = await service._get_or_fetch_market_data("MSFT")
        
        # Should create new market data entry
        assert result is not None
        assert result.symbol == "MSFT"
        assert result.current_price == 320.0

    @pytest.mark.asyncio
    async def test_get_or_fetch_market_data_stale(self, test_db_session, mock_market_data_service, mock_ai_service):
        """Test updating stale market data"""
        service = PortfolioService(test_db_session)
        
        # Create stale market data
        old_time = datetime.utcnow() - timedelta(minutes=10)
        stale_data = MarketData(
            symbol="GOOGL",
            current_price=100.0,
            updated_at=old_time
        )
        test_db_session.add(stale_data)
        test_db_session.commit()
        
        # Mock fresh data
        mock_market_data_service.get_current_prices.return_value = {"GOOGL": 110.0}
        
        result = await service._get_or_fetch_market_data("GOOGL")
        
        assert result.current_price == 110.0  # Updated price

    @pytest.mark.asyncio
    async def test_get_or_fetch_market_data_failure(self, test_db_session, mock_market_data_service, mock_ai_service):
        """Test market data fetch failure"""
        service = PortfolioService(test_db_session)
        
        # Mock failure
        mock_market_data_service.get_current_prices.return_value = {}
        
        result = await service._get_or_fetch_market_data("FAIL")
        
        assert result is None

    def test_determine_asset_type(self, test_db_session, mock_market_data_service, mock_ai_service):
        """Test asset type determination"""
        service = PortfolioService(test_db_session)
        
        assert service._determine_asset_type("BTC-USD") == "crypto"
        assert service._determine_asset_type("ETH-USD") == "crypto"
        assert service._determine_asset_type("SPY") == "etf"
        assert service._determine_asset_type("QQQ") == "etf"
        assert service._determine_asset_type("AAPL") == "stock"
        assert service._determine_asset_type("MSFT") == "stock"
        assert service._determine_asset_type("UNKNOWN123") == "other"


class TestPortfolioServiceSnapshots:
    """Test portfolio snapshot functionality"""

    @pytest.mark.asyncio
    async def test_create_portfolio_snapshot(self, test_db_session, sample_portfolio_data, mock_market_data_service, mock_ai_service):
        """Test creating portfolio snapshot"""
        service = PortfolioService(test_db_session)
        user_id = sample_portfolio_data["user"]["sub"]
        
        snapshot_data = {
            "total_value": 10000.0,
            "total_cost_basis": 9000.0,
            "total_pnl": 1000.0,
            "total_pnl_percent": 11.11,
            "asset_count": 3,
            "account_count": 1
        }
        
        await service._create_portfolio_snapshot(user_id, snapshot_data)
        
        # Verify snapshot was created
        snapshot = test_db_session.query(PortfolioSnapshot).filter(
            PortfolioSnapshot.clerk_user_id == user_id
        ).first()
        
        assert snapshot is not None
        assert snapshot.total_value == 10000.0
        assert snapshot.total_pnl == 1000.0

    @pytest.mark.asyncio
    async def test_create_portfolio_snapshot_duplicate_date(self, test_db_session, sample_portfolio_data, mock_market_data_service, mock_ai_service):
        """Test creating snapshot when one already exists for today"""
        service = PortfolioService(test_db_session)
        user_id = sample_portfolio_data["user"]["sub"]
        
        # Create first snapshot
        snapshot1 = PortfolioSnapshot(
            clerk_user_id=user_id,
            total_value=10000.0,
            total_cost_basis=9000.0,
            total_pnl=1000.0,
            total_pnl_percent=11.11,
            asset_count=3,
            account_count=1,
            snapshot_type="daily"
        )
        test_db_session.add(snapshot1)
        test_db_session.commit()
        
        # Try to create another for same day
        snapshot_data = {
            "total_value": 11000.0,
            "total_cost_basis": 9000.0,
            "total_pnl": 2000.0,
            "total_pnl_percent": 22.22,
            "asset_count": 3,
            "account_count": 1
        }
        
        await service._create_portfolio_snapshot(user_id, snapshot_data)
        
        # Should update existing snapshot
        updated_snapshot = test_db_session.query(PortfolioSnapshot).filter(
            PortfolioSnapshot.clerk_user_id == user_id
        ).first()
        
        assert updated_snapshot.total_value == 11000.0

    @pytest.mark.asyncio
    async def test_create_portfolio_snapshot_auto_calculation(self, test_db_session, sample_portfolio_data, mock_market_data_service, mock_ai_service):
        """Test creating snapshot with automatic calculation"""
        service = PortfolioService(test_db_session)
        user_id = sample_portfolio_data["user"]["sub"]
        
        # Call without data to trigger auto-calculation
        await service._create_portfolio_snapshot(user_id)
        
        # Verify snapshot was created
        snapshot = test_db_session.query(PortfolioSnapshot).filter(
            PortfolioSnapshot.clerk_user_id == user_id
        ).first()
        
        assert snapshot is not None
        assert snapshot.total_value > 0

    @pytest.mark.asyncio
    async def test_create_portfolio_snapshot_failure_handling(self, test_db_session, mock_market_data_service, mock_ai_service):
        """Test snapshot creation failure handling"""
        service = PortfolioService(test_db_session)
        user_id = "test_user"
        
        # Mock database error
        with patch.object(service.db, 'add', side_effect=Exception("DB Error")):
            # Should not raise exception, just log warning
            await service._create_portfolio_snapshot(user_id, {})


class TestPortfolioServiceAI:
    """Test AI analysis integration"""

    @pytest.mark.asyncio
    async def test_get_enhanced_asset_analysis(self, test_db_session, mock_market_data_service, mock_ai_service):
        """Test enhanced asset analysis"""
        service = PortfolioService(test_db_session)
        
        mock_ai_service.analyze_asset_fast.return_value = {
            "symbol": "AAPL",
            "recommendation": "BUY",
            "confidence": 0.85,
            "technical": {"rsi": 45},
            "sentiment": {"score": 0.3}
        }
        
        result = await service.get_enhanced_asset_analysis("AAPL")
        
        assert result["symbol"] == "AAPL"
        assert result["recommendation"] == "BUY"
        assert result["confidence"] == 0.85

    @pytest.mark.asyncio
    async def test_get_enhanced_asset_analysis_failure(self, test_db_session, mock_market_data_service, mock_ai_service):
        """Test asset analysis failure handling"""
        service = PortfolioService(test_db_session)
        
        # Mock AI service failure
        mock_ai_service.analyze_asset_fast.side_effect = Exception("AI Error")
        
        result = await service.get_enhanced_asset_analysis("FAIL")
        
        assert "error" in result
        assert result["symbol"] == "FAIL"

    def test_get_fallback_analysis(self, test_db_session, sample_portfolio_data, mock_market_data_service, mock_ai_service):
        """Test fallback analysis when AI fails"""
        service = PortfolioService(test_db_session)
        
        portfolio_data = [
            {
                "assets": [{"symbol": "AAPL"}, {"symbol": "MSFT"}]
            }
        ]
        
        result = service._get_fallback_analysis(portfolio_data, 10000.0, 9000.0)
        
        assert "analysis_type" in result
        assert result["analysis_type"] == "basic"
        assert "recommendation" in result
        assert "insights" in result


class TestPortfolioServiceErrorHandling:
    """Test error handling in portfolio service"""

    def test_create_account_database_error(self, test_db_session, mock_market_data_service, mock_ai_service):
        """Test account creation database error handling"""
        service = PortfolioService(test_db_session)
        
        account_data = AccountCreate(name="Test", account_type="brokerage")
        
        # Mock database error
        with patch.object(service.db, 'commit', side_effect=Exception("DB Error")):
            with pytest.raises(Exception):
                service.create_account(account_data, "user_123")

    @pytest.mark.asyncio
    async def test_add_asset_database_error(self, test_db_session, sample_portfolio_data, mock_market_data_service, mock_ai_service):
        """Test asset addition database error handling"""
        service = PortfolioService(test_db_session)
        account = sample_portfolio_data["account"]
        
        asset_data = AssetCreate(
            account_id=account.id,
            symbol="ERROR",
            shares=100,
            avg_cost=150.0
        )
        
        # Mock database error
        with patch.object(service.db, 'commit', side_effect=Exception("DB Error")):
            with pytest.raises(Exception):
                await service.add_asset(asset_data)

    @pytest.mark.asyncio
    async def test_update_prices_exception_handling(self, test_db_session, sample_portfolio_data, mock_market_data_service, mock_ai_service):
        """Test price update exception handling"""
        service = PortfolioService(test_db_session)
        user_id = sample_portfolio_data["user"]["sub"]
        
        # Mock market data service to raise exception
        mock_market_data_service.get_current_prices.side_effect = Exception("Market data error")
        
        with pytest.raises(Exception):
            await service.update_prices(clerk_user_id=user_id)

    @pytest.mark.asyncio
    async def test_portfolio_summary_exception_handling(self, test_db_session, mock_market_data_service, mock_ai_service):
        """Test portfolio summary exception handling"""
        service = PortfolioService(test_db_session)
        
        # Mock database error
        with patch.object(service.db, 'query', side_effect=Exception("DB Error")):
            with pytest.raises(Exception):
                await service.get_portfolio_summary("user_123")


@pytest.mark.slow
class TestPortfolioServicePerformance:
    """Test portfolio service performance"""

    @skip_if_production("Creates large test dataset")
    @pytest.mark.asyncio
    async def test_large_portfolio_performance(self, test_db_session, mock_market_data_service, mock_ai_service):
        """Test service performance with large portfolios"""
        service = PortfolioService(test_db_session)
        user_id = "large_user"
        
        # Create large portfolio
        account_data = AccountCreate(name="Large Account", account_type="brokerage")
        account = service.create_account(account_data, user_id)
        
        # Add many assets
        for i in range(100):
            asset_data = AssetCreate(
                account_id=account.id,
                symbol=f"STOCK{i}",
                shares=100,
                avg_cost=100.0
            )
            await service.add_asset(asset_data)
        
        # Test performance
        import time
        start_time = time.time()
        
        result = await service.get_portfolio_summary(clerk_user_id=user_id)
        
        execution_time = time.time() - start_time
        
        # Should complete within reasonable time
        assert execution_time < 5.0
        assert len(result["accounts"][0]["assets"]) == 100

    @pytest.mark.asyncio
    async def test_concurrent_price_updates(self, test_db_session, sample_portfolio_data, mock_market_data_service, mock_ai_service):
        """Test concurrent price update handling"""
        service = PortfolioService(test_db_session)
        user_id = sample_portfolio_data["user"]["sub"]
        
        # Mock market data to simulate delay
        mock_market_data_service.get_current_prices.return_value = {
            "AAPL": 160.0,
            "MSFT": 320.0,
            "BTC-USD": 45000.0
        }
        
        import asyncio
        
        # Start multiple price updates concurrently
        tasks = [
            service.update_prices(clerk_user_id=user_id)
            for _ in range(3)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should complete without errors
        for result in results:
            assert not isinstance(result, Exception)
            assert "updated_assets" in result
