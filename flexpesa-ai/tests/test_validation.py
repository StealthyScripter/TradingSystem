"""
Updated validation tests with correct Pydantic v2 error patterns
"""

import pytest
from pydantic import ValidationError
from app.schemas.portfolio import (
    AccountCreate, AssetCreate, Account, Asset,
    BulkAssetCreate, AssetUpdate, AccountUpdate
)


class TestAccountValidation:
    """Test account validation rules"""

    def test_valid_account_creation(self):
        """Test valid account creation"""
        account = AccountCreate(
            name="My Investment Account",
            account_type="brokerage"
        )
        assert account.name == "My Investment Account"
        assert account.account_type == "brokerage"
        assert account.currency == "USD"  # Default value

    def test_empty_account_name_fails(self):
        """Test empty account name fails validation"""
        with pytest.raises(ValidationError) as exc_info:
            AccountCreate(name="", account_type="brokerage")

        # Check that validation error contains our custom message
        errors = exc_info.value.errors()
        error_messages = [str(error.get('msg', '')) + str(error) for error in errors]
        assert any("Account name cannot be empty" in msg for msg in error_messages)

        with pytest.raises(ValidationError) as exc_info:
            AccountCreate(name="   ", account_type="brokerage")

        errors = exc_info.value.errors()
        error_messages = [str(error.get('msg', '')) + str(error) for error in errors]
        assert any("Account name cannot be empty" in msg for msg in error_messages)

    def test_missing_account_name_fails(self):
        """Test missing account name fails validation"""
        with pytest.raises(ValidationError) as exc_info:
            AccountCreate(account_type="brokerage")  # Missing name

        errors = exc_info.value.errors()
        # Should fail with required field error
        assert len(errors) > 0
        assert any(error.get('type') == 'missing' for error in errors)

    def test_invalid_account_type_fails(self):
        """Test invalid account type fails validation"""
        with pytest.raises(ValidationError) as exc_info:
            AccountCreate(name="Test", account_type="invalid_type")

        errors = exc_info.value.errors()
        error_messages = [str(error.get('msg', '')) + str(error) for error in errors]
        assert any("Account type must be one of" in msg for msg in error_messages)

    def test_empty_account_type_fails(self):
        """Test empty account type fails validation"""
        with pytest.raises(ValidationError) as exc_info:
            AccountCreate(name="Test", account_type="")

        errors = exc_info.value.errors()
        error_messages = [str(error.get('msg', '')) + str(error) for error in errors]
        assert any("Account type cannot be empty" in msg for msg in error_messages)

    def test_account_type_normalization(self):
        """Test account type gets normalized to lowercase"""
        account = AccountCreate(name="Test", account_type="BROKERAGE")
        assert account.account_type == "brokerage"

    def test_valid_account_types(self):
        """Test all valid account types"""
        valid_types = [
            "brokerage", "retirement", "ira", "roth_ira", "401k",
            "trading", "investment", "savings", "crypto", "testing"
        ]

        for account_type in valid_types:
            account = AccountCreate(name="Test Account", account_type=account_type)
            assert account.account_type == account_type.lower()

    def test_currency_validation(self):
        """Test currency code validation"""
        # Valid 3-letter currency
        account = AccountCreate(name="Test", account_type="brokerage", currency="EUR")
        assert account.currency == "EUR"

        # Invalid currency length
        with pytest.raises(ValidationError):
            AccountCreate(name="Test", account_type="brokerage", currency="US")


