from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import asyncio
import logging
import pandas as pd

from app.core.database import get_db
from app.schemas.portfolio import Account, AccountCreate, Asset, AssetCreate, PortfolioAnalysis
from app.models.portfolio import Account as AccountModel, Asset as AssetModel
from app.services.portfolio_service import PortfolioService

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

# ============ SIMPLIFIED AI ENDPOINTS ============

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
            service = PortfolioService(db)
            # Simple background task - could be expanded
            print("🔄 Background analysis scheduled")

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
    