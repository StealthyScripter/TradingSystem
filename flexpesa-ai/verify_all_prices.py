import yfinance as yf

symbols = ["AAPL", "MSFT", "SPY", "QQQ", "VTI", "NVDA", "TSLA", "AMD", "GOOGL", "BTC-USD", "ETH-USD"]

print("Real market prices from yfinance v0.2.65:")
total_portfolio_value = 0

# Your actual holdings
holdings = {
    "AAPL": 50, "MSFT": 25, "SPY": 15,
    "QQQ": 30, "VTI": 40, "NVDA": 5,
    "TSLA": 8, "AMD": 25, "GOOGL": 12,
    "BTC-USD": 0.5, "ETH-USD": 2.5
}

for symbol in symbols:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        price = info.get('regularMarketPrice') or info.get('currentPrice', 0)
        shares = holdings.get(symbol, 0)
        value = price * shares
        total_portfolio_value += value
        print(f"✅ {symbol}: ${price:,.2f} × {shares} = ${value:,.2f}")
    except Exception as e:
        print(f"❌ {symbol}: {e}")

print(f"\n🎯 Total Portfolio Value: ${total_portfolio_value:,.2f}")
