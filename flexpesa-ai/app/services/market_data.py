import yfinance as yf
import pandas as pd
import time
import random
from typing import List, Dict
import logging

class MarketDataService:
    """Rate-limited market data service that respects Yahoo Finance limits"""

    def __init__(self):
        self.min_delay = 1.0  # 1 second between requests
        self.max_delay = 3.0  # Up to 3 seconds
        self.last_request_time = 0
        self.rate_limit_cooldown = 60  # 60 second cooldown after rate limit
        self.last_rate_limit_time = 0

    def _enforce_rate_limit(self):
        """Enforce rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.min_delay:
            sleep_time = self.min_delay - time_since_last + random.uniform(0, 1)
            print(f"   ⏱️  Rate limiting: sleeping {sleep_time:.1f}s")
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _is_in_cooldown(self) -> bool:
        """Check if we're in rate limit cooldown"""
        if self.last_rate_limit_time == 0:
            return False
        return (time.time() - self.last_rate_limit_time) < self.rate_limit_cooldown

    def get_current_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Get real current prices with rate limiting and fallbacks"""
        service = MarketDataService()

        if not symbols:
            return {}

        # Check cooldown
        if service._is_in_cooldown():
            print(f"⏳ In rate limit cooldown - using mock data")
            return service._get_mock_prices(symbols)

        prices = {}
        print(f"📈 Fetching REAL prices for {len(symbols)} symbols with rate limiting...")

        for i, symbol in enumerate(symbols):
            try:
                # Rate limit all requests except the first
                if i > 0:
                    service._enforce_rate_limit()

                print(f"   Getting {symbol}...")
                price = service._get_single_price_safe(symbol)

                if price > 0:
                    prices[symbol] = price
                    print(f"   ✅ {symbol}: ${price:,.2f}")
                else:
                    prices[symbol] = 0.0
                    print(f"   ⚠️  {symbol}: No price data")

            except Exception as e:
                if "429" in str(e) or "Too Many Requests" in str(e):
                    print(f"   🚫 Rate limited at {symbol}! Switching to mock data")
                    service.last_rate_limit_time = time.time()

                    # Fill remaining symbols with mock data
                    remaining_symbols = symbols[i:]
                    mock_prices = service._get_mock_prices(remaining_symbols)
                    prices.update(mock_prices)
                    break
                else:
                    print(f"   ❌ {symbol}: Error - {e}")
                    prices[symbol] = 0.0

        successful_prices = len([p for p in prices.values() if p > 0])
        print(f"✅ Price fetch complete! Got {successful_prices}/{len(symbols)} prices")
        return prices

    def _get_single_price_safe(self, symbol: str) -> float:
        """Get price for single symbol with multiple strategies"""

        # Strategy 1: Try fast_info (if available)
        try:
            ticker = yf.Ticker(symbol)
            if hasattr(ticker, 'fast_info'):
                fast_info = ticker.fast_info
                if hasattr(fast_info, 'last_price') and fast_info.last_price:
                    return float(fast_info.last_price)
        except:
            pass

        # Strategy 2: Try regular info
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            price_fields = ['regularMarketPrice', 'currentPrice', 'previousClose']
            for field in price_fields:
                price = info.get(field)
                if price and isinstance(price, (int, float)) and price > 0:
                    return float(price)
        except Exception as e:
            if "429" in str(e):
                raise  # Re-raise rate limit errors

        # Strategy 3: Try history
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")

            if not hist.empty and 'Close' in hist.columns:
                return float(hist['Close'].iloc[-1])
        except Exception as e:
            if "429" in str(e):
                raise  # Re-raise rate limit errors

        return 0.0

    def _get_mock_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Get realistic mock prices for development"""
        mock_data = {
            'AAPL': 185.50,
            'MSFT': 338.20,
            'SPY': 445.30,
            'QQQ': 368.75,
            'VTI': 235.80,
            'NVDA': 725.40,
            'TSLA': 198.50,
            'AMD': 126.30,
            'GOOGL': 139.85,
            'BTC-USD': 42350.00,
            'ETH-USD': 2480.00
        }

        result = {}
        for symbol in symbols:
            if symbol in mock_data:
                # Add small random variation (±2%)
                base_price = mock_data[symbol]
                variation = random.uniform(-0.02, 0.02)
                result[symbol] = base_price * (1 + variation)
            else:
                result[symbol] = 100.0  # Default for unknown symbols

        return result

    @staticmethod
    def get_performance_data(symbols: List[str], period: str = "6mo") -> pd.DataFrame:
        """Get historical performance data with error handling"""
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
