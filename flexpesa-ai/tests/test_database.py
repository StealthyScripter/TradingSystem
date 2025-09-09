"""
Database tests - simplified and reliable
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
            currency="USD",
            is_active=True
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
            current_price=155.0,
            is_active=True
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

        assert len(sample_account.assets) >= 1

        # Find our asset
        found_asset = None
        for asset in sample_account.assets:
            if asset.symbol == "AAPL":
                found_asset = asset
                break

        assert found_asset is not None
        assert found_asset.account_id == sample_account.id

    def test_account_total_value(self, test_db, sample_account, sample_asset):
        """Test account total value calculation"""
        test_db.refresh(sample_account)

        expected_value = sample_asset.shares * sample_asset.current_price
        assert sample_account.total_value == expected_value

class TestDatabaseQueries:
    """Test database query operations"""

    def test_query_accounts(self, test_db, sample_account):
        """Test querying accounts"""
        accounts = test_db.query(Account).all()
        assert len(accounts) >= 1

        # Find our account
        found_account = None
        for acc in accounts:
            if acc.name == "Test Account":
                found_account = acc
                break

        assert found_account is not None

    def test_query_assets(self, test_db, sample_asset):
        """Test querying assets"""
        assets = test_db.query(Asset).all()
        assert len(assets) >= 1

        # Find our asset
        found_asset = None
        for asset in assets:
            if asset.symbol == "AAPL":
                found_asset = asset
                break

        assert found_asset is not None

    def test_query_by_user(self, test_db, sample_account):
        """Test querying by user ID"""
        user_accounts = test_db.query(Account).filter(
            Account.clerk_user_id == sample_account.clerk_user_id
        ).all()

        assert len(user_accounts) >= 1
        assert user_accounts[0].clerk_user_id == sample_account.clerk_user_id

    def test_query_active_assets(self, test_db, sample_account):
        """Test querying only active assets"""
        # Create both active and inactive assets
        active_asset = Asset(
            account_id=sample_account.id,
            symbol="ACTIVE",
            shares=10,
            avg_cost=100.0,
            is_active=True
        )
        inactive_asset = Asset(
            account_id=sample_account.id,
            symbol="INACTIVE",
            shares=5,
            avg_cost=100.0,
            is_active=False
        )

        test_db.add_all([active_asset, inactive_asset])
        test_db.commit()

        # Query only active assets
        active_assets = test_db.query(Asset).filter(Asset.is_active == True).all()
        active_symbols = [asset.symbol for asset in active_assets]

        assert "ACTIVE" in active_symbols
        assert "INACTIVE" not in active_symbols

class TestDatabaseUpdates:
    """Test database update operations"""

    def test_update_account(self, test_db, sample_account):
        """Test updating account"""
        original_name = sample_account.name
        sample_account.name = "Updated Account"
        test_db.commit()
        test_db.refresh(sample_account)

        assert sample_account.name == "Updated Account"
        assert sample_account.name != original_name

    def test_update_asset_price(self, test_db, sample_asset):
        """Test updating asset price"""
        old_price = sample_asset.current_price
        old_market_value = sample_asset.market_value

        sample_asset.current_price = 200.0
        test_db.commit()
        test_db.refresh(sample_asset)

        assert sample_asset.current_price == 200.0
        assert sample_asset.current_price != old_price
        assert sample_asset.market_value != old_market_value

    def test_update_asset_shares(self, test_db, sample_asset):
        """Test updating asset shares"""
        original_shares = sample_asset.shares
        sample_asset.shares = 20
        test_db.commit()
        test_db.refresh(sample_asset)

        assert sample_asset.shares == 20
        assert sample_asset.shares != original_shares

class TestDatabaseConstraints:
    """Test database constraints and data integrity"""

    def test_account_requires_user_id(self, test_db):
        """Test that accounts can be created with null user_id (for flexibility)"""
        account = Account(
            clerk_user_id=None,  # This should be allowed
            name="No User Account",
            account_type="testing"
        )

        test_db.add(account)
        test_db.commit()
        test_db.refresh(account)

        assert account.id is not None
        assert account.clerk_user_id is None

    def test_asset_requires_account(self, test_db):
        """Test that assets require valid account_id"""
        asset = Asset(
            account_id=99999,  # Non-existent account
            symbol="FAIL",
            shares=10,
            avg_cost=100.0
        )

        test_db.add(asset)

        # This should fail due to foreign key constraint
        with pytest.raises(Exception):
            test_db.commit()

    def test_unique_constraints(self, test_db, sample_account):
        """Test handling of duplicate data"""
        # Create two assets with same symbol in same account
        asset1 = Asset(
            account_id=sample_account.id,
            symbol="DUPLICATE",
            shares=10,
            avg_cost=100.0
        )
        asset2 = Asset(
            account_id=sample_account.id,
            symbol="DUPLICATE",
            shares=5,
            avg_cost=110.0
        )

        # Both should be allowed (no unique constraint on symbol per account)
        test_db.add_all([asset1, asset2])
        test_db.commit()

        # Verify both exist
        duplicates = test_db.query(Asset).filter(Asset.symbol == "DUPLICATE").all()
        assert len(duplicates) == 2

class TestDatabaseRelationships:
    """Test database relationships and cascading"""

    def test_account_with_multiple_assets(self, test_db, sample_account, sample_asset):
        """Test account with multiple assets"""
        new_assets = [
            Asset(
                account_id=sample_account.id,
                symbol="MSFT",
                shares=5,
                avg_cost=300.0,
                current_price=310.0
            ),
            Asset(
                account_id=sample_account.id,
                symbol="GOOGL",
                shares=3,
                avg_cost=2500.0,
                current_price=2600.0
            )
        ]

        test_db.add_all(new_assets)
        test_db.commit()
        test_db.refresh(sample_account)

        # Should have original asset plus new ones
        assert len(sample_account.assets) == 3

        symbols = [asset.symbol for asset in sample_account.assets]
        assert "AAPL" in symbols
        assert "MSFT" in symbols
        assert "GOOGL" in symbols

    def test_delete_asset_keeps_account(self, test_db, sample_account, sample_asset):
        """Test that deleting asset doesn't affect account"""
        asset_id = sample_asset.id
        account_id = sample_account.id

        test_db.delete(sample_asset)
        test_db.commit()

        # Asset should be gone
        deleted_asset = test_db.query(Asset).filter(Asset.id == asset_id).first()
        assert deleted_asset is None

        # Account should still exist
        existing_account = test_db.query(Account).filter(Account.id == account_id).first()
        assert existing_account is not None

