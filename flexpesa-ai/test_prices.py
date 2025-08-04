import yfinance as yf

symbols = ["AAPL", "MSFT", "SPY", "QQQ", "VTI", "NVDA", "TSLA", "AMD", "GOOGL", "BTC-USD", "ETH-USD"]

print("Testing yfinance for each symbol:")
for symbol in symbols:
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")
        if not hist.empty:
            price = hist['Close'].iloc[-1]
            print(f"✅ {symbol}: ${price:.2f}")
        else:
            print(f"❌ {symbol}: No data")
    except Exception as e:
        print(f"❌ {symbol}: Error - {e}")
