from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Any
from datetime import datetime
import re

class AssetBase(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=20, description="Asset symbol (e.g., AAPL, BTC-USD)")
    shares: float = Field(..., gt=0, description="Number of shares (must be positive)")
    avg_cost: float = Field(..., ge=0, description="Average cost per share (cannot be negative)")

    @field_validator('symbol')
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        if v is None:
            raise ValueError("Symbol is required")

        # Strip whitespace first
        symbol = str(v).strip()

        # Check for empty after stripping
        if not symbol:
            raise ValueError("Symbol cannot be empty")

        # Remove whitespace and convert to uppercase
        symbol = symbol.upper()

        # Check for valid characters (letters, numbers, and hyphens for crypto)
        if not re.match(r'^[A-Z0-9\-\.]+$', symbol):
            raise ValueError("Symbol contains invalid characters")

        return symbol

    @field_validator('shares')
    @classmethod
    def validate_shares(cls, v: float) -> float:
        if v is None:
            raise ValueError("Shares is required")

        if v <= 0:
            raise ValueError("Shares must be greater than 0")
        return v

    @field_validator('avg_cost')
    @classmethod
    def validate_avg_cost(cls, v: float) -> float:
        if v is None:
            raise ValueError("Average cost is required")
        if v < 0:
            raise ValueError("Average cost cannot be negative")
        return v

class AssetCreateRequest(AssetBase):
    account_id: int = Field(..., gt=0, description="Account ID this asset belongs to")

    @field_validator('account_id')
    @classmethod
    def validate_account_id(cls, v: int) -> int:
        if v is None:
            raise ValueError("Account ID is required")
        if v <= 0:
            raise ValueError("Account ID must be greater than 0")
        return v

class Asset(AssetBase):
    id: int
    account_id: int
    current_price: float
    last_updated: datetime

    class Config:
        from_attributes = True

class AccountBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Account name")
    account_type: str = Field(..., min_length=1, max_length=100, description="Account type")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if v is None:
            raise ValueError("Account name is required")

        name = str(v).strip()

        if not name:
            raise ValueError("Account name cannot be empty")
        return name

    @field_validator('account_type')
    @classmethod
    def validate_account_type(cls, v: str) -> str:
        # Handle None explicitly
        if v is None:
            raise ValueError("Account type is required")

        # Convert to string and strip
        account_type = str(v).strip()

        # Check for empty after stripping
        if not account_type:
            raise ValueError("Account type cannot be empty")

        # Normalize to lowercase
        account_type = account_type.lower()

        # Valid account types
        valid_types = {
            'brokerage', 'retirement', 'ira', 'roth_ira', '401k',
            'trading', 'investment', 'savings', 'crypto', 'testing'
        }

        if account_type not in valid_types:
            raise ValueError(f"Account type must be one of: {', '.join(sorted(valid_types))}")

        return account_type

class AccountCreateRequest(AccountBase):
    description: Optional[str] = Field(None, max_length=1000, description="Optional account description")
    currency: Optional[str] = Field("USD", min_length=3, max_length=3, description="Currency code")

    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v: Optional[str]) -> str:
        if v:
            currency = str(v).strip().upper()
            if len(currency) != 3:
                raise ValueError("Currency code must be exactly 3 characters")
            return currency
        return "USD"

class Account(AccountBase):
    id: int
    balance: float
    created_at: datetime
    assets: List[Asset] = []

    class Config:
        from_attributes = True

class PortfolioAnalysis(BaseModel):
    total_value: float
    day_change: float
    day_change_percent: float
    recommendation: str
    confidence: float
    risk_score: float

