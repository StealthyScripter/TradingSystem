"""
Basic calculation tests
Test core financial calculations and portfolio math
"""

import pytest
from app.models.portfolio import Account, Asset


class TestAssetCalculations:
    """Test individual asset calculations"""

    def test_market_value_calculation(self, test_db):
        """Test asset market value calculation"""
        asset = Asset(
            account_id=1,
            symbol="AAPL",
            shares=10,
            avg_cost=150.0,
            current_price=160.0
        )

        expected_value = 10 * 160.0  # 1600
        assert asset.market_value == expected_value

    def test_cost_basis_calculation(self, test_db):
        """Test asset cost basis calculation"""
        asset = Asset(
            account_id=1,
            symbol="AAPL",
            shares=10,
            avg_cost=150.0,
            current_price=160.0
        )

        expected_cost = 10 * 150.0  # 1500
        assert asset.cost_basis == expected_cost

    def test_unrealized_pnl_calculation(self, test_db):
        """Test unrealized P&L calculation"""
        asset = Asset(
            account_id=1,
            symbol="AAPL",
            shares=10,
            avg_cost=150.0,
            current_price=160.0
        )

        # P&L = (shares * current_price) - (shares * avg_cost)
        expected_pnl = (10 * 160.0) - (10 * 150.0)  # 1600 - 1500 = 100
        assert asset.unrealized_pnl == expected_pnl

    def test_unrealized_pnl_percentage(self, test_db):
        """Test unrealized P&L percentage calculation"""
        asset = Asset(
            account_id=1,
            symbol="AAPL",
            shares=10,
            avg_cost=150.0,
            current_price=160.0
        )

        # P&L % = (unrealized_pnl / cost_basis) * 100
        # (100 / 1500) * 100 = 6.67%
        expected_pnl_percent = (100 / 1500) * 100
        assert abs(asset.unrealized_pnl_percent - expected_pnl_percent) < 0.01

    def test_negative_pnl_calculation(self, test_db):
        """Test negative P&L calculation (loss)"""
        asset = Asset(
            account_id=1,
            symbol="AAPL",
            shares=10,
            avg_cost=150.0,
            current_price=140.0  # Price dropped
        )

        expected_pnl = (10 * 140.0) - (10 * 150.0)  # 1400 - 1500 = -100
        assert asset.unrealized_pnl == expected_pnl
        assert asset.unrealized_pnl < 0

    def test_zero_cost_basis_edge_case(self, test_db):
        """Test edge case with zero cost basis"""
        asset = Asset(
            account_id=1,
            symbol="FREE",
            shares=10,
            avg_cost=0.0,
            current_price=10.0
        )

        assert asset.cost_basis == 0.0
        assert asset.market_value == 100.0
        assert asset.unrealized_pnl == 100.0
        assert asset.unrealized_pnl_percent == 0.0  # Should handle division by zero

    def test_fractional_shares(self, test_db):
        """Test calculations with fractional shares"""
        asset = Asset(
            account_id=1,
            symbol="FRACTIONAL",
            shares=2.5,
            avg_cost=100.0,
            current_price=110.0
        )

        assert asset.cost_basis == 250.0  # 2.5 * 100
        assert asset.market_value == 275.0  # 2.5 * 110
        assert asset.unrealized_pnl == 25.0  # 275 - 250

    def test_high_precision_calculations(self, test_db):
        """Test calculations with high precision numbers"""
        asset = Asset(
            account_id=1,
            symbol="PRECISE",
            shares=0.123456,
            avg_cost=150.789,
            current_price=155.123
        )

        expected_cost = 0.123456 * 150.789
        expected_value = 0.123456 * 155.123
        expected_pnl = expected_value - expected_cost

        assert abs(asset.cost_basis - expected_cost) < 0.000001
        assert abs(asset.market_value - expected_value) < 0.000001
        assert abs(asset.unrealized_pnl - expected_pnl) < 0.000001


class TestAccountCalculations:
    """Test account-level calculations"""

    def test_single_asset_account_value(self, test_db, sample_account):
        """Test account value with single asset"""
        asset = Asset(
            account_id=sample_account.id,
            symbol="AAPL",
            shares=10,
            avg_cost=150.0,
            current_price=160.0
        )
        test_db.add(asset)
        test_db.commit()

        test_db.refresh(sample_account)

        expected_value = 10 * 160.0  # 1600
        assert sample_account.total_value == expected_value

    def test_multiple_assets_account_value(self, test_db, sample_account):
        """Test account value with multiple assets"""
        asset1 = Asset(
            account_id=sample_account.id,
            symbol="AAPL",
            shares=10,
            avg_cost=150.0,
            current_price=160.0
        )
        asset2 = Asset(
            account_id=sample_account.id,
            symbol="MSFT",
            shares=5,
            avg_cost=300.0,
            current_price=320.0
        )
        test_db.add_all([asset1, asset2])
        test_db.commit()

        test_db.refresh(sample_account)

        expected_value = (10 * 160.0) + (5 * 320.0)  # 1600 + 1600 = 3200
        assert sample_account.total_value == expected_value

    def test_account_value_with_inactive_assets(self, test_db, sample_account):
        """Test that inactive assets are excluded from account value"""
        active_asset = Asset(
            account_id=sample_account.id,
            symbol="AAPL",
            shares=10,
            avg_cost=150.0,
            current_price=160.0,
            is_active=True
        )
        inactive_asset = Asset(
            account_id=sample_account.id,
            symbol="SOLD",
            shares=5,
            avg_cost=100.0,
            current_price=200.0,
            is_active=False
        )
        test_db.add_all([active_asset, inactive_asset])
        test_db.commit()

        test_db.refresh(sample_account)

        # Should only include active asset
        expected_value = 10 * 160.0  # 1600
        assert sample_account.total_value == expected_value

    def test_empty_account_value(self, test_db, sample_account):
        """Test account value with no assets"""
        test_db.refresh(sample_account)
        assert sample_account.total_value == 0

    def test_account_value_fallback_to_avg_cost(self, test_db, sample_account):
        """Test account value calculation when current_price is None"""
        asset = Asset(
            account_id=sample_account.id,
            symbol="NO_PRICE",
            shares=10,
            avg_cost=150.0,
            current_price=None  # No current price
        )
        test_db.add(asset)
        test_db.commit()

        test_db.refresh(sample_account)

        # Should use avg_cost when current_price is None
        expected_value = 10 * 150.0  # 1500
        assert sample_account.total_value == expected_value


