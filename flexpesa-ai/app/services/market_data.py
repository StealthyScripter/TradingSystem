import yfinance as yf
import pandas as pd
from typing import List, Dict
import logging

class MarketDataService:
    """Real market data service using yfinance v0.2.65+"""
    
    @staticmethod
    def get_current_prices(symbols: List[str]) -> Dict[str, float]:
        """Get real current prices using new yfinance"""
        if not symbols:
            return {}
            
        prices = {}
        print(f"📈 Fetching REAL prices for {len(symbols)} symbols...")
        
        for symbol in symbols:
            try:
                print(f"   Getting {symbol}...")
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # Try multiple price fields (yfinance returns different fields)
                price = (info.get('regularMarketPrice') or 
                        info.get('currentPrice') or 
                        info.get('previousClose') or 0)
                
                if price > 0:
                    prices[symbol] = float(price)
                    print(f"   ✅ {symbol}: ${price:,.2f}")
                else:
                    print(f"   ❌ {symbol}: No price found")
                    prices[symbol] = 0.0
                        
            except Exception as e:
                print(f"   ❌ {symbol}: Error - {e}")
                prices[symbol] = 0.0
        
        successful_prices = len([p for p in prices.values() if p > 0])
        print(f"✅ Real price fetch complete! Got {successful_prices}/{len(symbols)} prices")
        return prices
    
    @staticmethod
    def get_performance_data(symbols: List[str], period: str = "6mo") -> pd.DataFrame:
        """Get historical performance data"""
        try:
            print(f"📊 Fetching {period} performance data for {symbols}")
            data = yf.download(symbols, period=period, auto_adjust=True, progress=False)
            
            if 'Close' in data.columns:
                return data['Close']
            elif len(symbols) == 1:
                return data[['Close']].rename(columns={'Close': symbols[0]})
            
            return pd.DataFrame()
        except Exception as e:
            logging.error(f"Error fetching performance data: {e}")
            return pd.DataFrame()
