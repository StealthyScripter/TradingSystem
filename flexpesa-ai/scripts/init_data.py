import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine, Base
from app.models.portfolio import Account, Asset

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Clear existing data
    db.query(Asset).delete()
    db.query(Account).delete()
    db.commit()

    # Sample data matching your frontend
    accounts_data = [
        {
            "name": "Wells Fargo Intuitive",
            "account_type": "brokerage",
            "assets": [
                {"symbol": "AAPL", "shares": 50, "avg_cost": 155.30},
                {"symbol": "MSFT", "shares": 25, "avg_cost": 285.20},
                {"symbol": "SPY", "shares": 15, "avg_cost": 420.50},
            ]
        },
        {
            "name": "Stack Well",
            "account_type": "investment",
            "assets": [
                {"symbol": "QQQ", "shares": 30, "avg_cost": 350.25},
                {"symbol": "VTI", "shares": 40, "avg_cost": 220.15},
                {"symbol": "NVDA", "shares": 5, "avg_cost": 520.80},
            ]
        },
        {
            "name": "Cash App Investing",
            "account_type": "trading",
            "assets": [
                {"symbol": "TSLA", "shares": 8, "avg_cost": 180.45},
                {"symbol": "AMD", "shares": 25, "avg_cost": 85.60},
                {"symbol": "GOOGL", "shares": 12, "avg_cost": 125.30},
            ]
        },
        {
            "name": "Robinhood",
            "account_type": "crypto",
            "assets": [
                {"symbol": "BTC-USD", "shares": 0.5, "avg_cost": 35000},
                {"symbol": "ETH-USD", "shares": 2.5, "avg_cost": 2200},
            ]
        }
    ]

    for account_data in accounts_data:
        account = Account(name=account_data["name"], account_type=account_data["account_type"])
        db.add(account)
        db.commit()
        db.refresh(account)

        for asset_data in account_data["assets"]:
            asset = Asset(account_id=account.id, **asset_data)
            db.add(asset)

        db.commit()

    print("✅ Sample data created successfully!")
except Exception as e:
    print(f"❌ Error creating sample data: {e}")
    db.rollback()
    raise

print(f"Created {len(accounts_data)} accounts with sample assets")
print("Now you can test the API endpoints:")
print("- http://localhost:8000/")
print("- http://localhost:8000/api/v1/portfolio/summary")
print("- http://localhost:8000/api/v1/accounts/")

db.close()