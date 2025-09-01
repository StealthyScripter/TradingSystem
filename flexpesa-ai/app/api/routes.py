from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request, status
from sqlalchemy.orm import Session
from typing import List, Dict, Optional, Any
import asyncio
import logging
import pandas as pd
from datetime import datetime

from app.core.database import get_db
from app.middleware.clerk_auth import get_current_user, get_current_user_optional, get_user_id
from app.schemas.portfolio import Account, AccountCreate, Asset, AssetCreate, PortfolioAnalysis
from app.models.portfolio import Account as AccountModel, Asset as AssetModel
from app.services.portfolio_service import PortfolioService
from app.services.perfomance import PerformanceService
from app.middleware.logging import business_logger
from app.middleware.rate_limit import market_data_limiter, ai_analysis_limiter

# Import Pydantic models for request/response
from pydantic import BaseModel, Field

# Enhanced Pydantic Models for Portfolio Performance
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
    purchase_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')

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

class UserProfileResponse(BaseModel):
    user_id: str
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    total_accounts: int
    total_portfolio_value: float
    last_active: str

router = APIRouter()

# ============ AUTHENTICATION & USER ROUTES ============

@router.get("/auth/profile", response_model=UserProfileResponse)
async def get_user_profile(
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Get current user's profile and portfolio summary"""
    try:
        user_id = user.get("sub")

        # Get user's accounts
        accounts = db.query(AccountModel).filter(
            AccountModel.clerk_user_id == user_id,
            AccountModel.is_active == True
        ).all()

        # Calculate total portfolio value
        total_value = sum(account.total_value for account in accounts)

        return UserProfileResponse(
            user_id=user_id,
            email=user.get("email"),
            first_name=user.get("first_name"),
            last_name=user.get("last_name"),
            total_accounts=len(accounts),
            total_portfolio_value=total_value,
            last_active=datetime.utcnow().isoformat()
        )

    except Exception as e:
        logging.error(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user profile")

@router.get("/auth/config")
async def get_auth_config():
    """Get authentication configuration for frontend"""
    from app.core.config import get_clerk_config

    config = get_clerk_config()
    return {
        "provider": "clerk",
        "configured": config["configured"],
        "publishable_key": config["publishable_key"],
        "domain": config["domain"]
    }

# ============ CORE PORTFOLIO ROUTES ============

@router.get("/portfolio/summary")
async def get_portfolio_summary(
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Get complete portfolio summary with enhanced AI analysis - MAIN ENDPOINT"""
    try:
        user_id = user.get("sub")
        service = PortfolioService(db)

        # Get user-specific portfolio data
        summary = await service.get_portfolio_summary(clerk_user_id=user_id)

        # Log business activity
        business_logger.log_portfolio_update(
            user_id=user_id,
            portfolio_value=summary.get("total_value", 0),
            assets_updated=summary.get("total_assets", 0)
        )

        return summary

    except Exception as e:
        logging.error(f"Error getting portfolio summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get portfolio summary")

@router.post("/portfolio/update-prices")
async def update_prices(
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Update current prices for user's assets"""
    try:
        # Rate limiting for expensive operations
        user_id = user.get("sub")
        if not market_data_limiter.is_allowed(f"user:{user_id}"):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded for price updates"
            )

        service = PortfolioService(db)
        result = await service.update_prices(clerk_user_id=user_id)

        # Log business activity
        business_logger.log_market_data_fetch(
            symbols=result.get("symbols", []),
            success_count=result.get("updated_assets", 0),
            duration=result.get("duration", 0)
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating prices: {e}")
        raise HTTPException(status_code=500, detail="Failed to update prices")

@router.post("/accounts/", response_model=Account)
def create_account(
    account: AccountCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Create new investment account"""
    try:
        user_id = user.get("sub")
        service = PortfolioService(db)

        # Add user ID to account creation
        result = service.create_account(account, clerk_user_id=user_id)

        # Log business activity
        business_logger.log_user_action(
            user_id=user_id,
            action="create_account",
            details={"account_name": account.name, "account_type": account.account_type}
        )

        return result

    except Exception as e:
        logging.error(f"Error creating account: {e}")
        raise HTTPException(status_code=500, detail="Failed to create account")

@router.get("/accounts/", response_model=List[Account])
def get_accounts(
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Get all user's accounts"""
    try:
        user_id = user.get("sub")

        accounts = db.query(AccountModel).filter(
            AccountModel.clerk_user_id == user_id,
            AccountModel.is_active == True
        ).all()

        return accounts

    except Exception as e:
        logging.error(f"Error getting accounts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get accounts")

@router.post("/assets/", response_model=Asset)
def add_asset(
    asset: AssetCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Add asset to account"""
    try:
        user_id = user.get("sub")

        # Verify account belongs to user
        account = db.query(AccountModel).filter(
            AccountModel.id == asset.account_id,
            AccountModel.clerk_user_id == user_id,
            AccountModel.is_active == True
        ).first()

        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        service = PortfolioService(db)
        result = service.add_asset(asset)

        # Log business activity
        business_logger.log_user_action(
            user_id=user_id,
            action="add_asset",
            details={
                "symbol": asset.symbol,
                "shares": asset.shares,
                "account_id": asset.account_id
            }
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error adding asset: {e}")
        raise HTTPException(status_code=500, detail="Failed to add asset")

# ============ ENHANCED PORTFOLIO PERFORMANCE ROUTES ============

@router.get("/portfolios/performance", response_model=List[PerformancePortfolioResponse])
async def get_all_portfolio_performance(
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Get performance analysis for all user's portfolios"""
    try:
        user_id = user.get("sub")
        performance_service = PerformanceService(db)

        return await performance_service.get_all_portfolio_performance(
            clerk_user_id=user_id
        )

    except Exception as e:
        logging.error(f"Error getting portfolio performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to get portfolio performance")

@router.get("/portfolios/performance/summary", response_model=PortfolioSummaryResponse)
async def get_portfolio_performance_summary(
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Get summary statistics across all user's portfolios"""
    try:
        user_id = user.get("sub")
        performance_service = PerformanceService(db)

        return await performance_service.get_portfolio_summary(clerk_user_id=user_id)

    except Exception as e:
        logging.error(f"Error getting portfolio summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get portfolio summary")

@router.get("/portfolios/{portfolio_id}/performance", response_model=PerformancePortfolioResponse)
async def get_single_portfolio_performance(
    portfolio_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Get performance metrics for a specific portfolio (account)"""
    try:
        user_id = user.get("sub")
        performance_service = PerformanceService(db)

        return await performance_service.get_portfolio_performance(
            portfolio_id, clerk_user_id=user_id
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logging.error(f"Error getting portfolio performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to get portfolio performance")

# ============ AI ANALYSIS ROUTES ============

@router.post("/analysis/asset/{symbol}")
async def get_enhanced_asset_analysis(
    symbol: str,
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Get comprehensive AI analysis for a specific asset"""
    try:
        user_id = user.get("sub")

        # Rate limiting for AI operations
        if not ai_analysis_limiter.is_allowed(f"user:{user_id}"):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded for AI analysis"
            )

        service = PortfolioService(db)
        start_time = datetime.utcnow()

        analysis = await service.get_enhanced_asset_analysis(symbol.upper())

        processing_time = (datetime.utcnow() - start_time).total_seconds()

        # Log business activity
        business_logger.log_ai_analysis(
            user_id=user_id,
            analysis_type="asset_analysis",
            processing_time=processing_time
        )

        return {
            "success": True,
            "symbol": symbol.upper(),
            "analysis": analysis,
            "timestamp": pd.Timestamp.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Enhanced asset analysis failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/analysis/quick")
def quick_analysis(
    symbols: List[str],
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Quick AI analysis for specific symbols"""
    try:
        if len(symbols) > 20:  # Limit for performance
            raise HTTPException(status_code=400, detail="Maximum 20 symbols allowed")

        user_id = user.get("sub")
        service = PortfolioService(db)

        results = {}
        for symbol in symbols:
            results[symbol] = {
                "sentiment": "neutral",
                "confidence": 0.6,
                "recommendation": "HOLD",
                "note": "Quick analysis - use enhanced analysis for detailed insights"
            }

        # Log business activity
        business_logger.log_user_action(
            user_id=user_id,
            action="quick_analysis",
            details={"symbols": symbols, "count": len(symbols)}
        )

        return {"analysis": results}

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Quick analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")

# ============ PUBLIC ROUTES (No Authentication Required) ============

@router.get("/market/status")
async def get_market_status(user: dict = Depends(get_current_user_optional)):
    """Get current market status (public endpoint)"""
    try:
        # Basic market status - could be enhanced with real market data
        return {
            "status": "open",  # Could check actual market hours
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Market data available",
            "authenticated": user is not None
        }

    except Exception as e:
        logging.error(f"Error getting market status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get market status")

@router.get("/health/detailed")
async def detailed_health_check(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user_optional)
):
    """Detailed health check including database connectivity"""
    try:
        # Test database connection
        db.execute("SELECT 1")

        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "database": "healthy",
                "authentication": "healthy" if user else "not_authenticated",
                "api": "healthy"
            },
            "version": "1.0.0"
        }

        return health_data

    except Exception as e:
        logging.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

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
    