# Additional validation models for more complex operations
class BulkAssetCreateRequest(BaseModel):
    """For creating multiple assets at once"""
    account_id: int = Field(..., gt=0)
    assets: List[AssetBase] = Field(..., min_length=1, max_length=50)

    @field_validator('assets')
    @classmethod
    def validate_unique_symbols(cls, v: List[AssetBase]) -> List[AssetBase]:
        if not v:
            raise ValueError("At least one asset is required")

        symbols = [asset.symbol.upper() for asset in v]
        if len(symbols) != len(set(symbols)):
            raise ValueError("Duplicate symbols are not allowed in bulk creation")
        return v

class AssetUpdate(BaseModel):
    """For updating existing assets"""
    shares: Optional[float] = Field(None, gt=0)
    avg_cost: Optional[float] = Field(None, ge=0)
    current_price: Optional[float] = Field(None, ge=0)

    @field_validator('shares')
    @classmethod
    def validate_shares(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("Shares must be greater than 0")
        return v

    @field_validator('avg_cost')
    @classmethod
    def validate_avg_cost(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("Average cost cannot be negative")
        return v

    @field_validator('current_price')
    @classmethod
    def validate_current_price(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("Current price cannot be negative")
        return v

    @model_validator(mode='after')
    def validate_at_least_one_field(self) -> 'AssetUpdate':
        if not any([self.shares, self.avg_cost, self.current_price]):
            raise ValueError("At least one field must be provided for update")
        return self

class AccountUpdate(BaseModel):
    """For updating existing accounts"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            # Convert to string and strip
            name = str(v).strip()
            # Check for empty after stripping
            if not name:
                raise ValueError("Account name cannot be empty")
            return name
        return v

# Response models with additional computed fields
class AssetResponse(Asset):
    """Enhanced asset response with calculated fields"""
    market_value: float = Field(..., description="Current market value (shares * current_price)")
    cost_basis: float = Field(..., description="Total cost basis (shares * avg_cost)")
    unrealized_pnl: float = Field(..., description="Unrealized profit/loss")
    unrealized_pnl_percent: float = Field(..., description="Unrealized P&L percentage")

class AccountResponse(Account):
    """Enhanced account response with calculated fields"""
    total_value: float = Field(..., description="Total account value from all assets")
    asset_count: int = Field(..., description="Number of assets in account")

class PortfolioSummaryResponse(BaseModel):
    """Complete portfolio summary response"""
    user_id: str
    accounts: List[AccountResponse]
    summary: dict
    analysis: PortfolioAnalysis
    last_updated: str
    status: str = "success"

# Validation for financial edge cases
class StockSplitData(BaseModel):
    """For handling stock splits"""
    symbol: str = Field(..., min_length=1, max_length=20)
    split_ratio: float = Field(..., gt=0, description="Split ratio (e.g., 2.0 for 2:1 split)")
    split_date: datetime

    @field_validator('symbol')
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Symbol cannot be empty")
        return v.strip().upper()

    @field_validator('split_ratio')
    @classmethod
    def validate_split_ratio(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Split ratio must be positive")
        # Common split ratios: 2:1, 3:1, 3:2, etc.
        if v > 10:
            raise ValueError("Split ratio seems unusually high")
        return v

class DividendData(BaseModel):
    """For handling dividend payments"""
    symbol: str = Field(..., min_length=1, max_length=20)
    dividend_per_share: float = Field(..., ge=0, description="Dividend amount per share")
    ex_dividend_date: datetime
    payment_date: datetime

    @field_validator('symbol')
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Symbol cannot be empty")
        return v.strip().upper()

    @model_validator(mode='after')
    def validate_dates(self) -> 'DividendData':
        if self.payment_date < self.ex_dividend_date:
            raise ValueError("Payment date cannot be before ex-dividend date")
        return self

class MarketOrderData(BaseModel):
    """For market orders validation"""
    symbol: str = Field(..., min_length=1, max_length=20)
    order_type: str = Field(..., description="buy, sell, buy_to_cover, sell_short")
    quantity: float = Field(..., gt=0, description="Number of shares")
    order_price: Optional[float] = Field(None, ge=0, description="Limit price (None for market order)")

    @field_validator('symbol')
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Symbol cannot be empty")

        symbol = v.strip().upper()
        if not re.match(r'^[A-Z0-9\-]+$', symbol):
            raise ValueError("Symbol contains invalid characters")
        return symbol

    @field_validator('order_type')
    @classmethod
    def validate_order_type(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Order type cannot be empty")

        valid_types = {'buy', 'sell', 'buy_to_cover', 'sell_short'}
        order_type = v.lower().strip()
        if order_type not in valid_types:
            raise ValueError(f"Order type must be one of: {', '.join(valid_types)}")
        return order_type

# Advanced portfolio analytics models
class PortfolioMetrics(BaseModel):
    """Advanced portfolio performance metrics"""
    sharpe_ratio: Optional[float] = Field(None, description="Risk-adjusted return")
    beta: Optional[float] = Field(None, description="Market correlation")
    alpha: Optional[float] = Field(None, description="Excess return")
    max_drawdown: Optional[float] = Field(None, ge=0, le=100, description="Maximum drawdown percentage")
    volatility: Optional[float] = Field(None, ge=0, description="Portfolio volatility")

    @field_validator('max_drawdown')
    @classmethod
    def validate_max_drawdown(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Max drawdown must be between 0 and 100 percent")
        return v

class RiskAssessment(BaseModel):
    """Portfolio risk assessment"""
    risk_level: str = Field(..., description="conservative, moderate, aggressive")
    concentration_risk: float = Field(..., ge=0, le=100, description="Concentration risk percentage")
    sector_exposure: dict = Field(default_factory=dict, description="Sector allocation percentages")

    @field_validator('risk_level')
    @classmethod
    def validate_risk_level(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Risk level cannot be empty")

        valid_levels = {'conservative', 'moderate', 'aggressive'}
        risk_level = v.lower().strip()
        if risk_level not in valid_levels:
            raise ValueError(f"Risk level must be one of: {', '.join(valid_levels)}")
        return risk_level

    @model_validator(mode='after')
    def validate_sector_exposure(self) -> 'RiskAssessment':
        if self.sector_exposure:
            total_exposure = sum(self.sector_exposure.values())
            if abs(total_exposure - 100.0) > 0.01:  # Allow for minor rounding differences
                raise ValueError("Sector exposure percentages must sum to 100%")
        return self

# Tax-related models
class TaxLotData(BaseModel):
    """For tax lot tracking"""
    symbol: str = Field(..., min_length=1, max_length=20)
    purchase_date: datetime
    quantity: float = Field(..., gt=0)
    cost_basis: float = Field(..., ge=0)
    holding_period: str = Field(..., description="short_term or long_term")

    @field_validator('symbol')
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Symbol cannot be empty")
        return v.strip().upper()

    @field_validator('holding_period')
    @classmethod
    def validate_holding_period(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Holding period cannot be empty")

        valid_periods = {'short_term', 'long_term'}
        period = v.lower().strip()
        if period not in valid_periods:
            raise ValueError("Holding period must be 'short_term' or 'long_term'")
        return period

# International trading models
class CurrencyConversion(BaseModel):
    """For international assets"""
    base_currency: str = Field(..., min_length=3, max_length=3, description="Base currency code")
    target_currency: str = Field(..., min_length=3, max_length=3, description="Target currency code")
    exchange_rate: float = Field(..., gt=0, description="Exchange rate")
    conversion_date: datetime

    @field_validator('base_currency', 'target_currency')
    @classmethod
    def validate_currency_codes(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Currency code cannot be empty")

        currency = v.upper().strip()
        if len(currency) != 3:
            raise ValueError("Currency code must be exactly 3 characters")
        if not currency.isalpha():
            raise ValueError("Currency code must contain only letters")
        return currency

    @model_validator(mode='after')
    def validate_different_currencies(self) -> 'CurrencyConversion':
        if self.base_currency == self.target_currency:
            raise ValueError("Base and target currencies must be different")
        return self