class TestPortfolioCalculations:
    """Test portfolio-level calculations"""

    def test_simple_portfolio_totals(self, test_db, sample_user):
        """Test portfolio totals across multiple accounts"""
        # Create two accounts
        account1 = Account(
            clerk_user_id=sample_user["sub"],
            name="Account 1",
            account_type="brokerage"
        )
        account2 = Account(
            clerk_user_id=sample_user["sub"],
            name="Account 2",
            account_type="retirement"
        )
        test_db.add_all([account1, account2])
        test_db.commit()
        test_db.refresh(account1)
        test_db.refresh(account2)

        # Add assets to each account
        asset1 = Asset(
            account_id=account1.id,
            symbol="AAPL",
            shares=10,
            avg_cost=150.0,
            current_price=160.0
        )
        asset2 = Asset(
            account_id=account2.id,
            symbol="MSFT",
            shares=5,
            avg_cost=300.0,
            current_price=320.0
        )
        test_db.add_all([asset1, asset2])
        test_db.commit()

        # Calculate portfolio totals
        test_db.refresh(account1)
        test_db.refresh(account2)

        total_portfolio_value = account1.total_value + account2.total_value
        expected_value = (10 * 160.0) + (5 * 320.0)  # 1600 + 1600 = 3200
        assert total_portfolio_value == expected_value

    def test_portfolio_cost_vs_market_value(self, test_db, sample_account):
        """Test cost basis vs market value calculations"""
        assets = [
            Asset(
                account_id=sample_account.id,
                symbol="WINNER",
                shares=10,
                avg_cost=100.0,
                current_price=120.0  # 20% gain
            ),
            Asset(
                account_id=sample_account.id,
                symbol="LOSER",
                shares=5,
                avg_cost=200.0,
                current_price=180.0  # 10% loss
            )
        ]
        test_db.add_all(assets)
        test_db.commit()

        test_db.refresh(sample_account)

        # Calculate totals
        total_cost_basis = sum(asset.cost_basis for asset in sample_account.assets)
        total_market_value = sample_account.total_value
        total_pnl = total_market_value - total_cost_basis

        expected_cost = (10 * 100.0) + (5 * 200.0)  # 1000 + 1000 = 2000
        expected_market = (10 * 120.0) + (5 * 180.0)  # 1200 + 900 = 2100
        expected_pnl = expected_market - expected_cost  # 2100 - 2000 = 100

        assert total_cost_basis == expected_cost
        assert total_market_value == expected_market
        assert total_pnl == expected_pnl


class TestCalculationEdgeCases:
    """Test edge cases in calculations"""

    def test_zero_shares_asset(self, test_db):
        """Test asset with zero shares"""
        asset = Asset(
            account_id=1,
            symbol="ZERO",
            shares=0,
            avg_cost=150.0,
            current_price=160.0
        )

        assert asset.market_value == 0
        assert asset.cost_basis == 0
        assert asset.unrealized_pnl == 0

    def test_very_large_numbers(self, test_db):
        """Test calculations with very large numbers"""
        asset = Asset(
            account_id=1,
            symbol="BIG",
            shares=1000000,
            avg_cost=1000.0,
            current_price=1100.0
        )

        expected_cost = 1000000 * 1000.0  # 1 billion
        expected_value = 1000000 * 1100.0  # 1.1 billion
        expected_pnl = expected_value - expected_cost  # 100 million

        assert asset.cost_basis == expected_cost
        assert asset.market_value == expected_value
        assert asset.unrealized_pnl == expected_pnl

    def test_very_small_numbers(self, test_db):
        """Test calculations with very small numbers"""
        asset = Asset(
            account_id=1,
            symbol="SMALL",
            shares=0.0001,
            avg_cost=0.01,
            current_price=0.02
        )

        expected_cost = 0.0001 * 0.01
        expected_value = 0.0001 * 0.02
        expected_pnl = expected_value - expected_cost

        assert abs(asset.cost_basis - expected_cost) < 1e-10
        assert abs(asset.market_value - expected_value) < 1e-10
        assert abs(asset.unrealized_pnl - expected_pnl) < 1e-10

    def test_negative_price_edge_case(self, test_db):
        """Test handling of negative prices (edge case)"""
        asset = Asset(
            account_id=1,
            symbol="NEGATIVE",
            shares=10,
            avg_cost=100.0,
            current_price=-10.0  # Unusual but test robustness
        )

        # System should handle this without crashing
        assert asset.market_value == -100.0
        assert asset.cost_basis == 1000.0
        assert asset.unrealized_pnl == -1100.0

    def test_percentage_calculation_precision(self, test_db):
        """Test percentage calculation precision"""
        asset = Asset(
            account_id=1,
            symbol="PRECISE",
            shares=3,
            avg_cost=100.0,
            current_price=133.33
        )

        # Should handle precision correctly
        pnl_percent = asset.unrealized_pnl_percent
        assert isinstance(pnl_percent, float)
        assert 33.0 < pnl_percent < 34.0  # Approximately 33.33%
        