class TestAssetValidation:
    """Test asset validation rules"""

    def test_valid_asset_creation(self):
        """Test valid asset creation"""
        asset = AssetCreate(
            account_id=1,
            symbol="AAPL",
            shares=10.5,
            avg_cost=150.25
        )
        assert asset.symbol == "AAPL"
        assert asset.shares == 10.5
        assert asset.avg_cost == 150.25

    def test_empty_symbol_fails(self):
        """Test empty symbol fails validation"""
        with pytest.raises(ValidationError) as exc_info:
            AssetCreate(account_id=1, symbol="", shares=10, avg_cost=150)

        errors = exc_info.value.errors()
        error_messages = [str(error.get('msg', '')) + str(error) for error in errors]
        assert any("Symbol cannot be empty" in msg for msg in error_messages)

    def test_whitespace_symbol_fails(self):
        """Test whitespace-only symbol fails validation"""
        with pytest.raises(ValidationError) as exc_info:
            AssetCreate(account_id=1, symbol="   ", shares=10, avg_cost=150)

        errors = exc_info.value.errors()
        error_messages = [str(error.get('msg', '')) + str(error) for error in errors]
        assert any("Symbol cannot be empty" in msg for msg in error_messages)

    def test_missing_symbol_fails(self):
        """Test missing symbol fails validation"""
        with pytest.raises(ValidationError) as exc_info:
            AssetCreate(account_id=1, shares=10, avg_cost=150)  # Missing symbol

        errors = exc_info.value.errors()
        assert any(error.get('type') == 'missing' for error in errors)

    def test_zero_shares_fails(self):
        """Test zero shares fails validation"""
        with pytest.raises(ValidationError) as exc_info:
            AssetCreate(account_id=1, symbol="AAPL", shares=0, avg_cost=150)

        errors = exc_info.value.errors()
        error_messages = [str(error.get('msg', '')) + str(error) for error in errors]
        # Pydantic v2 uses "greater than" in error messages
        assert any("greater than 0" in msg or "Shares must be greater than 0" in msg for msg in error_messages)

    def test_negative_shares_fails(self):
        """Test negative shares fails validation"""
        with pytest.raises(ValidationError) as exc_info:
            AssetCreate(account_id=1, symbol="AAPL", shares=-5, avg_cost=150)

        errors = exc_info.value.errors()
        error_messages = [str(error.get('msg', '')) + str(error) for error in errors]
        assert any("greater than 0" in msg or "Shares must be greater than 0" in msg for msg in error_messages)

    def test_negative_cost_fails(self):
        """Test negative cost fails validation"""
        with pytest.raises(ValidationError) as exc_info:
            AssetCreate(account_id=1, symbol="AAPL", shares=10, avg_cost=-50)

        errors = exc_info.value.errors()
        error_messages = [str(error.get('msg', '')) + str(error) for error in errors]
        assert any("greater than or equal to 0" in msg or "Average cost cannot be negative" in msg for msg in error_messages)

    def test_zero_account_id_fails(self):
        """Test zero account ID fails validation"""
        with pytest.raises(ValidationError) as exc_info:
            AssetCreate(account_id=0, symbol="AAPL", shares=10, avg_cost=150)

        errors = exc_info.value.errors()
        error_messages = [str(error.get('msg', '')) + str(error) for error in errors]
        assert any("greater than 0" in msg or "Account ID must be greater than 0" in msg for msg in error_messages)

    def test_symbol_normalization(self):
        """Test symbol gets normalized to uppercase and trimmed"""
        asset = AssetCreate(account_id=1, symbol="  aapl  ", shares=10, avg_cost=150)
        assert asset.symbol == "AAPL"

    def test_invalid_symbol_characters_fails(self):
        """Test invalid symbol characters fail validation"""
        with pytest.raises(ValidationError) as exc_info:
            AssetCreate(account_id=1, symbol="A@PL!", shares=10, avg_cost=150)

        errors = exc_info.value.errors()
        error_messages = [str(error.get('msg', '')) + str(error) for error in errors]
        assert any("Symbol contains invalid characters" in msg for msg in error_messages)

    def test_crypto_symbols_allowed(self):
        """Test cryptocurrency symbols are allowed"""
        asset = AssetCreate(account_id=1, symbol="BTC-USD", shares=0.5, avg_cost=35000)
        assert asset.symbol == "BTC-USD"

    def test_fractional_shares_allowed(self):
        """Test fractional shares are allowed"""
        asset = AssetCreate(account_id=1, symbol="AAPL", shares=0.123456, avg_cost=150)
        assert asset.shares == 0.123456

    def test_zero_cost_allowed(self):
        """Test zero cost is allowed (free shares)"""
        asset = AssetCreate(account_id=1, symbol="FREE", shares=10, avg_cost=0)
        assert asset.avg_cost == 0


