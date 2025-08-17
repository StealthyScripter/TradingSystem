from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import asyncio
import logging

from app.core.database import get_db
from app.schemas.portfolio import Account, AccountCreate, Asset, AssetCreate, PortfolioAnalysis
from app.models.portfolio import Account as AccountModel, Asset as AssetModel
from app.services.portfolio_service import PortfolioService, EnhancedAnalysisService

router = APIRouter()

@router.get("/portfolio/summary")
def get_portfolio_summary(db: Session = Depends(get_db)):
    """Get complete portfolio summary with enhanced AI analysis - MAIN ENDPOINT"""
    service = PortfolioService(db)
    return service.get_portfolio_summary()

@router.post("/portfolio/update-prices")
def update_prices(db: Session = Depends(get_db)):
    """Update current prices for all assets"""
    service = PortfolioService(db)
    return service.update_prices()

@router.post("/accounts/", response_model=Account)
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    """Create new investment account"""
    service = PortfolioService(db)
    return service.create_account(account)

@router.get("/accounts/", response_model=List[Account])
def get_accounts(db: Session = Depends(get_db)):
    """Get all accounts"""
    accounts = db.query(AccountModel).all()
    return accounts

@router.post("/assets/", response_model=Asset)
def add_asset(asset: AssetCreate, db: Session = Depends(get_db)):
    """Add asset to account"""
    service = PortfolioService(db)
    return service.add_asset(asset)

# ============ ENHANCED AI ENDPOINTS ============

@router.post("/analysis/asset/{symbol}")
async def get_enhanced_asset_analysis(symbol: str, db: Session = Depends(get_db)):
    """Get comprehensive AI analysis for a specific asset

    Returns:
    - Technical analysis (RSI, MACD, momentum, volatility)
    - Sentiment analysis from news sources
    - Buy/Sell/Hold recommendation
    - Risk assessment
    - Key insights
    """
    try:
        service = PortfolioService(db)
        analysis = await service.get_enhanced_asset_analysis(symbol.upper())
        return {
            "success": True,
            "symbol": symbol.upper(),
            "analysis": analysis,
            "timestamp": pd.Timestamp.now().isoformat()
        }
    except Exception as e:
        logging.error(f"Enhanced asset analysis failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/analysis/risk-report")
async def get_portfolio_risk_report(db: Session = Depends(get_db)):
    """Generate comprehensive portfolio risk assessment

    Returns:
    - Value at Risk (VaR) metrics
    - Sharpe ratio and risk-adjusted returns
    - Beta and market correlation
    - Portfolio optimization suggestions
    - Risk-based recommendations
    """
    try:
        service = PortfolioService(db)
        enhanced_service = EnhancedAnalysisService(service)
        risk_report = await enhanced_service.get_portfolio_risk_report()

        return {
            "success": True,
            "risk_report": risk_report,
            "timestamp": pd.Timestamp.now().isoformat()
        }
    except Exception as e:
        logging.error(f"Risk report generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Risk report failed: {str(e)}")

@router.post("/analysis/technical-batch")
async def get_technical_analysis_batch(symbols: List[str], db: Session = Depends(get_db)):
    """Get technical analysis for multiple symbols

    Body: {"symbols": ["AAPL", "MSFT", "GOOGL"]}

    Returns technical indicators for each symbol:
    - RSI, MACD, Bollinger Bands
    - Moving averages (20-day, 50-day)
    - Momentum and volatility
    """
    try:
        if len(symbols) > 20:
            raise HTTPException(status_code=400, detail="Maximum 20 symbols allowed")

        service = PortfolioService(db)

        # Run technical analysis for all symbols
        technical_data = await service.ai_service._get_technical_analysis_batch(symbols)

        # Format response
        results = {}
        for symbol, indicators in technical_data.items():
            results[symbol] = {
                "rsi": indicators.rsi,
                "rsi_signal": "OVERSOLD" if indicators.rsi < 30 else "OVERBOUGHT" if indicators.rsi > 70 else "NEUTRAL",
                "macd": indicators.macd,
                "macd_signal": indicators.macd_signal,
                "macd_crossover": "BULLISH" if indicators.macd > indicators.macd_signal else "BEARISH",
                "bollinger_position": "ABOVE_UPPER" if indicators.current_price > indicators.bollinger_upper else
                                    "BELOW_LOWER" if indicators.current_price < indicators.bollinger_lower else "WITHIN_BANDS",
                "sma_20": indicators.sma_20,
                "sma_50": indicators.sma_50,
                "trend": "BULLISH" if indicators.sma_20 > indicators.sma_50 else "BEARISH",
                "volatility": indicators.volatility,
                "volatility_level": "HIGH" if indicators.volatility > 0.4 else "MEDIUM" if indicators.volatility > 0.25 else "LOW",
                "momentum": indicators.momentum,
                "momentum_signal": "STRONG_POSITIVE" if indicators.momentum > 10 else
                                 "POSITIVE" if indicators.momentum > 0 else
                                 "NEGATIVE" if indicators.momentum > -10 else "STRONG_NEGATIVE"
            }

        return {
            "success": True,
            "technical_analysis": results,
            "symbols_analyzed": len(results),
            "timestamp": pd.Timestamp.now().isoformat()
        }

    except Exception as e:
        logging.error(f"Batch technical analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Technical analysis failed: {str(e)}")

