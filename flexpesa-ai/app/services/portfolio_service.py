from sqlalchemy.orm import Session
from typing import List, Dict
import logging
from datetime import datetime

from app.models.portfolio import Account, Asset
from app.schemas.portfolio import AccountCreate, AssetCreate
from app.services.market_data import MarketDataService
from app.services.enhanced_ai import LightweightAIService  # Use lightweight AI service
from app.core.config import settings

class PortfolioService:
    """Core portfolio management service with enhanced AI"""

    def __init__(self, db: Session):
        self.db = db
        self.market_data = MarketDataService()
        # Initialize lightweight AI with only news_api_key
        self.ai_service = LightweightAIService(
            news_api_key=settings.NEWS_API_KEY
        )

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

    async def get_portfolio_summary(self) -> Dict:
        """Get complete portfolio summary with enhanced AI analysis"""
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

        # Get lightweight AI analysis (async)
        try:
            # Run lightweight AI analysis
            ai_analysis = await self.ai_service.analyze_portfolio_fast(portfolio_data)

            print("🤖 Lightweight AI analysis completed successfully")

        except Exception as e:
            logging.error(f"AI analysis failed: {e}")
            # Fallback to basic analysis
            ai_analysis = self._get_fallback_analysis(portfolio_data, total_value)
            print("⚠️  Using fallback analysis due to AI service error")

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

    def _get_fallback_analysis(self, portfolio_data: List[Dict], total_value: float) -> Dict:
        """Fallback analysis if enhanced AI fails"""
        num_assets = sum(len(account.get('assets', [])) for account in portfolio_data)
        diversity_score = min(num_assets / 10, 1.0)

        return {
            "total_value": total_value,
            "diversity_score": diversity_score,
            "risk_score": (1 - diversity_score) * 10,
            "sentiment_score": 0.0,
            "technical_score": 0.0,
            "recommendation": "HOLD" if diversity_score > 0.5 else "DIVERSIFY",
            "confidence": 0.6,
            "insights": [
                f"Portfolio spans {len(portfolio_data)} accounts",
                f"Total of {num_assets} different assets",
                f"Diversity score: {diversity_score:.1%}",
                "Lightweight analysis active"
            ]
        }

    async def get_enhanced_asset_analysis(self, symbol: str) -> Dict:
        """Get detailed analysis for a specific asset"""
        try:
            # Use the lightweight AI service for fast asset analysis
            analysis = await self.ai_service.analyze_asset_fast(symbol)
            return analysis

        except Exception as e:
            logging.error(f"Asset analysis failed for {symbol}: {e}")
            return {
                "symbol": symbol,
                "error": "Analysis temporarily unavailable",
                "fallback_recommendation": "HOLD"
            }
