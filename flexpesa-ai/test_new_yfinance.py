import yfinance as yf

print("Testing new yfinance v0.2.65:")
try:
    # Just use default session
    ticker = yf.Ticker("AAPL")
    info = ticker.info
    price = info.get('regularMarketPrice') or info.get('currentPrice', 0)
    print(f"✅ AAPL: ${price}")
    
    # Test crypto
    btc = yf.Ticker("BTC-USD")
    btc_info = btc.info
    btc_price = btc_info.get('regularMarketPrice') or btc_info.get('currentPrice', 0)
    print(f"✅ BTC-USD: ${btc_price}")
    
except Exception as e:
    print(f"❌ Error: {e}")