@router.post("/analysis/sentiment-batch")
async def get_sentiment_analysis_batch(symbols: List[str], db: Session = Depends(get_db)):
    """Get sentiment analysis for multiple symbols

    Body: {"symbols": ["AAPL", "MSFT", "GOOGL"]}

    Returns sentiment data from news sources:
    - Overall sentiment score (-1 to 1)
    - Bullish/bearish signal counts
    - News article count and sources
    - Confidence level
    """
    try:
        if len(symbols) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 symbols allowed for sentiment analysis")

        service = PortfolioService(db)

        # Check if NEWS_API_KEY is available
        if not service.ai_service.news_api_key:
            return {
                "success": False,
                "error": "News API key not configured",
                "message": "Sentiment analysis requires NEWS_API_KEY in environment variables"
            }

        # Run sentiment analysis
        sentiment_data = await service.ai_service._get_sentiment_analysis_batch(symbols)

        # Format response
        results = {}
        for symbol, sentiment in sentiment_data.items():
            results[symbol] = {
                "sentiment_score": sentiment.sentiment_score,
                "sentiment": "BULLISH" if sentiment.sentiment_score > 0.2 else
                           "BEARISH" if sentiment.sentiment_score < -0.2 else "NEUTRAL",
                "confidence": sentiment.confidence,
                "strength": "HIGH" if sentiment.confidence > 0.7 else
                           "MEDIUM" if sentiment.confidence > 0.4 else "LOW",
                "news_count": sentiment.news_count,
                "bullish_signals": sentiment.bullish_signals,
                "bearish_signals": sentiment.bearish_signals,
                "signal_ratio": sentiment.bullish_signals / max(sentiment.bearish_signals, 1),
                "sources": sentiment.sources
            }

        return {
            "success": True,
            "sentiment_analysis": results,
            "symbols_analyzed": len(results),
            "timestamp": pd.Timestamp.now().isoformat()
        }

    except Exception as e:
        logging.error(f"Batch sentiment analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")

