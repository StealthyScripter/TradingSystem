from sqlalchemy.orm import Session
from app.models.portfolio import Account, Asset
from app.schemas.portfolio import AccountCreate, AssetCreate
from .market_data import MarketDataService
from .simple_ai import SimpleAIService
from typing import List, Dict
import logging

class PortfolioService:
    """Core portfolio management service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.market_data = MarketDataService()
        self.ai_service = SimpleAIService()
    
    def create_account(self, account: AccountCreate) -> Account:
        """Create new investment account"""
        db_account = Account(**account.dict())
        self.db.add(db_account)
        self.db.commit()
        self.db.refresh(db_account)
        return db_account
    
    def add_asset(self, asset: AssetCreate) -> Asset:
        """Add asset to account"""
        db_asset = Asset(**asset.dict())
        self.db.add(db_asset)
        self.db.commit()
        self.db.refresh(db_asset)
        return db_asset
    
    def update_prices(self) -> Dict:
        """Update current prices for all assets"""
        assets = self.db.query(Asset).all()
        symbols = list(set(asset.symbol for asset in assets))
        
        current_prices = self.market_data.get_current_prices(symbols)
        
        updated_count = 0
        for asset in assets:
            if asset.symbol in current_prices:
                asset.current_price = current_prices[asset.symbol]
                updated_count += 1
        
        self.db.commit()
        return {"updated_assets": updated_count, "total_assets": len(assets)}
    
    def get_portfolio_summary(self) -> Dict:
        """Get complete portfolio summary"""
        accounts = self.db.query(Account).all()
        
        portfolio_data = []
        total_value = 0
        
        for account in accounts:
            account_value = sum(asset.shares * asset.current_price for asset in account.assets)
            account.balance = account_value  # Update balance
            
            portfolio_data.append({
                "id": account.id,
                "name": account.name,
                "balance": account_value,
                "assets": [
                    {
                        "symbol": asset.symbol,
                        "shares": asset.shares,
                        "current_price": asset.current_price,
                        "value": asset.shares * asset.current_price
                    }
                    for asset in account.assets
                ]
            })
            total_value += account_value
        
        # Get AI analysis
        ai_analysis = self.ai_service.analyze_portfolio(portfolio_data)
        
        return {
            "accounts": portfolio_data,
            "total_value": total_value,
            "analysis": ai_analysis
        }
