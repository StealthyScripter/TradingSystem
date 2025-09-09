"""
Service tests - simplified and reliable
Test core service functionality with proper async handling
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from sqlalchemy.exc import IntegrityError, DataError, OperationalError
from app.services.portfolio_service import PortfolioService
from app.schemas.portfolio import AccountCreate, AssetCreate

class TestPortfolioServiceBasic:
    """Test basic portfolio service operations"""

    def test_service_initialization(self, test_db):
        """Test service can be initialized"""
        service = PortfolioService(test_db)
        assert service.db == test_db

    def test_create_account_service(self, test_db):
        """Test creating account through service"""
        service = PortfolioService(test_db)
        user_id = "test_user_123"

        account_data = AccountCreate(
            name="Service Test Account",
            account_type="brokerage"
        )

        result = service.create_account(account_data, user_id)

        assert result.name == "Service Test Account"
        assert result.account_type == "brokerage"
        assert result.clerk_user_id == user_id
        assert result.id is not None

    @pytest.mark.asyncio
    async def test_add_asset_service(self, test_db, sample_account):
        """Test adding asset through service"""
        service = PortfolioService(test_db)

        asset_data = AssetCreate(
            account_id=sample_account.id,
            symbol="GOOGL",
            shares=5,
            avg_cost=120.0
        )

        result = await service.add_asset(asset_data)

        assert result.symbol == "GOOGL"
        assert result.shares == 5
        assert result.avg_cost == 120.0
        assert result.account_id == sample_account.id

    @pytest.mark.asyncio
    async def test_add_asset_to_existing_position(self, test_db, sample_account):
        """Test adding to existing asset position"""
        service = PortfolioService(test_db)

        # Add initial position
        asset_data1 = AssetCreate(
            account_id=sample_account.id,
            symbol="AAPL",
            shares=10,
            avg_cost=150.0
        )
        await service.add_asset(asset_data1)

        # Add to existing position
        asset_data2 = AssetCreate(
            account_id=sample_account.id,
            symbol="AAPL",  # Same symbol
            shares=5,
            avg_cost=160.0
        )
        result = await service.add_asset(asset_data2)

        # Should combine positions with weighted average cost
        assert result.shares == 15  # 10 + 5

        # Weighted average: (10*150 + 5*160) / 15 = 153.33
        expected_avg = (10 * 150.0 + 5 * 160.0) / 15
        assert abs(result.avg_cost - expected_avg) < 0.01

    @pytest.mark.asyncio
    async def test_add_asset_invalid_account(self, test_db):
        """Test adding asset to invalid account"""
        service = PortfolioService(test_db)

        asset_data = AssetCreate(
            account_id=99999,  # Non-existent
            symbol="FAIL",
            shares=10,
            avg_cost=100.0
        )

        with pytest.raises(ValueError, match="Account not found"):
            await service.add_asset(asset_data)

    def test_determine_asset_type(self, test_db):
        """Test asset type determination"""
        service = PortfolioService(test_db)

        assert service._determine_asset_type("AAPL") == "stock"
        assert service._determine_asset_type("BTC-USD") == "crypto"
        assert service._determine_asset_type("ETH-USD") == "crypto"
        assert service._determine_asset_type("SPY") == "etf"
        assert service._determine_asset_type("QQQ") == "etf"

class TestPortfolioServiceWithMocks:
    """Test service with properly mocked dependencies"""

    @pytest.mark.asyncio
    async def test_portfolio_summary_with_mock_ai(self, test_db, sample_account, sample_asset):
        """Test portfolio summary with mocked AI service"""
        service = PortfolioService(test_db)
        user_id = sample_account.clerk_user_id

        # Mock AI service response
        mock_ai_response = {
            "total_value": 1550.0,
            "recommendation": "HOLD",
            "confidence": 0.8,
            "risk_score": 3.5,
            "insights": [
                "Portfolio is moderately diversified",
                "Technology sector exposure detected"
            ],
            "analysis_type": "enhanced"
        }

        # Mock the AI service
        with patch.object(service, 'ai_service') as mock_ai:
            mock_ai.analyze_portfolio_fast = AsyncMock(return_value=mock_ai_response)

            result = await service.get_portfolio_summary(clerk_user_id=user_id)

        assert result["analysis"]["recommendation"] == "HOLD"
        assert result["analysis"]["confidence"] == 0.8
        assert len(result["analysis"]["insights"]) == 2

    @pytest.mark.asyncio
    async def test_portfolio_summary_ai_failure(self, test_db, sample_account, sample_asset):
        """Test portfolio summary when AI service fails"""
        service = PortfolioService(test_db)
        user_id = sample_account.clerk_user_id

        # Mock AI service to raise exception
        with patch.object(service, 'ai_service') as mock_ai:
            mock_ai.analyze_portfolio_fast = AsyncMock(side_effect=Exception("AI service unavailable"))

            result = await service.get_portfolio_summary(clerk_user_id=user_id)

        # Should fall back to basic analysis
        assert result["analysis"]["analysis_type"] == "basic"
        assert "recommendation" in result["analysis"]

    @pytest.mark.asyncio
    async def test_update_prices_with_mock_market_data(self, test_db, sample_account, sample_asset):
        """Test price updates with mocked market data"""
        service = PortfolioService(test_db)
        user_id = sample_account.clerk_user_id

        # Mock market data service
        mock_prices = {"AAPL": 175.0}

        with patch.object(service, 'market_data') as mock_market:
            mock_market.get_current_prices.return_value = mock_prices

            result = await service.update_prices(clerk_user_id=user_id)

        assert result["updated_assets"] >= 1
        assert "AAPL" not in result.get("failed_symbols", [])

        # Check that price was updated
        test_db.refresh(sample_asset)
        assert sample_asset.current_price == 175.0

    @pytest.mark.asyncio
    async def test_update_prices_market_data_failure(self, test_db, sample_account, sample_asset):
        """Test price updates when market data fails"""
        service = PortfolioService(test_db)
        user_id = sample_account.clerk_user_id

        # Mock market data service to return empty results
        with patch.object(service, 'market_data') as mock_market:
            mock_market.get_current_prices.return_value = {}

            result = await service.update_prices(clerk_user_id=user_id)

        assert result["updated_assets"] == 0
        assert "AAPL" in result["failed_symbols"]

class TestPortfolioServiceIntegration:
    """Test service integration scenarios"""

    @pytest.mark.asyncio
    async def test_complete_workflow(self, test_db):
        """Test complete workflow through service"""
        service = PortfolioService(test_db)
        user_id = "workflow_user"

        # Step 1: Create account
        account_data = AccountCreate(
            name="Workflow Test Account",
            account_type="brokerage"
        )
        account = service.create_account(account_data, user_id)

        # Step 2: Add multiple assets
        assets_to_add = [
            AssetCreate(
                account_id=account.id,
                symbol="AAPL",
                shares=10,
                avg_cost=150.0
            ),
            AssetCreate(
                account_id=account.id,
                symbol="MSFT",
                shares=5,
                avg_cost=300.0
            )
        ]

        for asset_data in assets_to_add:
            await service.add_asset(asset_data)

        # Step 3: Get portfolio summary with mocked AI
        with patch.object(service, 'ai_service') as mock_ai:
            mock_ai.analyze_portfolio_fast = AsyncMock(return_value={
                "recommendation": "HOLD",
                "confidence": 0.8,
                "insights": ["Diversified portfolio"]
            })

            summary = await service.get_portfolio_summary(clerk_user_id=user_id)

        # Verify complete workflow
        assert len(summary["accounts"]) == 1
        assert len(summary["accounts"][0]["assets"]) == 2
        assert summary["summary"]["total_assets"] == 2
        assert summary["summary"]["total_value"] > 0

    @pytest.mark.asyncio
    async def test_multiple_users_isolation(self, test_db):
        """Test that multiple users' data is properly isolated"""
        service = PortfolioService(test_db)

        # Create accounts for different users
        user1_account = service.create_account(
            AccountCreate(name="User 1 Account", account_type="brokerage"),
            "user_1"
        )
        user2_account = service.create_account(
            AccountCreate(name="User 2 Account", account_type="retirement"),
            "user_2"
        )

        # Add assets for each user
        await service.add_asset(AssetCreate(
            account_id=user1_account.id,
            symbol="AAPL",
            shares=10,
            avg_cost=150.0
        ))
        await service.add_asset(AssetCreate(
            account_id=user2_account.id,
            symbol="MSFT",
            shares=5,
            avg_cost=300.0
        ))

        # Get summaries for each user with mocked AI
        with patch.object(service, 'ai_service') as mock_ai:
            mock_ai.analyze_portfolio_fast = AsyncMock(return_value={"recommendation": "HOLD"})

            user1_summary = await service.get_portfolio_summary(clerk_user_id="user_1")
            user2_summary = await service.get_portfolio_summary(clerk_user_id="user_2")

        # Verify isolation
        assert len(user1_summary["accounts"]) == 1
        assert len(user2_summary["accounts"]) == 1
        assert user1_summary["accounts"][0]["name"] == "User 1 Account"
        assert user2_summary["accounts"][0]["name"] == "User 2 Account"

