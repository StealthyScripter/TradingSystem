from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.portfolio import Account, AccountCreate, Asset, AssetCreate, PortfolioAnalysis
from app.services.portfolio_service import PortfolioService
from typing import List

router = APIRouter()

@router.get("/portfolio/summary")
def get_portfolio_summary(db: Session = Depends(get_db)):
    """Get complete portfolio summary - MAIN ENDPOINT for dashboard"""
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
    return db.query(Account).all()

@router.post("/assets/", response_model=Asset)
def add_asset(asset: AssetCreate, db: Session = Depends(get_db)):
    """Add asset to account"""
    service = PortfolioService(db)
    return service.add_asset(asset)

@router.post("/analysis/quick")
def quick_analysis(symbols: List[str], db: Session = Depends(get_db)):
    """Quick AI analysis for specific symbols"""
    service = PortfolioService(db)
    
    results = {}
    for symbol in symbols:
        sentiment = service.ai_service.get_basic_sentiment(symbol)
        results[symbol] = sentiment
    
    return {"analysis": results}
