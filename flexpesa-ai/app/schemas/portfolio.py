from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

class AssetBase(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10, description="Asset symbol (e.g., AAPL, BTC-USD)")
    shares: float = Field(..., gt=0, description="Number of shares (must be positive)")
    avg_cost: float = Field(..., ge=0, description="Average cost per share (must be non-negative)")

    @validator('symbol')
    def validate_symbol(cls, v):
        """Validate symbol format"""
        if not v or not v.strip():
            raise ValueError('Symbol cannot be empty')

        # Convert to uppercase and validate format
        symbol = v.strip().upper()

        # Basic symbol validation
        if not symbol.replace('-', '').replace('.', '').isalnum():
            raise ValueError('Symbol contains invalid characters')

        return symbol

    @validator('shares')
    def validate_shares(cls, v):
        """Validate share quantity"""
        if v <= 0:
            raise ValueError('Shares must be positive')
        if v > 1000000:  # Reasonable upper limit
            raise ValueError('Share quantity seems unreasonably high')
        return v

    @validator('avg_cost')
    def validate_avg_cost(cls, v):
        """Validate average cost"""
        if v < 0:
            raise ValueError('Average cost cannot be negative')
        if v > 100000:  # Reasonable upper limit for single share price
            raise ValueError('Average cost seems unreasonably high')
        return v

class AssetCreate(AssetBase):
    account_id: int = Field(..., gt=0, description="Account ID")

    @validator('account_id')
    def validate_account_id(cls, v):
        """Validate account ID"""
        if v <= 0:
            raise ValueError('Account ID must be positive')
        return v

class Asset(AssetBase):
    id: int
    account_id: int
    current_price: float
    last_updated: datetime

    class Config:
        from_attributes = True

class AccountBase(BaseModel):
    name: str
    account_type: str

class AccountCreate(AccountBase):
    pass

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

    @validator('risk_score')
    def validate_risk_score(cls,v):
        """Ensure risk score is between 0 and 10"""
        if not 0 <= v <= 10:
            raise ValueError('Risk score must be between 0 and 10')
        return v
