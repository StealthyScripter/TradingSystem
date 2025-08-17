from sqlalchemy.orm import Session
from typing import List, Dict
import logging
import asyncio
from datetime import datetime

# Fix imports
from app.models.portfolio import Account, Asset
from app.schemas.portfolio import AccountCreate, AssetCreate
from app.services.market_data import MarketDataService
from app.services.enhanced_ai import EnhancedAIService  # New enhanced AI
from app.core.config import settings

class PortfolioService:
    """Core portfolio management service with enhanced AI"""

    def __init__(self, db: Session):
        self.db = db
        self.market_data = MarketDataService()
        # Initialize enhanced AI with API keys from settings
        self.ai_service = EnhancedAIService(
            news_api_key=settings.NEWS_API_KEY,
            alpha_vantage_key=getattr(settings, 'ALPHA_VANTAGE_KEY', None)
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

    def get_portfolio_summary(self) -> Dict:
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

        # Get enhanced AI analysis (async)
        try:
            # Run enhanced AI analysis
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            ai_analysis = loop.run_until_complete(
                self.ai_service.analyze_portfolio_comprehensive(portfolio_data)
            )
            loop.close()

            print("🤖 Enhanced AI analysis completed successfully")

        except Exception as e:
            logging.error(f"Enhanced AI analysis failed: {e}")
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
                "Enhanced analysis temporarily unavailable"
            ]
        }

    async def get_enhanced_asset_analysis(self, symbol: str) -> Dict:
        """Get detailed analysis for a specific asset"""
        try:
            # Get technical analysis
            technical = await self.ai_service._calculate_technical_indicators(symbol)

            # Get sentiment analysis
            sentiment = await self.ai_service._get_real_sentiment(symbol)

            return {
                "symbol": symbol,
                "technical_analysis": {
                    "rsi": technical.rsi,
                    "rsi_signal": "OVERSOLD" if technical.rsi < 30 else "OVERBOUGHT" if technical.rsi > 70 else "NEUTRAL",
                    "macd": technical.macd,
                    "macd_signal": technical.macd_signal,
                    "momentum": technical.momentum,
                    "volatility": technical.volatility,
                    "sma_20": technical.sma_20,
                    "sma_50": technical.sma_50,
                    "price_vs_sma20": "ABOVE" if technical.current_price > technical.sma_20 else "BELOW",
                    "trend": "BULLISH" if technical.sma_20 > technical.sma_50 else "BEARISH"
                },
                "sentiment_analysis": {
                    "sentiment_score": sentiment.sentiment_score,
                    "sentiment": "BULLISH" if sentiment.sentiment_score > 0.2 else "BEARISH" if sentiment.sentiment_score < -0.2 else "NEUTRAL",
                    "confidence": sentiment.confidence,
                    "news_count": sentiment.news_count,
                    "bullish_signals": sentiment.bullish_signals,
                    "bearish_signals": sentiment.bearish_signals,
                    "sources": sentiment.sources
                },
                "overall_recommendation": self._get_asset_recommendation(technical, sentiment),
                "risk_level": self._assess_asset_risk(technical),
                "key_insights": self._generate_asset_insights(symbol, technical, sentiment)
            }

        except Exception as e:
            logging.error(f"Enhanced asset analysis failed for {symbol}: {e}")
            return {
                "symbol": symbol,
                "error": "Analysis temporarily unavailable",
                "fallback_recommendation": "HOLD"
            }

    def _get_asset_recommendation(self, technical, sentiment) -> str:
        """Generate recommendation for individual asset"""
        # Combine technical and sentiment signals
        tech_score = 0
        if technical.rsi < 30:
            tech_score += 1  # Oversold = potential buy
        elif technical.rsi > 70:
            tech_score -= 1  # Overbought = potential sell

        if technical.momentum > 5:
            tech_score += 1  # Positive momentum
        elif technical.momentum < -5:
            tech_score -= 1  # Negative momentum

        # MACD signal
        if technical.macd > technical.macd_signal:
            tech_score += 1
        else:
            tech_score -= 1

        # Sentiment score (normalized)
        sentiment_score = sentiment.sentiment_score * 2  # Scale up

        # Combined score
        total_score = tech_score + sentiment_score

        if total_score >= 2:
            return "STRONG_BUY"
        elif total_score >= 1:
            return "BUY"
        elif total_score <= -2:
            return "STRONG_SELL"
        elif total_score <= -1:
            return "SELL"
        else:
            return "HOLD"

    def _assess_asset_risk(self, technical) -> str:
        """Assess risk level of individual asset"""
        if technical.volatility > 0.4:
            return "HIGH"
        elif technical.volatility > 0.25:
            return "MEDIUM"
        else:
            return "LOW"

    def _generate_asset_insights(self, symbol: str, technical, sentiment) -> List[str]:
        """Generate insights for individual asset"""
        insights = []

        # RSI insights
        if technical.rsi < 30:
            insights.append(f"{symbol} appears oversold (RSI: {technical.rsi:.1f})")
        elif technical.rsi > 70:
            insights.append(f"{symbol} appears overbought (RSI: {technical.rsi:.1f})")

        # Momentum insights
        if abs(technical.momentum) > 10:
            direction = "positive" if technical.momentum > 0 else "negative"
            insights.append(f"Strong {direction} momentum ({technical.momentum:.1f}%)")

        # Volatility insights
        if technical.volatility > 0.4:
            insights.append(f"High volatility asset ({technical.volatility:.1%} annualized)")
        elif technical.volatility < 0.15:
            insights.append(f"Low volatility asset ({technical.volatility:.1%} annualized)")

        # Sentiment insights
        if sentiment.news_count > 10:
            if sentiment.sentiment_score > 0.3:
                insights.append(f"Strong positive news sentiment ({sentiment.news_count} articles)")
            elif sentiment.sentiment_score < -0.3:
                insights.append(f"Strong negative news sentiment ({sentiment.news_count} articles)")

        # Trend insights
        if technical.sma_20 > technical.sma_50 * 1.05:
            insights.append("Strong uptrend (20-day > 50-day SMA)")
        elif technical.sma_20 < technical.sma_50 * 0.95:
            insights.append("Strong downtrend (20-day < 50-day SMA)")

        return insights[:4]  # Limit to 4 insights

