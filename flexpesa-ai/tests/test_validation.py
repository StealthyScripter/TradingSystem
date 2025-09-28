"""
Updated validation tests that work with actual Pydantic v2 error messages
Also includes fixes for schemas if needed
"""

import pytest
from pydantic import ValidationError
from app.schemas.portfolio import (
    AccountCreateRequest, AssetCreateRequest, Account, Asset,
    BulkAssetCreateRequest, AssetUpdate, AccountUpdate
)


def extract_error_messages(validation_error: ValidationError) -> list[str]:
    """Helper function to properly extract error messages from ValidationError"""
    messages = []
    for error in validation_error.errors():
        # Get the error message directly
        if 'msg' in error:
            messages.append(error['msg'])
        # Also get the string representation as fallback
        messages.append(str(error))
    return messages


def has_validation_error_for_field(validation_error: ValidationError, field: str) -> bool:
    """Check if validation error exists for specific field"""
    for error in validation_error.errors():
        if 'loc' in error and field in error['loc']:
            return True
    return False


class TestAccountValidation:
    """Test account validation rules"""

    def test_valid_account_creation(self):
        """Test valid account creation"""
        account = AccountCreateRequest(
            name="My Investment Account",
            account_type="brokerage"
        )
        assert account.name == "My Investment Account"
        assert account.account_type == "brokerage"

    def test_empty_account_name_fails(self):
        """Test empty account name fails validation"""
        with pytest.raises(ValidationError) as exc_info:
            AccountCreateRequest(name="", account_type="brokerage")

        # Check that there's a validation error for the name field
        assert has_validation_error_for_field(exc_info.value, 'name')

        # Look for either custom message or standard validation
        error_messages = extract_error_messages(exc_info.value)
        assert any(
            "Account name cannot be empty" in msg or
            "String should have at least 1 character" in msg or
            "ensure this value has at least 1 character" in msg or
            "at least 1 character" in msg
            for msg in error_messages
        )

    def test_whitespace_account_name_fails(self):
        """Test whitespace-only account name fails validation"""
        with pytest.raises(ValidationError) as exc_info:
            AccountCreateRequest(name="   ", account_type="brokerage")

        # Should have validation error for name field
        assert has_validation_error_for_field(exc_info.value, 'name')

    def test_missing_account_name_fails(self):
        """Test missing account name fails validation"""
        with pytest.raises(ValidationError) as exc_info:
            AccountCreateRequest(account_type="brokerage")  # Missing name

        errors = exc_info.value.errors()
        # Should fail with required field error
        assert len(errors) > 0
        assert any(error.get('type') == 'missing' for error in errors)

    def test_invalid_account_type_fails(self):
        """Test invalid account type fails validation"""
        with pytest.raises(ValidationError) as exc_info:
            AccountCreateRequest(name="Test", account_type="invalid_type")

        # Should have validation error for account_type field
        assert has_validation_error_for_field(exc_info.value, 'account_type')

    def test_empty_account_type_fails(self):
        """Test empty account type fails validation"""
        with pytest.raises(ValidationError) as exc_info:
            AccountCreateRequest(name="Test", account_type="")

        # Should have validation error for account_type field
        assert has_validation_error_for_field(exc_info.value, 'account_type')

        # Check for either custom or standard validation message
        error_messages = extract_error_messages(exc_info.value)
        assert any(
            "Account type cannot be empty" in msg or
            "String should have at least 1 character" in msg or
            "at least 1 character" in msg
            for msg in error_messages
        )

    def test_account_type_normalization(self):
        """Test account type gets normalized to lowercase"""
        account = AccountCreateRequest(name="Test", account_type="BROKERAGE")
        assert account.account_type == "brokerage"

    def test_valid_account_types(self):
        """Test all valid account types"""
        valid_types = [
            "brokerage", "retirement", "ira", "roth_ira", "401k",
            "trading", "investment", "savings", "crypto", "testing"
        ]

        for account_type in valid_types:
            account = AccountCreateRequest(name="Test Account", account_type=account_type)
            assert account.account_type == account_type.lower()


