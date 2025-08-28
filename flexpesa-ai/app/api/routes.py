from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import asyncio
import logging
import pandas as pd
import uuid
from datetime import datetime

from app.core.database import get_db
from app.schemas.portfolio import Account, AccountCreate, Asset, AssetCreate, PortfolioAnalysis
from app.models.portfolio import Account as AccountModel, Asset as AssetModel
from app.services.portfolio_service import PortfolioService
from app.services.perfomance  import PerformanceService

# Import additional Pydantic models for performance tracking
from pydantic import BaseModel, Field

# Extended Pydantic Models for Portfolio Performance
class BenchmarkComparisonResponse(BaseModel):
    name: str
    performance: float

class RiskMetricsResponse(BaseModel):
    beta: float
    volatility: float
    alpha: float
    expense_ratio: float
    sortino_ratio: float
    value_at_risk: float

class PerformancePortfolioResponse(BaseModel):
    id: str
    name: str
    type: str
    total_return: float
    annualized_return: float
    sharpe_ratio: float
    max_drawdown: float
    total_value: float
    last_updated: str
    benchmark_comparisons: List[BenchmarkComparisonResponse]
    risk_metrics: RiskMetricsResponse

class HoldingCreate(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)
    quantity: float = Field(..., gt=0)
    purchase_price: float = Field(..., gt=0)
    purchase_date: str =  Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')

class HoldingResponse(BaseModel):
    symbol: str
    quantity: float
    purchase_price: float
    current_price: float
    purchase_date: str
    market_value: float
    gain_loss: float
    gain_loss_percentage: float

class PortfolioCreateExtended(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., min_length=1, max_length=50)
    initial_investment: float = Field(..., gt=0)
    expense_ratio: Optional[float] = Field(0.5, ge=0, le=5.0)
    holdings: List[HoldingCreate] = []

class PortfolioUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[str] = Field(None, min_length=1, max_length=50)
    expense_ratio: Optional[float] = Field(None, ge=0, le=5.0)

class DailyDataUpdate(BaseModel):
    date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')
    holdings_prices: Dict[str, float] = Field(..., description="Symbol -> Current Price mapping")

class PortfolioSummaryResponse(BaseModel):
    total_portfolios: int
    total_value: float
    average_return: float
    average_sharpe_ratio: float

router = APIRouter()

# ============ EXISTING ROUTES ============
@router.get("/portfolio/summary")
async def get_portfolio_summary(db: Session = Depends(get_db)):
    """Get complete portfolio summary with enhanced AI analysis - MAIN ENDPOINT"""
    service = PortfolioService(db)
    return await service.get_portfolio_summary()

@router.post("/portfolio/update-prices")
async def update_prices(db: Session = Depends(get_db)):
    """Update current prices for all assets"""
    service = PortfolioService(db)
    return await service.update_prices()

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

# ============ ENHANCED PORTFOLIO PERFORMANCE ROUTES ============

@router.get("/portfolios/performance", response_model=List[PerformancePortfolioResponse])
async def get_all_portfolio_performance(db: Session = Depends(get_db)):
    """Get performance analysis for all portfolios"""
    try:
        performance_service = PerformanceService(db)
        return await performance_service.get_all_portfolio_performance()
    except Exception as e:
        logging.error(f"Error getting portfolio performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to get portfolio performance")

@router.get("/portfolios/performance/summary", response_model=PortfolioSummaryResponse)
async def get_portfolio_performance_summary(db: Session = Depends(get_db)):
    """Get summary statistics across all portfolios"""
    try:
        performance_service = PerformanceService(db)
        return await performance_service.get_portfolio_summary()
    except Exception as e:
        logging.error(f"Error getting portfolio summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get portfolio summary")