@router.post("/analysis/optimize-portfolio")
async def optimize_portfolio(db: Session = Depends(get_db)):
    """Run Modern Portfolio Theory optimization

    Returns:
    - Optimal asset weights for maximum Sharpe ratio
    - Expected return and risk metrics
    - Current vs. optimal portfolio comparison
    - Rebalancing recommendations
    """
    try:
        service = PortfolioService(db)

        # Get current portfolio data
        accounts = db.query(AccountModel).all()
        if not accounts:
            raise HTTPException(status_code=404, detail="No portfolio data found")

        # Prepare optimization data
        symbols = []
        holdings = {}
        current_weights = {}
        total_value = 0

        for account in accounts:
            for asset in account.assets:
                if asset.symbol and asset.symbol != 'UNKNOWN':
                    asset_value = asset.shares * asset.current_price
                    holdings[asset.symbol] = holdings.get(asset.symbol, 0) + asset_value
                    total_value += asset_value
                    if asset.symbol not in symbols:
                        symbols.append(asset.symbol)

        # Calculate current weights
        for symbol in symbols:
            current_weights[symbol] = holdings[symbol] / total_value

        # Run optimization
        optimization = await service.ai_service._optimize_portfolio(symbols, holdings)

        # Calculate rebalancing needs
        rebalancing = {}
        for symbol in symbols:
            current_weight = current_weights.get(symbol, 0)
            optimal_weight = optimization.optimal_weights.get(symbol, 0)
            difference = optimal_weight - current_weight
            rebalancing[symbol] = {
                "current_weight": current_weight,
                "optimal_weight": optimal_weight,
                "difference": difference,
                "action": "BUY" if difference > 0.05 else "SELL" if difference < -0.05 else "HOLD",
                "amount_to_rebalance": abs(difference * total_value)
            }

        return {
            "success": True,
            "optimization": {
                "current_portfolio": {
                    "expected_return": "Not calculated",  # Would need historical analysis
                    "sharpe_ratio": "Not calculated",
                    "weights": current_weights
                },
                "optimal_portfolio": {
                    "expected_return": optimization.expected_return,
                    "expected_risk": optimization.expected_risk,
                    "sharpe_ratio": optimization.sharpe_ratio,
                    "diversification_ratio": optimization.diversification_ratio,
                    "weights": optimization.optimal_weights
                },
                "improvement_potential": {
                    "sharpe_improvement": optimization.sharpe_ratio - 0.5,  # Assuming current Sharpe
                    "diversification_improvement": optimization.diversification_ratio - 1.0
                },
                "rebalancing": rebalancing
            },
            "recommendations": self._generate_optimization_recommendations(optimization, rebalancing),
            "timestamp": pd.Timestamp.now().isoformat()
        }

    except Exception as e:
        logging.error(f"Portfolio optimization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

def _generate_optimization_recommendations(optimization, rebalancing) -> List[str]:
    """Generate actionable optimization recommendations"""
    recommendations = []

    if optimization.sharpe_ratio > 1.0:
        recommendations.append("Excellent risk-adjusted returns - maintain current strategy")
    elif optimization.sharpe_ratio < 0.5:
        recommendations.append("Consider improving risk-adjusted returns through rebalancing")

    # Check for major rebalancing needs
    major_rebalances = [symbol for symbol, data in rebalancing.items()
                       if abs(data["difference"]) > 0.1]

    if major_rebalances:
        recommendations.append(f"Consider rebalancing {', '.join(major_rebalances[:3])}")

    if optimization.diversification_ratio > 1.2:
        recommendations.append("Portfolio benefits from good diversification")
    elif optimization.diversification_ratio < 0.8:
        recommendations.append("Increase diversification across asset classes")

    if optimization.expected_return > 0.12:
        recommendations.append("High expected returns - monitor risk levels")
    elif optimization.expected_return < 0.06:
        recommendations.append("Consider growth-oriented assets for higher returns")

    return recommendations

@router.get("/analysis/market-overview")
async def get_market_overview(db: Session = Depends(get_db)):
    """Get overall market conditions and their impact on portfolio

    Returns:
    - Market indices analysis
    - Volatility levels
    - Sector performance
    - Portfolio correlation with market
    """
    try:
        service = PortfolioService(db)

        # Analyze major market indices
        market_symbols = ["^GSPC", "^IXIC", "^DJI", "^VIX"]  # S&P 500, NASDAQ, Dow, VIX

        market_analysis = {}
        for symbol in market_symbols:
            try:
                technical = await service.ai_service._calculate_technical_indicators(symbol)
                market_analysis[symbol] = {
                    "momentum": technical.momentum,
                    "volatility": technical.volatility,
                    "rsi": technical.rsi,
                    "trend": "BULLISH" if technical.sma_20 > technical.sma_50 else "BEARISH"
                }
            except:
                market_analysis[symbol] = {"status": "Data unavailable"}

        # Overall market sentiment
        market_sentiment = "NEUTRAL"
        if market_analysis.get("^GSPC", {}).get("momentum", 0) > 5:
            market_sentiment = "BULLISH"
        elif market_analysis.get("^GSPC", {}).get("momentum", 0) < -5:
            market_sentiment = "BEARISH"

        # VIX analysis (fear index)
        vix_data = market_analysis.get("^VIX", {})
        fear_level = "MEDIUM"
        if vix_data.get("momentum", 0) > 20:
            fear_level = "HIGH"
        elif vix_data.get("momentum", 0) < -20:
            fear_level = "LOW"

        return {
            "success": True,
            "market_overview": {
                "overall_sentiment": market_sentiment,
                "fear_level": fear_level,
                "indices_analysis": market_analysis,
                "portfolio_impact": {
                    "recommendation": "DEFENSIVE" if market_sentiment == "BEARISH" else
                                   "AGGRESSIVE" if market_sentiment == "BULLISH" else "BALANCED",
                    "risk_level": "HIGH" if fear_level == "HIGH" else "MEDIUM"
                }
            },
            "timestamp": pd.Timestamp.now().isoformat()
        }

    except Exception as e:
        logging.error(f"Market overview failed: {e}")
        raise HTTPException(status_code=500, detail=f"Market overview failed: {str(e)}")

# Background task for periodic analysis updates
@router.post("/analysis/schedule-update")
async def schedule_analysis_update(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Schedule background update of all AI analysis data

    This endpoint triggers background analysis updates without blocking the response.
    Useful for periodic data refresh.
    """
    try:
        def run_background_analysis():
            service = PortfolioService(db)
            # Run comprehensive analysis in background
            asyncio.run(service.ai_service.analyze_portfolio_comprehensive([]))

        background_tasks.add_task(run_background_analysis)

        return {
            "success": True,
            "message": "Analysis update scheduled",
            "timestamp": pd.Timestamp.now().isoformat()
        }

    except Exception as e:
        logging.error(f"Failed to schedule analysis update: {e}")
        raise HTTPException(status_code=500, detail=f"Scheduling failed: {str(e)}")

# Legacy endpoint (maintained for compatibility)
@router.post("/analysis/quick")
def quick_analysis(symbols: List[str], db: Session = Depends(get_db)):
    """Legacy quick AI analysis for specific symbols (deprecated)

    Use /analysis/asset/{symbol} or /analysis/technical-batch instead
    """
    service = PortfolioService(db)

    results = {}
    for symbol in symbols:
        # Basic sentiment fallback
        sentiment = service.ai_service._get_neutral_sentiment()
        results[symbol] = {
            "sentiment": "neutral",
            "confidence": sentiment.confidence,
            "recommendation": "HOLD",
            "note": "Use enhanced endpoints for detailed analysis"
        }

    return {"analysis": results}