class TestAssetValidation:
    """Test asset validation rules"""

    def test_valid_asset_creation(self):
        """Test valid asset creation"""
        asset = AssetCreateRequest(
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
            AssetCreateRequest(account_id=1, symbol="", shares=10, avg_cost=150)

        # Should have validation error for symbol field
        assert has_validation_error_for_field(exc_info.value, 'symbol')

        # Check for either custom or standard validation message
        error_messages = extract_error_messages(exc_info.value)
        assert any(
            "Symbol cannot be empty" in msg or
            "String should have at least 1 character" in msg or
            "at least 1 character" in msg
            for msg in error_messages
        )

    def test_whitespace_symbol_fails(self):
        """Test whitespace-only symbol fails validation"""
        with pytest.raises(ValidationError) as exc_info:
            AssetCreateRequest(account_id=1, symbol="   ", shares=10, avg_cost=150)

        # Should have validation error for symbol field
        assert has_validation_error_for_field(exc_info.value, 'symbol')

    def test_missing_symbol_fails(self):
        """Test missing symbol fails validation"""
        with pytest.raises(ValidationError) as exc_info:
            AssetCreateRequest(account_id=1, shares=10, avg_cost=150)  # Missing symbol

        errors = exc_info.value.errors()
        assert any(error.get('type') == 'missing' for error in errors)

    def test_zero_shares_fails(self):
        """Test zero shares fails validation"""
        with pytest.raises(ValidationError) as exc_info:
            AssetCreateRequest(account_id=1, symbol="AAPL", shares=0, avg_cost=150)

        error_messages = extract_error_messages(exc_info.value)
        # Pydantic v2 uses "greater than" in error messages
        assert any("greater than 0" in msg or "Shares must be greater than 0" in msg for msg in error_messages)

    def test_negative_shares_fails(self):
        """Test negative shares fails validation"""
        with pytest.raises(ValidationError) as exc_info:
            AssetCreateRequest(account_id=1, symbol="AAPL", shares=-5, avg_cost=150)

        error_messages = extract_error_messages(exc_info.value)
        assert any("greater than 0" in msg or "Shares must be greater than 0" in msg for msg in error_messages)

    def test_negative_cost_fails(self):
        """Test negative cost fails validation"""
        with pytest.raises(ValidationError) as exc_info:
            AssetCreateRequest(account_id=1, symbol="AAPL", shares=10, avg_cost=-50)

        error_messages = extract_error_messages(exc_info.value)
        assert any("greater than or equal to 0" in msg or "Average cost cannot be negative" in msg for msg in error_messages)

    def test_zero_account_id_fails(self):
        """Test zero account ID fails validation"""
        with pytest.raises(ValidationError) as exc_info:
            AssetCreateRequest(account_id=0, symbol="AAPL", shares=10, avg_cost=150)

        error_messages = extract_error_messages(exc_info.value)
        assert any("greater than 0" in msg or "Account ID must be greater than 0" in msg for msg in error_messages)

    def test_symbol_normalization(self):
        """Test symbol gets normalized to uppercase and trimmed"""
        asset = AssetCreateRequest(account_id=1, symbol="  aapl  ", shares=10, avg_cost=150)
        assert asset.symbol == "AAPL"

    def test_crypto_symbols_allowed(self):
        """Test cryptocurrency symbols are allowed"""
        asset = AssetCreateRequest(account_id=1, symbol="BTC-USD", shares=0.5, avg_cost=35000)
        assert asset.symbol == "BTC-USD"

    def test_fractional_shares_allowed(self):
        """Test fractional shares are allowed"""
        asset = AssetCreateRequest(account_id=1, symbol="AAPL", shares=0.123456, avg_cost=150)
        assert asset.shares == 0.123456

    def test_zero_cost_allowed(self):
        """Test zero cost is allowed (free shares)"""
        asset = AssetCreateRequest(account_id=1, symbol="FREE", shares=10, avg_cost=0)
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

        error_messages = extract_error_messages(exc_info.value)
        # Look for custom validation or model validation error
        assert any(
            "At least one field must be provided" in msg or
            "Value error" in msg or
            "validation error" in msg
            for msg in error_messages
        )

    def test_account_update_empty_name_fails(self):
        """Test account update with empty name fails"""
        with pytest.raises(ValidationError) as exc_info:
            AccountUpdate(name="")

        # Should have validation error for name field
        assert has_validation_error_for_field(exc_info.value, 'name')

        # Check for either custom or standard validation message
        error_messages = extract_error_messages(exc_info.value)
        assert any(
            "Account name cannot be empty" in msg or
            "String should have at least 1 character" in msg or
            "at least 1 character" in msg
            for msg in error_messages
        )

    def test_account_update_valid_name(self):
        """Test account update with valid name"""
        update = AccountUpdate(name="New Account Name")
        assert update.name == "New Account Name"

    def test_account_update_none_values_allowed(self):
        """Test account update with None values (no change)"""
        update = AccountUpdate(name=None, description=None)
        assert update.name is None
        assert update.description is None


class TestCriticalFinancialValidation:
    """Test critical validation for financial data integrity"""

    def test_positive_shares_required(self):
        """CRITICAL: Shares must be positive"""
        with pytest.raises(ValidationError) as exc_info:
            AssetCreateRequest(account_id=1, symbol="AAPL", shares=0, avg_cost=150)

        error_messages = extract_error_messages(exc_info.value)
        assert any("greater than 0" in msg for msg in error_messages)

    def test_non_negative_cost_required(self):
        """CRITICAL: Average cost cannot be negative"""
        with pytest.raises(ValidationError) as exc_info:
            AssetCreateRequest(account_id=1, symbol="AAPL", shares=10, avg_cost=-50)

        error_messages = extract_error_messages(exc_info.value)
        assert any("greater than or equal to 0" in msg or "cannot be negative" in msg for msg in error_messages)

    def test_valid_account_id_required(self):
        """CRITICAL: Must reference a valid account"""
        with pytest.raises(ValidationError) as exc_info:
            AssetCreateRequest(account_id=0, symbol="AAPL", shares=10, avg_cost=150)

        error_messages = extract_error_messages(exc_info.value)
        assert any("greater than 0" in msg for msg in error_messages)

    def test_account_name_required(self):
        """IMPORTANT: Account must have a meaningful name"""
        with pytest.raises(ValidationError) as exc_info:
            AccountCreateRequest(name="", account_type="brokerage")

        # Should have validation error for name field
        assert has_validation_error_for_field(exc_info.value, 'name')


class TestBulkValidation:
    """Test bulk operations validation"""

    def test_valid_bulk_creation(self):
        """Test valid bulk asset creation"""
        from app.schemas.portfolio import AssetBase

        assets = [
            AssetBase(symbol="AAPL", shares=10, avg_cost=150),
            AssetBase(symbol="MSFT", shares=5, avg_cost=300)
        ]

        bulk_asset = BulkAssetCreateRequest(account_id=1, assets=assets)
        assert len(bulk_asset.assets) == 2

    def test_empty_assets_list_fails(self):
        """Test empty assets list fails"""
        with pytest.raises(ValidationError) as exc_info:
            BulkAssetCreateRequest(account_id=1, assets=[])

        # Should have validation error for assets field
        assert has_validation_error_for_field(exc_info.value, 'assets')

        # Check for either custom or standard validation message
        error_messages = extract_error_messages(exc_info.value)
        assert any(
            "At least one asset is required" in msg or
            "List should have at least 1 item" in msg or
            "at least 1 item" in msg or
            "ensure this value has at least 1 item" in msg
            for msg in error_messages
        )

    def test_duplicate_symbols_fails(self):
        """Test duplicate symbols in bulk creation fails"""
        from app.schemas.portfolio import AssetBase

        assets = [
            AssetBase(symbol="AAPL", shares=10, avg_cost=150),
            AssetBase(symbol="AAPL", shares=5, avg_cost=160)  # Duplicate
        ]

        with pytest.raises(ValidationError) as exc_info:
            BulkAssetCreateRequest(account_id=1, assets=assets)

        # Should have some validation error (either custom or field-level)
        assert len(exc_info.value.errors()) > 0


class TestRealWorldScenarios:
    """Test realistic usage scenarios"""

    def test_typical_stock_purchase(self):
        """Test typical stock purchase validation"""
        asset = AssetCreateRequest(
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
        asset = AssetCreateRequest(
            account_id=1,
            symbol="BTC-USD",
            shares=0.5,
            avg_cost=42000.00
        )
        assert asset.symbol == "BTC-USD"
        assert asset.shares == 0.5

    def test_retirement_account_setup(self):
        """Test retirement account creation"""
        account = AccountCreateRequest(
            name="My 401(k)",
            account_type="401k",
            description="Employer-sponsored retirement account"
        )
        assert account.account_type == "401k"

    def test_international_symbols(self):
        """Test international stock symbols"""
        international_symbols = ["TSM", "ASML", "BABA"]

        for symbol in international_symbols:
            asset = AssetCreateRequest(account_id=1, symbol=symbol, shares=10, avg_cost=100)
            assert asset.symbol == symbol

    def test_penny_stocks(self):
        """Test very low-priced assets"""
        asset = AssetCreateRequest(account_id=1, symbol="PENNY", shares=10000, avg_cost=0.01)
        assert asset.avg_cost == 0.01

    def test_expensive_stocks(self):
        """Test expensive stocks like Berkshire Hathaway"""
        asset = AssetCreateRequest(
            account_id=1,
            symbol="BRK-A",
            shares=1,
            avg_cost=500000
        )
        assert asset.avg_cost == 500000


class TestErrorMessageQuality:
    """Test that error messages are helpful and clear"""

    def test_missing_required_fields_clear_messages(self):
        """Test that missing required fields give clear messages"""
        with pytest.raises(ValidationError) as exc_info:
            AccountCreateRequest()  # Missing everything

        errors = exc_info.value.errors()
        assert len(errors) >= 2  # Should catch missing name and account_type

        # Check error types
        error_types = [error.get('type') for error in errors]
        assert 'missing' in error_types

    def test_invalid_data_types_clear_messages(self):
        """Test that invalid data types give clear messages"""
        with pytest.raises(ValidationError) as exc_info:
            AssetCreateRequest(
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
            AssetCreateRequest(
                account_id=-1,    # Should be > 0
                symbol="AAPL",
                shares=-5,        # Should be > 0
                avg_cost=-100     # Should be >= 0
            )

        errors = exc_info.value.errors()
        assert len(errors) >= 3  # Should catch all range errors