@router.get("/portfolios/{portfolio_id}/performance", response_model=PerformancePortfolioResponse)
async def get_single_portfolio_performance(portfolio_id: str, db: Session = Depends(get_db)):
    """Get performance metrics for a specific portfolio (account)"""
    try:
        performance_service = PerformanceService(db)
        return await performance_service.get_portfolio_performance(portfolio_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logging.error(f"Error getting portfolio performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to get portfolio performance")

@router.post("/portfolios/", response_model=PerformancePortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_portfolio_with_performance(portfolio: PortfolioCreateExtended, db: Session = Depends(get_db)):
    """Create a new portfolio with initial holdings and performance tracking"""
    try:
        performance_service = PerformanceService(db)
        return await performance_service.create_portfolio_with_holdings(portfolio)
    except Exception as e:
        logging.error(f"Error creating portfolio: {e}")
        raise HTTPException(status_code=500, detail="Failed to create portfolio")

@router.put("/portfolios/{portfolio_id}/performance", response_model=PerformancePortfolioResponse)
async def update_portfolio_with_performance(
    portfolio_id: str,
    portfolio_update: PortfolioUpdate,
    db: Session = Depends(get_db)
):
    """Update existing portfolio and recalculate performance"""
    try:
        performance_service = PerformanceService(db)
        return await performance_service.update_portfolio(portfolio_id, portfolio_update)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logging.error(f"Error updating portfolio: {e}")
        raise HTTPException(status_code=500, detail="Failed to update portfolio")

@router.delete("/portfolios/{portfolio_id}/performance", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio_with_performance(portfolio_id: str, db: Session = Depends(get_db)):
    """Delete a portfolio and all related performance data"""
    try:
        performance_service = PerformanceService(db)
        await performance_service.delete_portfolio(portfolio_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logging.error(f"Error deleting portfolio: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete portfolio")

@router.get("/portfolios/{portfolio_id}/holdings", response_model=List[HoldingResponse])
async def get_portfolio_holdings_with_performance(portfolio_id: str, db: Session = Depends(get_db)):
    """Get detailed holdings with performance metrics for a portfolio"""
    try:
        performance_service = PerformanceService(db)
        return await performance_service.get_portfolio_holdings(portfolio_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logging.error(f"Error getting holdings: {e}")
        raise HTTPException(status_code=500, detail="Failed to get portfolio holdings")

@router.post("/portfolios/{portfolio_id}/holdings")
async def add_holdings_to_portfolio(
    portfolio_id: str,
    holdings: List[HoldingCreate],
    db: Session = Depends(get_db)
):
    """Add or update holdings for a portfolio with performance recalculation"""
    try:
        performance_service = PerformanceService(db)
        result = await performance_service.add_holdings_to_portfolio(portfolio_id, holdings)
        return {"message": "Holdings added successfully", "updated": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logging.error(f"Error adding holdings: {e}")
        raise HTTPException(status_code=500, detail="Failed to add holdings")

@router.post("/portfolios/{portfolio_id}/daily-data")
async def update_daily_performance_data(
    portfolio_id: str,
    daily_data: DailyDataUpdate,
    db: Session = Depends(get_db)
):
    """Update daily price data and recalculate performance metrics"""
    try:
        performance_service = PerformanceService(db)
        result = await performance_service.update_daily_data(portfolio_id, daily_data)
        return {"message": "Daily data updated successfully", "result": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logging.error(f"Error updating daily data: {e}")
        raise HTTPException(status_code=500, detail="Failed to update daily data")

@router.post("/portfolios/{portfolio_id}/recalculate")
async def recalculate_portfolio_performance(portfolio_id: str, db: Session = Depends(get_db)):
    """Force recalculation of portfolio performance metrics"""
    try:
        performance_service = PerformanceService(db)
        result = await performance_service.recalculate_performance(portfolio_id)
        return {"message": "Performance recalculated successfully", "result": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logging.error(f"Error recalculating performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to recalculate performance")

# ============ EXISTING AI ANALYSIS ROUTES ============

@router.post("/analysis/asset/{symbol}")
async def get_enhanced_asset_analysis(symbol: str, db: Session = Depends(get_db)):
    """Get comprehensive AI analysis for a specific asset"""
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

@router.post("/analysis/quick")
def quick_analysis(symbols: List[str], db: Session = Depends(get_db)):
    """Quick AI analysis for specific symbols"""
    service = PortfolioService(db)

    results = {}
    for symbol in symbols:
        # Basic analysis using the lightweight service
        results[symbol] = {
            "sentiment": "neutral",
            "confidence": 0.6,
            "recommendation": "HOLD",
            "note": "Lightweight analysis - upgrade for enhanced features"
        }

    return {"analysis": results}

# Background task for periodic analysis updates
@router.post("/analysis/schedule-update")
async def schedule_analysis_update(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Schedule background update of all AI analysis data"""
    try:
        def run_background_analysis():
            from app.core.database import SessionLocal
            background_db = SessionLocal()
            try:
                service = PortfolioService(background_db)
                # Simple background task - could be expanded
                print("🔄 Background analysis scheduled")
            finally:
                background_db.close()

        background_tasks.add_task(run_background_analysis)

        return {
            "success": True,
            "message": "Analysis update scheduled",
            "timestamp": pd.Timestamp.now().isoformat()
        }

    except Exception as e:
        logging.error(f"Failed to schedule analysis update: {e}")
        raise HTTPException(status_code=500, detail=f"Scheduling failed: {str(e)}")

# Additional simplified endpoints for compatibility
@router.get("/analysis/market-overview")
async def get_market_overview(db: Session = Depends(get_db)):
    """Get basic market overview"""
    return {
        "success": True,
        "market_overview": {
            "overall_sentiment": "NEUTRAL",
            "fear_level": "MEDIUM",
            "portfolio_impact": {
                "recommendation": "BALANCED",
                "risk_level": "MEDIUM"
            }
        },
        "message": "Simplified market overview - upgrade for detailed analysis",
        "timestamp": pd.Timestamp.now().isoformat()
    }

@router.post("/analysis/technical-batch")
async def get_technical_analysis_batch(symbols: List[str], db: Session = Depends(get_db)):
    """Get basic technical analysis for multiple symbols"""
    try:
        if len(symbols) > 20:
            raise HTTPException(status_code=400, detail="Maximum 20 symbols allowed")

        # Simplified technical analysis
        results = {}
        for symbol in symbols:
            results[symbol] = {
                "rsi": 50.0,
                "rsi_signal": "NEUTRAL",
                "trend": "NEUTRAL",
                "volatility": "MEDIUM",
                "momentum": "NEUTRAL",
                "note": "Simplified analysis - upgrade for detailed technical indicators"
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
    """Get basic sentiment analysis for multiple symbols"""
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

        # Simplified sentiment analysis
        results = {}
        for symbol in symbols:
            results[symbol] = {
                "sentiment_score": 0.0,
                "sentiment": "NEUTRAL",
                "confidence": 0.5,
                "strength": "LOW",
                "news_count": 0,
                "note": "Simplified sentiment analysis"
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

# ============ UTILITY ROUTES ============

@router.get("/portfolios/performance/benchmarks")
async def get_available_benchmarks():
    """Get list of available benchmarks for comparison"""
    return {
        "benchmarks": [
            {"name": "S&P 500", "symbol": "SPY", "description": "Large-cap US stocks"},
            {"name": "NASDAQ 100", "symbol": "QQQ", "description": "Technology-focused index"},
            {"name": "Total Stock Market", "symbol": "VTI", "description": "Entire US stock market"},
            {"name": "60/40 Portfolio", "symbol": "BALANCED", "description": "60% stocks, 40% bonds"}
        ]
    }

@router.get("/portfolios/performance/metrics")
async def get_available_metrics():
    """Get list of available performance metrics and their descriptions"""
    return {
        "metrics": {
            "total_return": "Overall percentage gain/loss including dividends",
            "annualized_return": "Standardized yearly return rate",
            "sharpe_ratio": "Return per unit of risk (higher is better)",
            "sortino_ratio": "Return per unit of downside risk",
            "max_drawdown": "Largest peak-to-trough decline",
            "beta": "Sensitivity to market movements",
            "alpha": "Excess return above expected given risk level",
            "volatility": "Standard deviation of returns",
            "value_at_risk": "Potential loss in worst-case scenarios"
        }
    }