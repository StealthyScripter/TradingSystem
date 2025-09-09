from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import logging
from datetime import datetime
from pydantic import ValidationError
from app.models.portfolio import Account, Asset, MarketData, PortfolioSnapshot
from app.schemas.portfolio import AccountCreate, AssetCreate
from app.services.market_data import MarketDataService
from app.services.enhanced_ai import LightweightAIService
from app.core.config import settings

class PortfolioService:
    """Core portfolio management service with enhanced AI and Clerk authentication"""

    def __init__(self, db: Session):
        self.db = db
        self.market_data = MarketDataService(db)
        # Initialize lightweight AI with API keys from settings
        self.ai_service = LightweightAIService(
            news_api_key=settings.NEWS_API_KEY
        )

    def create_account(self, account: AccountCreate, clerk_user_id: str) -> Account:
        """Create new investment account for a specific user"""
        try:
            db_account = Account(
                clerk_user_id=clerk_user_id,
                name=account.name,
                account_type=account.account_type,
                description=getattr(account, 'description', None),
                currency=getattr(account, 'currency', 'USD')
            )

            self.db.add(db_account)
            self.db.commit()
            self.db.refresh(db_account)

            logging.info(f"Created account '{account.name}' for user {clerk_user_id}")
            return db_account

        except Exception as e:
            self.db.rollback()
            logging.error(f"Failed to create account: {e}")
            raise

    async def add_asset(self, asset: AssetCreate) -> Asset:
        """Add asset to account with enhanced data"""
        try:
            # Check if account exists and is active
            account = self.db.query(Account).filter(
                Account.id == asset.account_id,
                Account.is_active == True
            ).first()

            if not account:
                raise ValueError("Account not found or inactive")

            # Check for existing asset in the same account
            existing_asset = self.db.query(Asset).filter(
                Asset.account_id == asset.account_id,
                Asset.symbol == asset.symbol.upper(),
                Asset.is_active == True
            ).first()

            if existing_asset:
                # Update existing asset (average down/up the cost)
                total_shares = existing_asset.shares + asset.shares
                total_cost = (existing_asset.shares * existing_asset.avg_cost +
                            asset.shares * asset.avg_cost)
                new_avg_cost = total_cost / total_shares if total_shares > 0 else asset.avg_cost

                existing_asset.shares = total_shares
                existing_asset.avg_cost = new_avg_cost
                existing_asset.last_updated = datetime.utcnow()

                self.db.commit()
                self.db.refresh(existing_asset)

                logging.info(f"Updated existing asset {asset.symbol} in account {asset.account_id}")
                return existing_asset
            else:
                # Create new asset
                db_asset = Asset(
                    account_id=asset.account_id,
                    symbol=asset.symbol.upper(),
                    shares=asset.shares,
                    avg_cost=asset.avg_cost,
                    current_price=asset.avg_cost,  # Initialize with purchase price
                    asset_type=self._determine_asset_type(asset.symbol),
                    currency=getattr(asset, 'currency', 'USD')
                )

                self.db.add(db_asset)
                self.db.commit()
                self.db.refresh(db_asset)

               # Try to update market data separately (non-critical)
                try:
                    await self._update_market_data(asset.symbol, asset.avg_cost)

                    # Optionally update asset with fresh market data
                    fresh_data = self.db.query(MarketData).filter(MarketData.symbol == asset.symbol).first()
                    if fresh_data:
                        db_asset.current_price = fresh_data.current_price
                        self.db.commit()
                except Exception as e:
                    logging.warning(f"Market data update failed for {asset.symbol}: {e}")

                logging.info(f"Added new asset {asset.symbol} to account {asset.account_id}")
                return db_asset
        except ValidationError as e:
            logging.error(f"Asset validation failed: {e}")

        except Exception as e:
            self.db.rollback()
            logging.error(f"Failed to add asset: {e}")
            raise

    def _validate_and_normalize_symbol(self, symbol: str) -> str:
        """Validate and normalize symbol"""
        symbol = symbol.strip().upper()

        # Check symbol format
        if len(symbol) > 10:
            raise ValueError("Symbol too long (max 10 characters)")

        # Check for valid characters (letters, numbers, hyphens)
        if not all(c.isalnum() or c in ['-', '.'] for c in symbol):
            raise ValueError("Symbol contains invalid characters")

        # Check against known invalid patterns
        invalid_patterns = ['', 'NULL', 'UNDEFINED', 'TEST']
        if symbol in invalid_patterns:
            raise ValueError(f"Invalid symbol: {symbol}")

        return symbol

    def _validate_business_rules(self, asset: AssetCreate, account: Account):
        """Validate business rules"""
        # Check account type restrictions
        if account.account_type == "retirement" and asset.symbol.endswith("-USD"):
            raise ValueError("Cryptocurrency not allowed in retirement accounts")

        # Check position size limits
        max_position_value = asset.shares * asset.avg_cost
        if max_position_value > 1000000:  # $1M limit per position
            raise ValueError("Position size exceeds maximum allowed")

        # Check for duplicate active positions
        existing = self.db.query(Asset).filter(
            Asset.account_id == asset.account_id,
            Asset.symbol == asset.symbol,
            Asset.is_active == True
        ).first()

        # Note: This is handled by combining positions, but could be restricted

    async def _validate_market_data(self, symbol: str):
        """Validate symbol exists in market data"""
        try:
            # Attempt to fetch market data for validation
            market_data = await self._get_or_fetch_market_data(symbol)

            # If we can't get any market data, warn but don't fail
            if not market_data:
                logging.warning(f"No market data available for symbol: {symbol}")
                # Could choose to raise error here if strict validation needed

        except Exception as e:
            logging.warning(f"Market data validation failed for {symbol}: {e}")
            # Decide whether to fail or continue

    def _validate_position_limits(self, asset: AssetCreate, account: Account):
        """Validate position and account limits"""
        # Calculate new total account value
        current_value = account.total_value
        new_position_value = asset.shares * asset.avg_cost
        projected_value = current_value + new_position_value

        # Account value limits (example: $10M max per account)
        if projected_value > 10000000:
            raise ValueError("Adding this position would exceed account value limit")

        # Asset count limits (example: max 100 different assets per account)
        current_asset_count = len([a for a in account.assets if a.is_active])
        if current_asset_count >= 100:
            raise ValueError("Account has reached maximum number of assets (100)")

    async def update_prices(self, clerk_user_id: str = None) -> Dict:
        """Update current prices for user's assets or all assets"""
        try:
            start_time = datetime.utcnow()

            # Get assets to update
            query = self.db.query(Asset).filter(Asset.is_active == True)

            if clerk_user_id:
                # Only update assets for specific user
                query = query.join(Account).filter(
                    Account.clerk_user_id == clerk_user_id,
                    Account.is_active == True
                )

            assets = query.all()

            if not assets:
                return {"updated_assets": 0, "total_assets": 0, "message": "No assets to update"}

            # Get unique symbols
            symbols = list(set(asset.symbol for asset in assets))

            logging.info(f"🔄 Updating prices for {len(symbols)} unique symbols from {len(assets)} assets")

            # Fetch current prices
            current_prices = self.market_data.get_current_prices(symbols)

            updated_count = 0
            failed_symbols = []

            # Update assets with new prices
            for asset in assets:
                try:
                    if asset.symbol in current_prices and current_prices[asset.symbol] > 0:
                        old_price = asset.current_price
                        new_price = current_prices[asset.symbol]

                        # Calculate day change
                        if old_price and old_price > 0:
                            asset.day_change = new_price - old_price
                            asset.day_change_percent = ((new_price - old_price) / old_price) * 100

                        asset.current_price = new_price
                        asset.price_updated_at = datetime.utcnow()
                        asset.last_updated = datetime.utcnow()

                        updated_count += 1

                        if old_price != new_price:
                            logging.info(f"   ✅ {asset.symbol}: ${old_price:.2f} → ${new_price:.2f}")
                    else:
                        failed_symbols.append(asset.symbol)
                        logging.warning(f"   ❌ {asset.symbol}: No price data available")

                except Exception as e:
                    failed_symbols.append(asset.symbol)
                    logging.error(f"   ❌ {asset.symbol}: Update failed - {e}")

            # Update account balances
            if clerk_user_id:
                self._update_account_balances(clerk_user_id)

            # Create portfolio snapshot if for specific user
            if clerk_user_id:
                await self._create_portfolio_snapshot(clerk_user_id)

            self.db.commit()

            duration = (datetime.utcnow() - start_time).total_seconds()

            result = {
                "updated_assets": updated_count,
                "total_assets": len(assets),
                "unique_symbols": len(symbols),
                "failed_symbols": failed_symbols,
                "duration": duration,
                "timestamp": datetime.utcnow().isoformat()
            }

            logging.info(f"📊 Price update complete: {updated_count}/{len(assets)} assets updated in {duration:.2f}s")
            return result

        except Exception as e:
            self.db.rollback()
            logging.error(f"Price update failed: {e}")
            raise

    async def get_portfolio_summary(self, clerk_user_id: str) -> Dict:
        """Get complete portfolio summary with enhanced AI analysis for specific user"""
        try:
            # Get user's accounts
            accounts = self.db.query(Account).filter(
                Account.clerk_user_id == clerk_user_id,
                Account.is_active == True
            ).all()

            portfolio_data = []
            total_value = 0
            total_cost_basis = 0

            for account in accounts:
                # Calculate account value and update balance
                account_value = 0
                account_cost = 0

                # Build complete asset data for frontend
                asset_data = []
                for asset in account.assets:
                    if not asset.is_active:
                        continue

                    current_value = asset.shares * (asset.current_price or asset.avg_cost)
                    total_cost = asset.shares * asset.avg_cost
                    pnl = current_value - total_cost
                    pnl_percent = (pnl / total_cost * 100) if total_cost > 0 else 0

                    asset_info = {
                        "id": asset.id,
                        "symbol": asset.symbol,
                        "name": asset.name,
                        "shares": float(asset.shares),
                        "avg_cost": float(asset.avg_cost),
                        "current_price": float(asset.current_price or asset.avg_cost),
                        "value": float(current_value),
                        "cost_basis": float(total_cost),
                        "pnl": float(pnl),
                        "pnl_percent": float(pnl_percent),
                        "day_change": float(asset.day_change or 0),
                        "day_change_percent": float(asset.day_change_percent or 0),
                        "asset_type": asset.asset_type,
                        "sector": asset.sector,
                        "last_updated": asset.last_updated.isoformat() if asset.last_updated else None,
                        "price_updated_at": asset.price_updated_at.isoformat() if asset.price_updated_at else None
                    }
                    asset_data.append(asset_info)

                    account_value += current_value
                    account_cost += total_cost

                # Update account balance
                account.balance = account_value

                portfolio_data.append({
                    "id": account.id,
                    "name": account.name,
                    "account_type": account.account_type,
                    "description": account.description,
                    "balance": float(account_value),
                    "cost_basis": float(account_cost),
                    "pnl": float(account_value - account_cost),
                    "pnl_percent": float((account_value - account_cost) / account_cost * 100) if account_cost > 0 else 0,
                    "currency": account.currency,
                    "created_at": account.created_at.isoformat() if account.created_at else None,
                    "assets": asset_data
                })

                total_value += account_value
                total_cost_basis += account_cost

            self.db.commit()  # Save updated balances

            # Get lightweight AI analysis (async)
            try:
                ai_analysis = await self.ai_service.analyze_portfolio_fast(portfolio_data)
                logging.info("🤖 AI analysis completed successfully")
            except Exception as e:
                logging.error(f"AI analysis failed: {e}")
                ai_analysis = self._get_fallback_analysis(portfolio_data, total_value, total_cost_basis)
                logging.info("⚠️  Using fallback analysis due to AI service error")

            # Calculate portfolio-level metrics
            total_assets = sum(len(account["assets"]) for account in portfolio_data)
            total_pnl = total_value - total_cost_basis
            total_pnl_percent = (total_pnl / total_cost_basis * 100) if total_cost_basis > 0 else 0

            # Create portfolio snapshot
            await self._create_portfolio_snapshot(clerk_user_id, {
                "total_value": total_value,
                "total_cost_basis": total_cost_basis,
                "total_pnl": total_pnl,
                "total_pnl_percent": total_pnl_percent,
                "asset_count": total_assets,
                "account_count": len(portfolio_data)
            })

            return {
                "user_id": clerk_user_id,
                "accounts": portfolio_data,
                "summary": {
                    "total_value": float(total_value),
                    "total_cost_basis": float(total_cost_basis),
                    "total_pnl": float(total_pnl),
                    "total_pnl_percent": float(total_pnl_percent),
                    "total_accounts": len(portfolio_data),
                    "total_assets": total_assets
                },
                "analysis": ai_analysis,
                "last_updated": datetime.utcnow().isoformat(),
                "status": "success"
            }

        except Exception as e:
            logging.error(f"Failed to get portfolio summary: {e}")
            raise

    def _update_account_balances(self, clerk_user_id: str):
        """Update account balances for user"""
        accounts = self.db.query(Account).filter(
            Account.clerk_user_id == clerk_user_id,
            Account.is_active == True
        ).all()

        for account in accounts:
            account.balance = sum(
                asset.shares * (asset.current_price or asset.avg_cost)
                for asset in account.assets
                if asset.is_active
            )

    async def _create_portfolio_snapshot(self, clerk_user_id: str, data: Dict = None):
        """Create portfolio snapshot for performance tracking"""
        try:
            if not data:
                # Calculate snapshot data
                accounts = self.db.query(Account).filter(
                    Account.clerk_user_id == clerk_user_id,
                    Account.is_active == True
                ).all()

                total_value = sum(account.balance for account in accounts)
                total_assets = sum(len(account.assets) for account in accounts)

                data = {
                    "total_value": total_value,
                    "total_cost_basis": 0,  # Would need to calculate
                    "total_pnl": 0,
                    "total_pnl_percent": 0,
                    "asset_count": total_assets,
                    "account_count": len(accounts)
                }

            # Check if snapshot already exists for today
            today = datetime.utcnow().date()
            existing_snapshot = self.db.query(PortfolioSnapshot).filter(
                PortfolioSnapshot.clerk_user_id == clerk_user_id,
                PortfolioSnapshot.snapshot_type == "daily",
                PortfolioSnapshot.created_at >= datetime.combine(today, datetime.min.time())
            ).first()

            if existing_snapshot:
                # Update existing snapshot
                for key, value in data.items():
                    if hasattr(existing_snapshot, key):
                        setattr(existing_snapshot, key, value)
            else:
                # Create new snapshot
                snapshot = PortfolioSnapshot(
                    clerk_user_id=clerk_user_id,
                    total_value=data["total_value"],
                    total_cost_basis=data["total_cost_basis"],
                    total_pnl=data["total_pnl"],
                    total_pnl_percent=data["total_pnl_percent"],
                    asset_count=data["asset_count"],
                    account_count=data["account_count"],
                    snapshot_type="daily"
                )
                self.db.add(snapshot)
                self.db.commit()

        except Exception as e:
            logging.warning(f"Failed to create portfolio snapshot: {e}")

    async def _get_or_fetch_market_data(self, symbol: str) -> Optional[MarketData]:
        """Get market data from cache or fetch from API"""
        try:
            # Check cache first
            cached_data = self.db.query(MarketData).filter(
                MarketData.symbol == symbol.upper()
            ).first()

            if cached_data and not cached_data.is_stale:
                return cached_data

            # Fetch new data
            prices = self.market_data.get_current_prices([symbol])
            if symbol in prices and prices[symbol] > 0:
                if cached_data:
                    # Update existing
                    cached_data.current_price = prices[symbol]
                    cached_data.updated_at = datetime.utcnow()
                    return cached_data
                else:
                    # Create new
                    market_data = MarketData(
                        symbol=symbol.upper(),
                        current_price=prices[symbol],
                        asset_type=self._determine_asset_type(symbol)
                    )
                    self.db.add(market_data)
                    return market_data

            return None

        except Exception as e:
            logging.warning(f"Failed to get market data for {symbol}: {e}")
            return None

    def _determine_asset_type(self, symbol: str) -> str:
        """Determine asset type from symbol"""
        symbol = symbol.upper()

        if "-USD" in symbol or symbol.endswith("USDT"):
            return "crypto"
        elif symbol in ["SPY", "QQQ", "VTI", "IWM", "DIA"]:
            return "etf"
        elif len(symbol) <= 4 and symbol.isalpha():
            return "stock"
        else:
            return "other"

    def _get_fallback_analysis(self, portfolio_data: List[Dict], total_value: float, total_cost_basis: float) -> Dict:
        """Fallback analysis if enhanced AI fails"""
        num_assets = sum(len(account.get('assets', [])) for account in portfolio_data)
        diversity_score = min(num_assets / 10, 1.0)

        total_pnl = total_value - total_cost_basis
        total_pnl_percent = (total_pnl / total_cost_basis * 100) if total_cost_basis > 0 else 0

        return {
            "total_value": total_value,
            "total_pnl": total_pnl,
            "total_pnl_percent": total_pnl_percent,
            "diversity_score": diversity_score,
            "risk_score": (1 - diversity_score) * 5,
            "sentiment_score": 0.0,
            "technical_score": 0.0,
            "recommendation": "HOLD" if diversity_score > 0.5 else "DIVERSIFY",
            "confidence": 0.6,
            "insights": [
                f"Portfolio spans {len(portfolio_data)} accounts",
                f"Total of {num_assets} different assets",
                f"Diversity score: {diversity_score:.1%}",
                f"Total P&L: {'+' if total_pnl >= 0 else ''}${total_pnl:,.2f} ({total_pnl_percent:+.1f}%)",
                "Basic analysis - upgrade for enhanced AI features"
            ],
            "analysis_type": "basic"
        }

    async def get_enhanced_asset_analysis(self, symbol: str) -> Dict:
        """Get detailed analysis for a specific asset"""
        try:
            analysis = await self.ai_service.analyze_asset_fast(symbol)
            return analysis
        except Exception as e:
            logging.error(f"Asset analysis failed for {symbol}: {e}")
            return {
                "symbol": symbol,
                "error": "Analysis temporarily unavailable",
                "fallback_recommendation": "HOLD"
            }

    def _validate_symbol_format(self, symbol: str) -> str:
        """Simple symbol validation and normalization"""
        if not symbol or not symbol.strip():
            raise ValueError("Symbol cannot be empty")

        symbol = symbol.strip().upper()

        # Basic length check
        if len(symbol) > 10:
            raise ValueError("Symbol too long (maximum 10 characters)")

        return symbol

    def _validate_asset_data(self, asset_data):
        """Basic asset data validation"""
        # Additional validation beyond Pydantic
        if asset_data.shares > 1000000:  # Reasonable upper limit
            raise ValueError("Share quantity exceeds reasonable limit (1,000,000)")

        if asset_data.avg_cost > 100000:  # $100k per share limit
            raise ValueError("Average cost exceeds reasonable limit ($100,000)")
