"""
Database operations and model tests
Tests database models, relationships, and data integrity
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from app.models.portfolio import Account, Asset, MarketData, PortfolioSnapshot
from app.core.database import check_database_connection
from conftest import skip_if_production


class TestDatabaseConnection:
    """Test database connectivity and health"""

    def test_database_connection(self, test_db_session: Session):
        """Test basic database connection"""
        result = test_db_session.execute(text("SELECT 1 as test"))
        assert result.scalar() == 1

    def test_database_health_check(self):
        """Test database health check function"""
        assert check_database_connection() is True

    def test_database_tables_exist(self, test_db_session: Session):
        """Test that all required tables exist"""
        # Check if tables exist by querying them
        test_db_session.execute(text("SELECT COUNT(*) FROM accounts"))
        test_db_session.execute(text("SELECT COUNT(*) FROM assets"))
        test_db_session.execute(text("SELECT COUNT(*) FROM market_data_cache"))
        test_db_session.execute(text("SELECT COUNT(*) FROM portfolio_snapshots"))


class TestAccountModel:
    """Test Account model operations"""

    def test_create_account(self, test_db_session: Session):
        """Test creating a basic account"""
        account = Account(
            clerk_user_id="test_user_123",
            name="Test Account",
            account_type="brokerage",
            description="Test account for unit tests",
            currency="USD"
        )
        
        test_db_session.add(account)
        test_db_session.commit()
        test_db_session.refresh(account)
        
        assert account.id is not None
        assert account.name == "Test Account"
        assert account.account_type == "brokerage"
        assert account.clerk_user_id == "test_user_123"
        assert account.is_active is True
        assert account.created_at is not None

    def test_account_default_values(self, test_db_session: Session):
        """Test account default values"""
        account = Account(
            clerk_user_id="test_user_123",
            name="Test Account",
            account_type="brokerage"
        )
        
        test_db_session.add(account)
        test_db_session.commit()
        test_db_session.refresh(account)
        
        assert account.balance == 0.0
        assert account.currency == "USD"
        assert account.is_active is True

    def test_account_total_value_property(self, test_db_session: Session):
        """Test account total_value calculated property"""
        account = Account(
            clerk_user_id="test_user_123",
            name="Test Account",
            account_type="brokerage"
        )
        test_db_session.add(account)
        test_db_session.commit()
        test_db_session.refresh(account)
        
        # Add assets to test total value calculation
        asset1 = Asset(
            account_id=account.id,
            symbol="TEST1",
            shares=10,
            avg_cost=100.0,
            current_price=110.0,
            is_active=True
        )
        asset2 = Asset(
            account_id=account.id,
            symbol="TEST2", 
            shares=5,
            avg_cost=200.0,
            current_price=190.0,
            is_active=True
        )
        
        test_db_session.add_all([asset1, asset2])
        test_db_session.commit()
        
        # Refresh to load relationship
        test_db_session.refresh(account)
        
        expected_total = (10 * 110.0) + (5 * 190.0)  # 1100 + 950 = 2050
        assert account.total_value == expected_total

    def test_account_to_dict(self, test_db_session: Session):
        """Test account to_dict method"""
        account = Account(
            clerk_user_id="test_user_123",
            name="Test Account",
            account_type="brokerage",
            description="Test description"
        )
        test_db_session.add(account)
        test_db_session.commit()
        test_db_session.refresh(account)
        
        account_dict = account.to_dict()
        
        assert isinstance(account_dict, dict)
        assert account_dict["name"] == "Test Account"
        assert account_dict["account_type"] == "brokerage"
        assert account_dict["clerk_user_id"] == "test_user_123"
        assert "created_at" in account_dict
        assert "total_value" in account_dict
        assert "asset_count" in account_dict

    def test_account_relationships(self, test_db_session: Session):
        """Test account-asset relationships"""
        account = Account(
            clerk_user_id="test_user_123",
            name="Test Account",
            account_type="brokerage"
        )
        test_db_session.add(account)
        test_db_session.commit()
        test_db_session.refresh(account)
        
        # Add assets
        asset = Asset(
            account_id=account.id,
            symbol="TEST",
            shares=10,
            avg_cost=100.0,
            current_price=110.0
        )
        test_db_session.add(asset)
        test_db_session.commit()
        
        # Test relationship access
        test_db_session.refresh(account)
        assert len(account.assets) == 1
        assert account.assets[0].symbol == "TEST"

    @skip_if_production("Requires database modifications")
    def test_account_cascade_delete(self, test_db_session: Session):
        """Test that deleting account cascades to assets"""
        account = Account(
            clerk_user_id="test_user_123",
            name="Test Account",
            account_type="brokerage"
        )
        test_db_session.add(account)
        test_db_session.commit()
        test_db_session.refresh(account)
        
        # Add asset
        asset = Asset(
            account_id=account.id,
            symbol="TEST",
            shares=10,
            avg_cost=100.0,
            current_price=110.0
        )
        test_db_session.add(asset)
        test_db_session.commit()
        
        asset_id = asset.id
        
        # Delete account
        test_db_session.delete(account)
        test_db_session.commit()
        
        # Check that asset is also deleted
        deleted_asset = test_db_session.query(Asset).filter(Asset.id == asset_id).first()
        assert deleted_asset is None


class TestAssetModel:
    """Test Asset model operations"""

    def test_create_asset(self, test_db_session: Session):
        """Test creating a basic asset"""
        # Create account first
        account = Account(
            clerk_user_id="test_user_123",
            name="Test Account",
            account_type="brokerage"
        )
        test_db_session.add(account)
        test_db_session.commit()
        test_db_session.refresh(account)
        
        asset = Asset(
            account_id=account.id,
            symbol="AAPL",
            shares=10,
            avg_cost=150.0,
            current_price=155.0,
            name="Apple Inc.",
            asset_type="stock",
            sector="Technology"
        )
        
        test_db_session.add(asset)
        test_db_session.commit()
        test_db_session.refresh(asset)
        
        assert asset.id is not None
        assert asset.symbol == "AAPL"
        assert asset.shares == 10
        assert asset.avg_cost == 150.0
        assert asset.current_price == 155.0
        assert asset.is_active is True

    def test_asset_calculated_properties(self, test_db_session: Session):
        """Test asset calculated properties"""
        account = Account(
            clerk_user_id="test_user_123",
            name="Test Account",
            account_type="brokerage"
        )
        test_db_session.add(account)
        test_db_session.commit()
        test_db_session.refresh(account)
        
        asset = Asset(
            account_id=account.id,
            symbol="TEST",
            shares=10,
            avg_cost=100.0,
            current_price=110.0
        )
        test_db_session.add(asset)
        test_db_session.commit()
        
        # Test calculated properties
        assert asset.market_value == 1100.0  # 10 * 110
        assert asset.cost_basis == 1000.0    # 10 * 100
        assert asset.unrealized_pnl == 100.0 # 1100 - 1000
        assert asset.unrealized_pnl_percent == 10.0  # (100/1000) * 100

    def test_asset_zero_cost_basis(self, test_db_session: Session):
        """Test asset with zero cost basis"""
        account = Account(
            clerk_user_id="test_user_123",
            name="Test Account",
            account_type="brokerage"
        )
        test_db_session.add(account)
        test_db_session.commit()
        test_db_session.refresh(account)
        
        asset = Asset(
            account_id=account.id,
            symbol="FREE",
            shares=10,
            avg_cost=0.0,
            current_price=10.0
        )
        test_db_session.add(asset)
        test_db_session.commit()
        
        assert asset.unrealized_pnl_percent == 0.0

    def test_asset_to_dict(self, test_db_session: Session):
        """Test asset to_dict method"""
        account = Account(
            clerk_user_id="test_user_123",
            name="Test Account",
            account_type="brokerage"
        )
        test_db_session.add(account)
        test_db_session.commit()
        test_db_session.refresh(account)
        
        asset = Asset(
            account_id=account.id,
            symbol="TEST",
            shares=10,
            avg_cost=100.0,
            current_price=110.0,
            name="Test Asset",
            asset_type="stock"
        )
        test_db_session.add(asset)
        test_db_session.commit()
        
        asset_dict = asset.to_dict()
        
        assert isinstance(asset_dict, dict)
        assert asset_dict["symbol"] == "TEST"
        assert asset_dict["shares"] == 10
        assert asset_dict["market_value"] == 1100.0
        assert asset_dict["unrealized_pnl"] == 100.0
        assert "created_at" in asset_dict

    def test_asset_foreign_key_constraint(self, test_db_session: Session):
        """Test foreign key constraint on asset"""
        with pytest.raises(IntegrityError):
            asset = Asset(
                account_id=99999,  # Non-existent account
                symbol="TEST",
                shares=10,
                avg_cost=100.0
            )
            test_db_session.add(asset)
            test_db_session.commit()


class TestMarketDataModel:
    """Test MarketData model operations"""

    def test_create_market_data(self, test_db_session: Session):
        """Test creating market data entry"""
        market_data = MarketData(
            symbol="AAPL",
            name="Apple Inc.",
            current_price=155.50,
            open_price=154.00,
            high_price=157.00,
            low_price=153.00,
            volume=1000000,
            sector="Technology",
            asset_type="stock"
        )
        
        test_db_session.add(market_data)
        test_db_session.commit()
        test_db_session.refresh(market_data)
        
        assert market_data.id is not None
        assert market_data.symbol == "AAPL"
        assert market_data.current_price == 155.50
        assert market_data.created_at is not None

    def test_market_data_unique_symbol(self, test_db_session: Session):
        """Test unique constraint on market data symbol"""
        market_data1 = MarketData(
            symbol="TEST",
            current_price=100.0
        )
        test_db_session.add(market_data1)
        test_db_session.commit()
        
        # Try to add another with same symbol
        with pytest.raises(IntegrityError):
            market_data2 = MarketData(
                symbol="TEST",
                current_price=110.0
            )
            test_db_session.add(market_data2)
            test_db_session.commit()

    def test_market_data_is_stale(self, test_db_session: Session):
        """Test market data staleness check"""
        # Create fresh market data
        market_data = MarketData(
            symbol="FRESH",
            current_price=100.0
        )
        test_db_session.add(market_data)
        test_db_session.commit()
        test_db_session.refresh(market_data)
        
        # Should not be stale
        assert not market_data.is_stale(max_age_minutes=5)
        
        # Make it old
        old_time = datetime.utcnow() - timedelta(minutes=10)
        market_data.updated_at = old_time
        test_db_session.commit()
        
        # Should be stale now
        assert market_data.is_stale(max_age_minutes=5)

    def test_market_data_to_dict(self, test_db_session: Session):
        """Test market data to_dict method"""
        market_data = MarketData(
            symbol="TEST",
            name="Test Asset",
            current_price=100.0,
            sector="Technology"
        )
        test_db_session.add(market_data)
        test_db_session.commit()
        
        data_dict = market_data.to_dict()
        
        assert isinstance(data_dict, dict)
        assert data_dict["symbol"] == "TEST"
        assert data_dict["current_price"] == 100.0
        assert "updated_at" in data_dict


class TestPortfolioSnapshotModel:
    """Test PortfolioSnapshot model operations"""

    def test_create_portfolio_snapshot(self, test_db_session: Session):
        """Test creating portfolio snapshot"""
        snapshot = PortfolioSnapshot(
            clerk_user_id="test_user_123",
            total_value=10000.0,
            total_cost_basis=9000.0,
            total_pnl=1000.0,
            total_pnl_percent=11.11,
            asset_count=5,
            account_count=2,
            snapshot_type="daily"
        )
        
        test_db_session.add(snapshot)
        test_db_session.commit()
        test_db_session.refresh(snapshot)
        
        assert snapshot.id is not None
        assert snapshot.clerk_user_id == "test_user_123"
        assert snapshot.total_value == 10000.0
        assert snapshot.snapshot_type == "daily"
        assert snapshot.created_at is not None

    def test_portfolio_snapshot_to_dict(self, test_db_session: Session):
        """Test portfolio snapshot to_dict method"""
        snapshot = PortfolioSnapshot(
            clerk_user_id="test_user_123",
            total_value=10000.0,
            total_cost_basis=9000.0,
            total_pnl=1000.0,
            total_pnl_percent=11.11,
            asset_count=5,
            account_count=2
        )
        test_db_session.add(snapshot)
        test_db_session.commit()
        
        snapshot_dict = snapshot.to_dict()
        
        assert isinstance(snapshot_dict, dict)
        assert snapshot_dict["total_value"] == 10000.0
        assert snapshot_dict["total_pnl"] == 1000.0
        assert "created_at" in snapshot_dict


class TestDatabaseQueries:
    """Test common database queries"""

    def test_query_accounts_by_user(self, test_db_session: Session):
        """Test querying accounts by user ID"""
        # Create accounts for different users
        account1 = Account(
            clerk_user_id="user_123",
            name="Account 1",
            account_type="brokerage"
        )
        account2 = Account(
            clerk_user_id="user_456", 
            name="Account 2",
            account_type="retirement"
        )
        account3 = Account(
            clerk_user_id="user_123",
            name="Account 3", 
            account_type="trading"
        )
        
        test_db_session.add_all([account1, account2, account3])
        test_db_session.commit()
        
        # Query accounts for user_123
        user_123_accounts = test_db_session.query(Account).filter(
            Account.clerk_user_id == "user_123",
            Account.is_active == True
        ).all()
        
        assert len(user_123_accounts) == 2
        account_names = [acc.name for acc in user_123_accounts]
        assert "Account 1" in account_names
        assert "Account 3" in account_names

    def test_query_assets_with_joins(self, test_db_session: Session):
        """Test querying assets with account joins"""
        account = Account(
            clerk_user_id="test_user",
            name="Test Account",
            account_type="brokerage"
        )
        test_db_session.add(account)
        test_db_session.commit()
        test_db_session.refresh(account)
        
        asset = Asset(
            account_id=account.id,
            symbol="AAPL",
            shares=10,
            avg_cost=150.0,
            current_price=155.0
        )
        test_db_session.add(asset)
        test_db_session.commit()
        
        # Query assets with account information
        result = test_db_session.query(Asset, Account).join(Account).filter(
            Account.clerk_user_id == "test_user"
        ).all()
        
        assert len(result) == 1
        asset_result, account_result = result[0]
        assert asset_result.symbol == "AAPL"
        assert account_result.name == "Test Account"

    def test_query_portfolio_performance_data(self, test_db_session: Session):
        """Test querying data for performance calculations"""
        account = Account(
            clerk_user_id="test_user",
            name="Performance Test Account",
            account_type="brokerage"
        )
        test_db_session.add(account)
        test_db_session.commit()
        test_db_session.refresh(account)
        
        assets = [
            Asset(
                account_id=account.id,
                symbol="AAPL",
                shares=10,
                avg_cost=150.0,
                current_price=155.0
            ),
            Asset(
                account_id=account.id,
                symbol="MSFT",
                shares=5,
                avg_cost=300.0,
                current_price=310.0
            )
        ]
        
        test_db_session.add_all(assets)
        test_db_session.commit()
        
        # Query for portfolio performance calculation
        portfolio_data = test_db_session.query(Asset).join(Account).filter(
            Account.clerk_user_id == "test_user",
            Asset.is_active == True
        ).all()
        
        assert len(portfolio_data) == 2
        
        total_market_value = sum(asset.market_value for asset in portfolio_data)
        total_cost_basis = sum(asset.cost_basis for asset in portfolio_data)
        
        assert total_market_value == (10 * 155.0) + (5 * 310.0)  # 1550 + 1550 = 3100
        assert total_cost_basis == (10 * 150.0) + (5 * 300.0)    # 1500 + 1500 = 3000

    def test_query_historical_snapshots(self, test_db_session: Session):
        """Test querying historical portfolio snapshots"""
        user_id = "test_user"
        
        # Create snapshots for different dates
        snapshots = []
        for i in range(5):
            snapshot = PortfolioSnapshot(
                clerk_user_id=user_id,
                total_value=10000.0 + (i * 100),  # Increasing value
                total_cost_basis=9000.0,
                total_pnl=1000.0 + (i * 100),
                total_pnl_percent=11.11,
                asset_count=5,
                account_count=2,
                snapshot_type="daily"
            )
            snapshots.append(snapshot)
        
        test_db_session.add_all(snapshots)
        test_db_session.commit()
        
        # Query recent snapshots
        recent_snapshots = test_db_session.query(PortfolioSnapshot).filter(
            PortfolioSnapshot.clerk_user_id == user_id
        ).order_by(PortfolioSnapshot.created_at.desc()).limit(3).all()
        
        assert len(recent_snapshots) == 3
        # Check they're ordered by newest first
        assert recent_snapshots[0].total_value >= recent_snapshots[1].total_value


class TestDatabaseIntegrity:
    """Test database integrity and constraints"""

    def test_account_required_fields(self, test_db_session: Session):
        """Test that required fields are enforced"""
        with pytest.raises(IntegrityError):
            # Missing required fields
            account = Account(clerk_user_id="test")
            test_db_session.add(account)
            test_db_session.commit()

    def test_asset_required_fields(self, test_db_session: Session):
        """Test that asset required fields are enforced"""
        account = Account(
            clerk_user_id="test_user",
            name="Test Account",
            account_type="brokerage"
        )
        test_db_session.add(account)
        test_db_session.commit()
        test_db_session.refresh(account)
        
        with pytest.raises(IntegrityError):
            # Missing required fields
            asset = Asset(account_id=account.id)
            test_db_session.add(asset)
            test_db_session.commit()

    def test_data_consistency_after_updates(self, test_db_session: Session):
        """Test data consistency after updates"""
        account = Account(
            clerk_user_id="test_user",
            name="Test Account",
            account_type="brokerage"
        )
        test_db_session.add(account)
        test_db_session.commit()
        test_db_session.refresh(account)
        
        asset = Asset(
            account_id=account.id,
            symbol="TEST",
            shares=10,
            avg_cost=100.0,
            current_price=100.0
        )
        test_db_session.add(asset)
        test_db_session.commit()
        
        original_value = asset.market_value
        
        # Update price
        asset.current_price = 110.0
        test_db_session.commit()
        
        # Verify value changed
        test_db_session.refresh(asset)
        assert asset.market_value != original_value
        assert asset.market_value == 1100.0


@pytest.mark.slow
class TestDatabasePerformance:
    """Test database performance with larger datasets"""

    @skip_if_production("Creates large test dataset")
    def test_query_performance_large_dataset(self, test_db_session: Session):
        """Test query performance with larger dataset"""
        # Create multiple accounts and assets
        accounts = []
        for i in range(10):
            account = Account(
                clerk_user_id=f"user_{i}",
                name=f"Account {i}",
                account_type="brokerage"
            )
            accounts.append(account)
        
        test_db_session.add_all(accounts)
        test_db_session.commit()
        
        assets = []
        symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
        for account in accounts:
            for j, symbol in enumerate(symbols):
                asset = Asset(
                    account_id=account.id,
                    symbol=symbol,
                    shares=10 + j,
                    avg_cost=100.0 + j * 10,
                    current_price=105.0 + j * 10
                )
                assets.append(asset)
        
        test_db_session.add_all(assets)
        test_db_session.commit()
        
        # Test query performance
        import time
        start_time = time.time()
        
        result = test_db_session.query(Account, Asset).join(Asset).filter(
            Account.clerk_user_id.like("user_%")
        ).all()
        
        query_time = time.time() - start_time
        
        assert len(result) == 50  # 10 accounts * 5 assets each
        assert query_time < 1.0   # Should be fast even with more data