class TestUpdateValidation:
    """Test update model validation"""

    def test_valid_asset_update(self):
        """Test valid asset update"""
        update = AssetUpdate(shares=15, avg_cost=160)
        assert update.shares == 15
        assert update.avg_cost == 160

    def test_empty_asset_update_fails(self):
        """Test empty asset update fails"""
        with pytest.raises(ValidationError) as exc_info:
            AssetUpdate()

        errors = exc_info.value.errors()
        error_messages = [str(error.get('msg', '')) + str(error) for error in errors]
        assert any("At least one field must be provided" in msg for msg in error_messages)

    def test_account_update_empty_name_fails(self):
        """Test account update with empty name fails"""
        with pytest.raises(ValidationError) as exc_info:
            AccountUpdate(name="")

        errors = exc_info.value.errors()
        error_messages = [str(error.get('msg', '')) + str(error) for error in errors]
        assert any("Account name cannot be empty" in msg for msg in error_messages)

    def test_account_update_whitespace_name_fails(self):
        """Test account update with whitespace-only name fails"""
        with pytest.raises(ValidationError) as exc_info:
            AccountUpdate(name="   ")

        errors = exc_info.value.errors()
        error_messages = [str(error.get('msg', '')) + str(error) for error in errors]
        assert any("Account name cannot be empty" in msg for msg in error_messages)

    def test_account_update_valid_name(self):
        """Test account update with valid name"""
        update = AccountUpdate(name="New Account Name")
        assert update.name == "New Account Name"

    def test_account_update_none_values_allowed(self):
        """Test account update with None values (no change)"""
        update = AccountUpdate(name=None, description=None)
        assert update.name is None
        assert update.description is None

    def test_asset_update_validation(self):
        """Test asset update field validation"""
        # Valid updates
        update = AssetUpdate(shares=20.5)
        assert update.shares == 20.5

        # Invalid shares
        with pytest.raises(ValidationError):
            AssetUpdate(shares=0)

        with pytest.raises(ValidationError):
            AssetUpdate(shares=-5)

        # Invalid avg_cost
        with pytest.raises(ValidationError):
            AssetUpdate(avg_cost=-10)

        # Invalid current_price
        with pytest.raises(ValidationError):
            AssetUpdate(current_price=-5)


class TestCriticalFinancialValidation:
    """Test critical validation for financial data integrity"""

    def test_positive_shares_required(self):
        """CRITICAL: Shares must be positive"""
        with pytest.raises(ValidationError) as exc_info:
            AssetCreate(account_id=1, symbol="AAPL", shares=0, avg_cost=150)

        errors = exc_info.value.errors()
        error_messages = [str(error.get('msg', '')) + str(error) for error in errors]
        assert any("greater than 0" in msg for msg in error_messages)

    def test_non_negative_cost_required(self):
        """CRITICAL: Average cost cannot be negative"""
        with pytest.raises(ValidationError) as exc_info:
            AssetCreate(account_id=1, symbol="AAPL", shares=10, avg_cost=-50)

        errors = exc_info.value.errors()
        error_messages = [str(error.get('msg', '')) + str(error) for error in errors]
        assert any("greater than or equal to 0" in msg or "cannot be negative" in msg for msg in error_messages)

    def test_valid_account_id_required(self):
        """CRITICAL: Must reference a valid account"""
        with pytest.raises(ValidationError) as exc_info:
            AssetCreate(account_id=0, symbol="AAPL", shares=10, avg_cost=150)

        errors = exc_info.value.errors()
        error_messages = [str(error.get('msg', '')) + str(error) for error in errors]
        assert any("greater than 0" in msg for msg in error_messages)

    def test_account_name_required(self):
        """IMPORTANT: Account must have a meaningful name"""
        with pytest.raises(ValidationError) as exc_info:
            AccountCreate(name="", account_type="brokerage")

        errors = exc_info.value.errors()
        error_messages = [str(error.get('msg', '')) + str(error) for error in errors]
        assert any("Account name cannot be empty" in msg for msg in error_messages)

    def test_symbol_format_validation(self):
        """IMPORTANT: Symbol format must be valid"""
        # Valid symbols should work
        valid_symbols = ["AAPL", "BTC-USD", "MSFT", "SPY"]
        for symbol in valid_symbols:
            asset = AssetCreate(account_id=1, symbol=symbol, shares=10, avg_cost=150)
            assert asset.symbol == symbol.upper()

        # Invalid symbols should fail
        with pytest.raises(ValidationError) as exc_info:
            AssetCreate(account_id=1, symbol="A@PL!", shares=10, avg_cost=150)

        errors = exc_info.value.errors()
        error_messages = [str(error.get('msg', '')) + str(error) for error in errors]
        assert any("invalid characters" in msg for msg in error_messages)


