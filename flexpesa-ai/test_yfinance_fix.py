import yfinance as yf
import requests

# Set user agent to avoid blocking
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

# Test with session
ticker = yf.Ticker("AAPL", session=session)
try:
    info = ticker.info
    print(f"AAPL current price: ${info.get('regularMarketPrice', 'N/A')}")
except Exception as e:
    print(f"Error: {e}")
