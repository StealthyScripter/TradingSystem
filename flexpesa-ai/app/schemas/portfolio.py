from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AssetBase(BaseModel):
    symbol: str
    shares: float
    avg_cost: float

class AssetCreate(AssetBase):
    account_id: int

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