class TestBulkValidation:
    """Test bulk operations validation"""

    def test_valid_bulk_creation(self):
        """Test valid bulk asset creation"""
        from app.schemas.portfolio import AssetBase

        assets = [
            AssetBase(symbol="AAPL", shares=10, avg_cost=150),
            AssetBase(symbol="MSFT", shares=5, avg_cost=300)
        ]

        bulk_asset = BulkAssetCreate(account_id=1, assets=assets)
        assert len(bulk_asset.assets) == 2

    def test_duplicate_symbols_fails(self):
        """Test duplicate symbols in bulk creation fails"""
        from app.schemas.portfolio import AssetBase

        assets = [
            AssetBase(symbol="AAPL", shares=10, avg_cost=150),
            AssetBase(symbol="AAPL", shares=5, avg_cost=160)  # Duplicate
        ]

        with pytest.raises(ValidationError) as exc_info:
            BulkAssetCreate(account_id=1, assets=assets)

        errors = exc_info.value.errors()
        error_messages = [str(error.get('msg', '')) + str(error) for error in errors]
        assert any("Duplicate symbols" in msg for msg in error_messages)

    def test_empty_assets_list_fails(self):
        """Test empty assets list fails"""
        with pytest.raises(ValidationError) as exc_info:
            BulkAssetCreate(account_id=1, assets=[])

        errors = exc_info.value.errors()
        error_messages = [str(error.get('msg', '')) + str(error) for error in errors]
        assert any("At least one asset is required" in msg for msg in error_messages)


class TestRealWorldScenarios:
    """Test realistic usage scenarios"""

    def test_typical_stock_purchase(self):
        """Test typical stock purchase validation"""
        asset = AssetCreate(
            account_id=1,
            symbol="AAPL",
            shares=100,
            avg_cost=150.50
        )
        assert asset.symbol == "AAPL"
        assert asset.shares == 100
        assert asset.avg_cost == 150.50

    def test_crypto_purchase(self):
        """Test cryptocurrency purchase validation"""
        asset = AssetCreate(
            account_id=1,
            symbol="BTC-USD",
            shares=0.5,
            avg_cost=42000.00
        )
        assert asset.symbol == "BTC-USD"
        assert asset.shares == 0.5

    def test_retirement_account_setup(self):
        """Test retirement account creation"""
        account = AccountCreate(
            name="My 401(k)",
            account_type="401k",
            description="Employer-sponsored retirement account"
        )
        assert account.account_type == "401k"

    def test_international_symbols(self):
        """Test international stock symbols"""
        international_symbols = ["TSM", "ASML", "BABA"]

        for symbol in international_symbols:
            asset = AssetCreate(account_id=1, symbol=symbol, shares=10, avg_cost=100)
            assert asset.symbol == symbol

    def test_penny_stocks(self):
        """Test very low-priced assets"""
        asset = AssetCreate(account_id=1, symbol="PENNY", shares=10000, avg_cost=0.01)
        assert asset.avg_cost == 0.01

    def test_expensive_stocks(self):
        """Test expensive stocks like Berkshire Hathaway"""
        asset = AssetCreate(
            account_id=1,
            symbol="BRK-A",
            shares=1,
            avg_cost=500000
        )
        assert asset.avg_cost == 500000

    def test_edge_case_inputs(self):
        """Test various edge case inputs"""
        # Very long but valid symbol
        asset = AssetCreate(account_id=1, symbol="VERYLONGSYM", shares=1, avg_cost=1)
        assert asset.symbol == "VERYLONGSYM"

        # Very small fractional shares
        asset = AssetCreate(account_id=1, symbol="FRAC", shares=0.000001, avg_cost=1000000)
        assert asset.shares == 0.000001


class TestErrorMessageQuality:
    """Test that error messages are helpful and clear"""

    def test_missing_required_fields_clear_messages(self):
        """Test that missing required fields give clear messages"""
        with pytest.raises(ValidationError) as exc_info:
            AccountCreate()  # Missing everything

        errors = exc_info.value.errors()
        assert len(errors) >= 2  # Should catch missing name and account_type

        # Check error types
        error_types = [error.get('type') for error in errors]
        assert 'missing' in error_types

    def test_invalid_data_types_clear_messages(self):
        """Test that invalid data types give clear messages"""
        with pytest.raises(ValidationError) as exc_info:
            AssetCreate(
                account_id="not_a_number",  # Should be int
                symbol="AAPL",
                shares="not_a_number",     # Should be float
                avg_cost="not_a_number"    # Should be float
            )

        errors = exc_info.value.errors()
        assert len(errors) >= 3  # Should catch all type errors

    def test_out_of_range_values_clear_messages(self):
        """Test that out-of-range values give clear messages"""
        with pytest.raises(ValidationError) as exc_info:
            AssetCreate(
                account_id=-1,    # Should be > 0
                symbol="AAPL",
                shares=-5,        # Should be > 0
                avg_cost=-100     # Should be >= 0
            )

        errors = exc_info.value.errors()
        assert len(errors) >= 3  # Should catch all range errors