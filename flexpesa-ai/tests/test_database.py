"""
Basic database tests
Test core database operations and models
"""

import pytest
from sqlalchemy import text
from app.models.portfolio import Account, Asset


class TestDatabaseBasics:
    """Test basic database functionality"""

    def test_database_connection(self, test_db):
        """Test database connection works"""
        result = test_db.execute(text("SELECT 1 as test"))
        assert result.scalar() == 1

    def test_create_account(self, test_db):
        """Test creating an account"""
        account = Account(
            clerk_user_id="test_user_123",
            name="Test Account",
            account_type="brokerage",
            currency="USD"
        )

        test_db.add(account)
        test_db.commit()
        test_db.refresh(account)

        assert account.id is not None
        assert account.name == "Test Account"
        assert account.account_type == "brokerage"
        assert account.is_active is True

    def test_create_asset(self, test_db, sample_account):
        """Test creating an asset"""
        asset = Asset(
            account_id=sample_account.id,
            symbol="AAPL",
            shares=10,
            avg_cost=150.0,
            current_price=155.0
        )

        test_db.add(asset)
        test_db.commit()
        test_db.refresh(asset)

        assert asset.id is not None
        assert asset.symbol == "AAPL"
        assert asset.shares == 10
        assert asset.avg_cost == 150.0

    def test_account_asset_relationship(self, test_db, sample_account, sample_asset):
        """Test account-asset relationship"""
        # Refresh to load relationship
        test_db.refresh(sample_account)

        assert len(sample_account.assets) == 1
        assert sample_account.assets[0].symbol == "AAPL"
        assert sample_asset.account_id == sample_account.id

    def test_account_total_value(self, test_db, sample_account, sample_asset):
        """Test account total value calculation"""
        test_db.refresh(sample_account)

        expected_value = sample_asset.shares * sample_asset.current_price
        assert sample_account.total_value == expected_value

    def test_asset_calculations(self, test_db, sample_asset):
        """Test asset calculation properties"""
        # Market value = shares * current_price
        expected_market_value = 10 * 155.0  # 1550
        assert sample_asset.market_value == expected_market_value

        # Cost basis = shares * avg_cost
        expected_cost_basis = 10 * 150.0  # 1500
        assert sample_asset.cost_basis == expected_cost_basis

        # P&L = market_value - cost_basis
        expected_pnl = 1550 - 1500  # 50
        assert sample_asset.unrealized_pnl == expected_pnl

        # P&L % = (pnl / cost_basis) * 100
        expected_pnl_percent = (50 / 1500) * 100  # 3.33%
        assert abs(sample_asset.unrealized_pnl_percent - expected_pnl_percent) < 0.01

    def test_query_accounts(self, test_db, sample_account):
        """Test querying accounts"""
        accounts = test_db.query(Account).all()
        assert len(accounts) == 1
        assert accounts[0].name == "Test Account"

    def test_query_assets(self, test_db, sample_asset):
        """Test querying assets"""
        assets = test_db.query(Asset).all()
        assert len(assets) == 1
        assert assets[0].symbol == "AAPL"

    def test_query_by_user(self, test_db, sample_account):
        """Test querying by user ID"""
        user_accounts = test_db.query(Account).filter(
            Account.clerk_user_id == "test_user_123"
        ).all()

        assert len(user_accounts) == 1
        assert user_accounts[0].id == sample_account.id

    def test_update_account(self, test_db, sample_account):
        """Test updating account"""
        sample_account.name = "Updated Account"
        test_db.commit()
        test_db.refresh(sample_account)

        assert sample_account.name == "Updated Account"

    def test_update_asset_price(self, test_db, sample_asset):
        """Test updating asset price"""
        old_market_value = sample_asset.market_value

        sample_asset.current_price = 160.0
        test_db.commit()
        test_db.refresh(sample_asset)

        new_market_value = sample_asset.market_value
        assert new_market_value != old_market_value
        assert sample_asset.current_price == 160.0

    def test_delete_asset(self, test_db, sample_asset):
        """Test deleting asset"""
        asset_id = sample_asset.id

        test_db.delete(sample_asset)
        test_db.commit()

        deleted_asset = test_db.query(Asset).filter(Asset.id == asset_id).first()
        assert deleted_asset is None

    def test_account_with_multiple_assets(self, test_db, sample_account):
        """Test account with multiple assets"""
        # Add second asset
        asset2 = Asset(
            account_id=sample_account.id,
            symbol="MSFT",
            shares=5,
            avg_cost=300.0,
            current_price=310.0
        )
        test_db.add(asset2)
        test_db.commit()

        # Refresh account
        test_db.refresh(sample_account)

        assert len(sample_account.assets) == 2

        # Check total value calculation
        expected_total = (10 * 155.0) + (5 * 310.0)  # AAPL + MSFT
        assert sample_account.total_value == expected_total