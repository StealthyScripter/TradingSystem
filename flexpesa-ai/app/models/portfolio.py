from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Index
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import uuid

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)

    # Clerk user ID - string format used by Clerk
    clerk_user_id = Column(String(255), index=True, nullable=True)

    name = Column(String(255), index=True, nullable=False)  # "Wells Fargo", "Stack Well", etc.
    account_type = Column(String(100), nullable=False)      # "brokerage", "retirement", etc.
    balance = Column(Float, default=0.0)

    # Additional account metadata
    description = Column(Text, nullable=True)
    currency = Column(String(3), default="USD")  # ISO currency code
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assets = relationship("Asset", back_populates="account", cascade="all, delete-orphan")

    # Indexes for better query performance
    __table_args__ = (
        Index('idx_account_user_active', 'clerk_user_id', 'is_active'),
        Index('idx_account_type', 'account_type'),
    )

    def __repr__(self):
        return f"<Account(id={self.id}, name='{self.name}', type='{self.account_type}')>"

    @property
    def total_value(self):
        """Calculate total account value from assets"""
        return sum(
            (asset.shares * (asset.current_price or asset.avg_cost)) for asset in self.assets if asset.is_active)

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "clerk_user_id": self.clerk_user_id,
            "name": self.name,
            "account_type": self.account_type,
            "balance": self.balance,
            "description": self.description,
            "currency": self.currency,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "total_value": self.total_value,
            "asset_count": len(self.assets)
        }

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)

    # Asset details
    symbol = Column(String(20), index=True, nullable=False)     # "AAPL", "BTC-USD", etc.
    name = Column(String(255), nullable=True)                   # Full company/asset name
    asset_type = Column(String(50), nullable=True)             # "stock", "crypto", "etf", etc.

    # Position details
    shares = Column(Float, nullable=False)
    avg_cost = Column(Float, nullable=False)
    current_price = Column(Float, default=0.0)

    # Market data
    market_cap = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    day_change = Column(Float, default=0.0)
    day_change_percent = Column(Float, default=0.0)

    # Additional metadata
    currency = Column(String(3), default="USD")
    exchange = Column(String(10), nullable=True)  # NYSE, NASDAQ, etc.
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    price_updated_at = Column(DateTime, nullable=True)

    # Relationships
    account = relationship("Account", back_populates="assets")

    # Indexes for better query performance
    __table_args__ = (
        Index('idx_asset_symbol', 'symbol'),
        Index('idx_asset_account_symbol', 'account_id', 'symbol'),
        Index('idx_asset_account_active', 'account_id', 'is_active'),
        Index('idx_asset_type', 'asset_type'),
    )

    def __repr__(self):
        return f"<Asset(id={self.id}, symbol='{self.symbol}', shares={self.shares})>"

    @property
    def market_value(self):
        """Current market value of the position"""
        return self.shares * (self.current_price or self.avg_cost)

    @property
    def cost_basis(self):
        """Total cost basis of the position"""
        return self.shares * self.avg_cost

    @property
    def unrealized_pnl(self):
        """Unrealized profit/loss"""
        return self.market_value - self.cost_basis

    @property
    def unrealized_pnl_percent(self):
        """Unrealized profit/loss percentage"""
        if self.cost_basis == 0:
            return 0.0
        return (self.unrealized_pnl / self.cost_basis) * 100

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "account_id": self.account_id,
            "symbol": self.symbol,
            "name": self.name,
            "asset_type": self.asset_type,
            "shares": self.shares,
            "avg_cost": self.avg_cost,
            "current_price": self.current_price,
            "market_value": self.market_value,
            "cost_basis": self.cost_basis,
            "unrealized_pnl": self.unrealized_pnl,
            "unrealized_pnl_percent": self.unrealized_pnl_percent,
            "market_cap": self.market_cap,
            "volume": self.volume,
            "day_change": self.day_change,
            "day_change_percent": self.day_change_percent,
            "currency": self.currency,
            "exchange": self.exchange,
            "sector": self.sector,
            "industry": self.industry,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "price_updated_at": self.price_updated_at.isoformat() if self.price_updated_at else None
        }

class PortfolioSnapshot(Base):
    """Table to store historical portfolio snapshots for performance tracking"""
    __tablename__ = "portfolio_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    clerk_user_id = Column(String(255), index=True, nullable=False)

    # Snapshot data
    total_value = Column(Float, nullable=False)
    total_cost_basis = Column(Float, nullable=False)
    total_pnl = Column(Float, nullable=False)
    total_pnl_percent = Column(Float, nullable=False)

    # Asset breakdown
    asset_count = Column(Integer, nullable=False)
    account_count = Column(Integer, nullable=False)

    # Snapshot metadata
    snapshot_type = Column(String(20), default="daily")  # daily, weekly, monthly
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Indexes
    __table_args__ = (
        Index('idx_snapshot_user_date', 'clerk_user_id', 'created_at'),
        Index('idx_snapshot_type', 'snapshot_type'),
    )

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "clerk_user_id": self.clerk_user_id,
            "total_value": self.total_value,
            "total_cost_basis": self.total_cost_basis,
            "total_pnl": self.total_pnl,
            "total_pnl_percent": self.total_pnl_percent,
            "asset_count": self.asset_count,
            "account_count": self.account_count,
            "snapshot_type": self.snapshot_type,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class MarketData(Base):
    """Table to cache market data to reduce API calls"""
    __tablename__ = "market_data_cache"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, index=True, nullable=False)

    # Price data
    current_price = Column(Float, nullable=False)
    open_price = Column(Float, nullable=True)
    high_price = Column(Float, nullable=True)
    low_price = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)

    # Change data
    day_change = Column(Float, default=0.0)
    day_change_percent = Column(Float, default=0.0)

    # Company/Asset info
    name = Column(String(255), nullable=True)
    market_cap = Column(Float, nullable=True)
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)

    # Metadata
    currency = Column(String(3), default="USD")
    exchange = Column(String(10), nullable=True)
    asset_type = Column(String(50), nullable=True)

    # Cache timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index('idx_market_data_updated', 'updated_at'),
        Index('idx_market_data_type', 'asset_type'),
    )

    @property
    def is_stale(self, max_age_minutes: int = 5) -> bool:
        """Check if market data is stale"""
        if not self.updated_at:
            return True

        age = datetime.utcnow() - self.updated_at
        return age.total_seconds() > (max_age_minutes * 60)

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "symbol": self.symbol,
            "name": self.name,
            "current_price": self.current_price,
            "open_price": self.open_price,
            "high_price": self.high_price,
            "low_price": self.low_price,
            "volume": self.volume,
            "day_change": self.day_change,
            "day_change_percent": self.day_change_percent,
            "market_cap": self.market_cap,
            "sector": self.sector,
            "industry": self.industry,
            "currency": self.currency,
            "exchange": self.exchange,
            "asset_type": self.asset_type,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
