from sqlalchemy.orm import Session
from typing import List, Dict
import logging
from datetime import datetime

# Fix imports
from app.models.portfolio import Account, Asset
from app.schemas.portfolio import AccountCreate, AssetCreate
from app.services.market_data import MarketDataService
from app.services.simple_ai import SimpleAIService

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
        
        print(f"🔄 Updating prices for {len(symbols)} symbols...")
        current_prices = self.market_data.get_current_prices(symbols)
        
        updated_count = 0
        for asset in assets:
            if asset.symbol in current_prices and current_prices[asset.symbol] > 0:
                asset.current_price = current_prices[asset.symbol]
                asset.last_updated = datetime.utcnow()
                updated_count += 1
                print(f"   ✅ {asset.symbol}: ${asset.current_price:,.2f}")
        
        self.db.commit()
        print(f"📊 Updated {updated_count}/{len(assets)} assets")
        return {"updated_assets": updated_count, "total_assets": len(assets)}
    
    def get_portfolio_summary(self) -> Dict:
        """Get complete portfolio summary with full asset data"""
        accounts = self.db.query(Account).all()
        
        portfolio_data = []
        total_value = 0
        
        for account in accounts:
            # Calculate account value and update balance
            account_value = sum(asset.shares * asset.current_price for asset in account.assets)
            account.balance = account_value
            
            # Build complete asset data for frontend
            asset_data = []
            for asset in account.assets:
                current_value = asset.shares * asset.current_price
                total_cost = asset.shares * asset.avg_cost
                pnl = current_value - total_cost
                pnl_percent = ((current_value - total_cost) / total_cost * 100) if total_cost > 0 else 0
                
                asset_info = {
                    "id": asset.id,
                    "symbol": asset.symbol,
                    "shares": float(asset.shares),
                    "avg_cost": float(asset.avg_cost),
                    "current_price": float(asset.current_price) if asset.current_price else 0.0,
                    "value": float(current_value),
                    "last_updated": asset.last_updated.isoformat() if asset.last_updated else datetime.utcnow().isoformat(),
                    "pnl": float(pnl),
                    "pnl_percent": float(pnl_percent)
                }
                asset_data.append(asset_info)
            
            portfolio_data.append({
                "id": account.id,
                "name": account.name,
                "account_type": account.account_type,
                "balance": float(account_value),
                "created_at": account.created_at.isoformat() if account.created_at else datetime.utcnow().isoformat(),
                "assets": asset_data
            })
            total_value += account_value
        
        # Get AI analysis
        ai_analysis = self.ai_service.analyze_portfolio(portfolio_data)
        
        # Calculate portfolio-level metrics
        total_assets = sum(len(account["assets"]) for account in portfolio_data)
        
        return {
            "accounts": portfolio_data,
            "total_value": float(total_value),
            "total_assets": total_assets,
            "analysis": ai_analysis,
            "last_updated": datetime.utcnow().isoformat(),
            "status": "success"
        }