class TestErrorHandling:
    """Test error handling in portfolio service"""
    @pytest.mark.asyncio
    async def test_service_database_constraint_error(self, test_db):
        """Test service behavior with database constraint violations"""
        service = PortfolioService(test_db)

        # Create account first
        service.create_account(
            AccountCreate(name="Test", account_type="brokerage"),
            "user_123"
        )

        # Try to create duplicate (if you have unique constraints)
        with patch.object(test_db, 'commit', side_effect=IntegrityError("", "", "")):
            with pytest.raises(Exception):
                service.create_account(
                    AccountCreate(name="Test2", account_type="brokerage"),
                    "user_456"
                )

    @pytest.mark.asyncio
    async def test_service_rollback_on_error(self, test_db):
        """Test that service properly rolls back on errors"""
        service = PortfolioService(test_db)

        with patch.object(test_db, 'commit', side_effect=Exception("Commit failed")):
            with patch.object(test_db, 'rollback') as mock_rollback:
                try:
                    service.create_account(
                        AccountCreate(name="Test", account_type="brokerage"),
                        "user_123"
                    )
                except:
                    pass

                # Verify rollback was called
                mock_rollback.assert_called_once()

    def test_fallback_analysis(self, test_db):
        """Test fallback analysis when AI fails"""
        service = PortfolioService(test_db)

        portfolio_data = [
            {
                "assets": [
                    {"symbol": "AAPL"},
                    {"symbol": "MSFT"}
                ]
            }
        ]

        result = service._get_fallback_analysis(portfolio_data, 10000.0, 9000.0)

        assert "analysis_type" in result
        assert result["analysis_type"] == "basic"
        assert "recommendation" in result
        assert "insights" in result
        assert isinstance(result["insights"], list)
