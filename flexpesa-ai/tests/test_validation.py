import pytest
from pydantic import ValidationError

class TestAssetValidation:

    def test_valid_account_creation(self):
        """Test valid account creation"""
        account = AccountCreate(
            name="My Investment Account",
            account_type="brokerage"
        )
        assert account.name == "My Investment Account"
        assert account.account_type == "brokerage"

    def test_empty_account_name_fails(self):
        """Test empty account name fails"""
        with pytest.raises(ValidationError, match="Account name cannot be empty"):
            AccountCreate(name="", account_type="brokerage")

        with pytest.raises(ValidationError, match="Account name cannot be empty"):
            AccountCreate(name="   ", account_type="brokerage")

    def test_invalid_account_type_fails(self):
        """Test invalid account type fails"""
        with pytest.raises(ValidationError, match="Account type must be one of"):
            AccountCreate(name="Test", account_type="invalid_type")

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
        """Test empty symbol fails"""
        with pytest.raises(ValidationError, match="Symbol cannot be empty"):
            AssetCreate(account_id=1, symbol="", shares=10, avg_cost=150)

        with pytest.raises(ValidationError, match="Symbol cannot be empty"):
            AssetCreate(account_id=1, symbol="   ", shares=10, avg_cost=150)

    def test_negative_shares_fails(self):
        """Test negative shares fails"""
        with pytest.raises(ValidationError, match="Shares must be greater than 0"):
            AssetCreate(account_id=1, symbol="AAPL", shares=-5, avg_cost=150)

        with pytest.raises(ValidationError, match="Shares must be greater than 0"):
            AssetCreate(account_id=1, symbol="AAPL", shares=0, avg_cost=150)

    def test_negative_cost_fails(self):
        """Test negative cost fails"""
        with pytest.raises(ValidationError, match="Average cost cannot be negative"):
            AssetCreate(account_id=1, symbol="AAPL", shares=10, avg_cost=-50)

    def test_invalid_symbol_characters_fails(self):
        """Test invalid symbol characters fail"""
        with pytest.raises(ValidationError, match="Symbol contains invalid characters"):
            AssetCreate(account_id=1, symbol="A@PL!", shares=10, avg_cost=150)

    def test_symbol_normalization(self):
        """Test symbol gets normalized to uppercase"""
        asset = AssetCreate(account_id=1, symbol="  aapl  ", shares=10, avg_cost=150)
        assert asset.symbol == "AAPL"

    def test_account_type_normalization(self):
        """Test account type gets normalized to lowercase"""
        account = AccountCreate(name="Test", account_type="BROKERAGE")
        assert account.account_type == "brokerage"

    def test_valid_asset_creation(self):
        """Test creating valid asset"""
        asset = AssetCreate(
            account_id=1,
            symbol="AAPL",
            shares=10.5,
            avg_cost=150.25
        )
        assert asset.symbol == "AAPL"
        assert asset.shares == 10.5

    def test_invalid_symbol_validation(self):
        """Test symbol validation"""
        with pytest.raises(ValidationError, match="Symbol cannot be empty"):
            AssetCreate(
                account_id=1,
                symbol="",
                shares=10,
                avg_cost=150
            )

    def test_negative_shares_validation(self):
        """Test negative shares validation"""
        with pytest.raises(ValidationError, match="Shares must be positive"):
            AssetCreate(
                account_id=1,
                symbol="AAPL",
                shares=-5,
                avg_cost=150
            )

    def test_negative_cost_validation(self):
        """Test negative cost validation"""
        with pytest.raises(ValidationError, match="Average cost cannot be negative"):
            AssetCreate(
                account_id=1,
                symbol="AAPL",
                shares=10,
                avg_cost=-50
            )

    @pytest.mark.asyncio
    async def test_service_level_validation(self, test_db, sample_account):
        """Test service-level validation"""
        service = PortfolioService(test_db)

        # Test invalid account
        with pytest.raises(ValueError, match="Account not found"):
            await service.add_asset(AssetCreate(
                account_id=99999,
                symbol="AAPL",
                shares=10,
                avg_cost=150
            ))