# Additional API endpoint helper for enhanced analysis
class EnhancedAnalysisService:
    """Service for enhanced analysis endpoints"""

    def __init__(self, portfolio_service: PortfolioService):
        self.portfolio_service = portfolio_service

    async def get_portfolio_risk_report(self) -> Dict:
        """Generate comprehensive risk report"""
        try:
            accounts = self.portfolio_service.db.query(Account).all()

            # Prepare data
            portfolio_data = []
            holdings = {}
            symbols = []

            for account in accounts:
                account_data = {
                    "id": account.id,
                    "name": account.name,
                    "balance": float(sum(asset.shares * asset.current_price for asset in account.assets)),
                    "assets": []
                }

                for asset in account.assets:
                    asset_value = asset.shares * asset.current_price
                    account_data["assets"].append({
                        "symbol": asset.symbol,
                        "value": asset_value
                    })
                    holdings[asset.symbol] = holdings.get(asset.symbol, 0) + asset_value
                    if asset.symbol not in symbols:
                        symbols.append(asset.symbol)

                portfolio_data.append(account_data)

            # Calculate risk metrics
            risk_metrics = await self.portfolio_service.ai_service._calculate_portfolio_risk(symbols, holdings)

            # Generate optimization
            optimization = await self.portfolio_service.ai_service._optimize_portfolio(symbols, holdings)

            return {
                "risk_metrics": {
                    "value_at_risk_5pct": risk_metrics.value_at_risk,
                    "expected_shortfall": risk_metrics.expected_shortfall,
                    "portfolio_beta": risk_metrics.beta,
                    "sharpe_ratio": risk_metrics.sharpe_ratio,
                    "sortino_ratio": risk_metrics.sortino_ratio,
                    "maximum_drawdown": risk_metrics.maximum_drawdown
                },
                "optimization": {
                    "current_sharpe": risk_metrics.sharpe_ratio,
                    "optimal_sharpe": optimization.sharpe_ratio,
                    "expected_return": optimization.expected_return,
                    "expected_risk": optimization.expected_risk,
                    "diversification_ratio": optimization.diversification_ratio,
                    "optimal_weights": optimization.optimal_weights
                },
                "recommendations": self._generate_risk_recommendations(risk_metrics, optimization),
                "generated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logging.error(f"Risk report generation failed: {e}")
            return {"error": "Risk report temporarily unavailable"}

    def _generate_risk_recommendations(self, risk_metrics, optimization) -> List[str]:
        """Generate risk-based recommendations"""
        recommendations = []

        if risk_metrics.sharpe_ratio < 0.5:
            recommendations.append("Consider improving risk-adjusted returns (Sharpe ratio < 0.5)")

        if abs(risk_metrics.maximum_drawdown) > 0.2:
            recommendations.append("High historical drawdown detected - implement stop-losses")

        if risk_metrics.beta > 1.5:
            recommendations.append("High market sensitivity - consider defensive assets")

        if optimization.diversification_ratio < 0.8:
            recommendations.append("Portfolio lacks diversification - consider broader allocation")

        if optimization.sharpe_ratio > risk_metrics.sharpe_ratio * 1.1:
            recommendations.append("Portfolio optimization could improve returns by 10%+")

        return recommendations
