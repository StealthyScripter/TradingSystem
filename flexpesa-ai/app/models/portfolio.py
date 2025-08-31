from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"),nullable=False)
    name = Column(String, index=True)  # "Wells Fargo", "Stack Well", etc.
    account_type = Column(String)      # "brokerage", "retirement", etc.
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="accounts")
    assets = relationship("Asset", back_populates="account")

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    symbol = Column(String, index=True)     # "AAPL", "BTC-USD", etc.
    shares = Column(Float)
    avg_cost = Column(Float)
    current_price = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow)

    account = relationship("Account", back_populates="assets")
