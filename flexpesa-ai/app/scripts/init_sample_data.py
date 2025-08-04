"""
from app.core.database import SessionLocal, engine, Base
from app.models.portfolio import Account, Asset

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

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

print("Sample data created!")
db.close()
"""