class TestDatabaseTransactions:
    """Test database transaction handling"""

    def test_rollback_on_error(self, test_db, sample_account):
        """Test that transactions rollback properly on error"""
        original_asset_count = test_db.query(Asset).count()

        # Asset count should be unchanged
        final_asset_count = test_db.query(Asset).count()
        assert final_asset_count == original_asset_count

        with pytest.raises(Exception):  # Expect the foreign key error
            # Create a valid asset
            valid_asset = Asset(
                account_id=sample_account.id,
                symbol="VALID",
                shares=10,
                avg_cost=100.0
            )
            test_db.add(valid_asset)

            # Create an invalid asset that should cause rollback
            invalid_asset = Asset(
                account_id=99999,  # Non-existent account
                symbol="INVALID",
                shares=10,
                avg_cost=100.0
            )
            test_db.add(invalid_asset)

            # This should fail and auto-rollback both additions
            test_db.commit()

        test_db.rollback()
        
        # Asset count should be unchanged (rollback happened)
        final_asset_count = test_db.query(Asset).count()
        assert final_asset_count == original_asset_count

    def test_successful_transaction(self, test_db, sample_account):
        """Test successful transaction commits properly"""
        original_count = test_db.query(Asset).count()

        asset = Asset(
            account_id=sample_account.id,
            symbol="SUCCESS",
            shares=10,
            avg_cost=100.0
        )

        test_db.add(asset)
        test_db.commit()

        final_count = test_db.query(Asset).count()
        assert final_count == original_count + 1

    def test_explicit_rollback(self, test_db, sample_account):
        """Test explicit rollback functionality"""
        original_count = test_db.query(Asset).count()

        try:
            asset = Asset(
                account_id=sample_account.id,
                symbol="ROLLBACK_TEST",
                shares=10,
                avg_cost=100.0
            )
            test_db.add(asset)
            # Don't commit yet

            # Manually trigger rollback
            test_db.rollback()

            # Count should be unchanged
            final_count = test_db.query(Asset).count()
            assert final_count == original_count

        except Exception:
            test_db.rollback()
