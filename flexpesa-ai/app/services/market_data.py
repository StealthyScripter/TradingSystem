import yfinance as yf
import pandas as pd
from typing import List, Dict
import logging

class MarketDataService:
    """Simple market data service using only yfinance"""
    
    @staticmethod
    def get_current_prices(symbols: List[str]) -> Dict[str, float]:
        """Get current prices for symbols"""
        try:
            if not symbols:
                return {}
                
            tickers = yf.Tickers(' '.join(symbols))
            prices = {}
            
            for symbol in symbols:
                try:
                    ticker = tickers.tickers[symbol]
                    hist = ticker.history(period="1d")
                    if not hist.empty:
                        prices[symbol] = float(hist['Close'].iloc[-1])
                except Exception as e:
                    logging.warning(f"Could not get price for {symbol}: {e}")
                    prices[symbol] = 0.0
            
            return prices
        except Exception as e:
            logging.error(f"Error fetching prices: {e}")
            return {symbol: 0.0 for symbol in symbols}
    
    @staticmethod
    def get_performance_data(symbols: List[str], period: str = "6mo") -> pd.DataFrame:
        """Get historical performance data"""
        try:
            data = yf.download(symbols, period=period, auto_adjust=True)
            if 'Close' in data.columns:
                return data['Close']
            return pd.DataFrame()
        except Exception as e:
            logging.error(f"Error fetching performance data: {e}")
            return pd.DataFrame()
