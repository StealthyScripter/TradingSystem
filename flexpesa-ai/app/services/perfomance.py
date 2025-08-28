import math
import statistics
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session
import numpy as np
import pandas as pd

from app.models.portfolio import Account, Asset
from app.services.market_data import MarketDataService

# Performance calculation classes
class PortfolioHolding:
    def __init__(self, symbol: str, quantity: float, purchase_price: float,
                 current_price: float, purchase_date: str):
        self.symbol = symbol
        self.quantity = quantity
        self.purchase_price = purchase_price
        self.current_price = current_price
        self.purchase_date = purchase_date

class PerformanceCalculator:
    def __init__(self):
        # Mock benchmark data (daily returns for past year)
        self.benchmarks = {
            "S&P 500": self._generate_benchmark_returns(0.001, 0.015),
            "NASDAQ 100": self._generate_benchmark_returns(0.002, 0.018),
            "Total Stock Market": self._generate_benchmark_returns(0.0008, 0.012),
            "60/40 Portfolio": self._generate_benchmark_returns(0.0005, 0.008)
        }

        # Risk-free rate (10-year Treasury)
        self.risk_free_rate = 0.045  # 4.5%

    def _generate_benchmark_returns(self, base_return: float, volatility: float, days: int = 365) -> List[float]:
        """Generate realistic benchmark returns using random walk"""
        import random
        returns = []
        for _ in range(days):
            # Generate daily return with some randomness
            daily_return = random.normalvariate(base_return, volatility)
            returns.append(daily_return)
        return returns

    def calculate_total_return(self, holdings: List[PortfolioHolding],
                             initial_investment: float) -> float:
        """Calculate total return percentage"""
        if initial_investment <= 0:
            return 0.0

        current_value = sum(holding.quantity * holding.current_price for holding in holdings)
        total_return = ((current_value - initial_investment) / initial_investment) * 100
        return round(total_return, 2)

    def calculate_annualized_return(self, total_return: float, days_held: int) -> float:
        """Calculate annualized return"""
        if days_held <= 0:
            return 0.0

        years = days_held / 365.25
        if years <= 0:
            return 0.0

        annualized = (pow(1 + (total_return / 100), 1 / years) - 1) * 100
        return round(annualized, 2)

    def calculate_portfolio_returns(self, price_history: List[float]) -> List[float]:
        """Calculate daily returns from price history"""
        if len(price_history) < 2:
            return []

        returns = []
        for i in range(1, len(price_history)):
            if price_history[i-1] != 0:
                daily_return = (price_history[i] - price_history[i-1]) / price_history[i-1]
                returns.append(daily_return)
        return returns

    def calculate_volatility(self, returns: List[float]) -> float:
        """Calculate annualized volatility (standard deviation)"""
        if len(returns) < 2:
            return 0.0

        std_dev = statistics.stdev(returns)
        # Annualize volatility (assuming daily returns)
        annualized_vol = std_dev * math.sqrt(252) * 100  # 252 trading days
        return round(annualized_vol, 2)

    def calculate_sharpe_ratio(self, returns: List[float], risk_free_rate: float = None) -> float:
        """Calculate Sharpe ratio"""
        if len(returns) < 2:
            return 0.0

        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate

        avg_return = statistics.mean(returns)
        volatility = statistics.stdev(returns)

        if volatility == 0:
            return 0.0

        # Convert to annualized
        excess_return = (avg_return * 252) - risk_free_rate
        annualized_volatility = volatility * math.sqrt(252)

        sharpe = excess_return / annualized_volatility
        return round(sharpe, 3)

    def calculate_sortino_ratio(self, returns: List[float], risk_free_rate: float = None) -> float:
        """Calculate Sortino ratio (downside deviation)"""
        if len(returns) < 2:
            return 0.0

        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate / 252  # Daily risk-free rate

        avg_return = statistics.mean(returns)
        downside_returns = [r for r in returns if r < risk_free_rate]

        if len(downside_returns) < 2:
            return 0.0

        downside_deviation = statistics.stdev(downside_returns) * math.sqrt(252)
        excess_return = (avg_return * 252) - self.risk_free_rate

        if downside_deviation == 0:
            return 0.0

        sortino = excess_return / downside_deviation
        return round(sortino, 3)

    def calculate_max_drawdown(self, price_history: List[float]) -> float:
        """Calculate maximum drawdown"""
        if len(price_history) < 2:
            return 0.0

        running_max = price_history[0]
        max_drawdown = 0.0

        for price in price_history:
            if price > running_max:
                running_max = price

            if running_max > 0:
                drawdown = (price - running_max) / running_max
                if drawdown < max_drawdown:
                    max_drawdown = drawdown

        return round(max_drawdown * 100, 2)

    def calculate_beta(self, portfolio_returns: List[float], benchmark_returns: List[float]) -> float:
        """Calculate beta relative to benchmark"""
        if len(portfolio_returns) != len(benchmark_returns) or len(portfolio_returns) < 2:
            return 1.0

        # Calculate covariance and variance
        portfolio_mean = statistics.mean(portfolio_returns)
        benchmark_mean = statistics.mean(benchmark_returns)

        covariance = sum((p - portfolio_mean) * (b - benchmark_mean)
                        for p, b in zip(portfolio_returns, benchmark_returns)) / len(portfolio_returns)

        benchmark_variance = statistics.variance(benchmark_returns)

        if benchmark_variance == 0:
            return 1.0

        beta = covariance / benchmark_variance
        return round(beta, 3)

    def calculate_alpha(self, portfolio_returns: List[float], benchmark_returns: List[float],
                       beta: float, risk_free_rate: float = None) -> float:
        """Calculate Jensen's Alpha"""
        if len(portfolio_returns) < 2:
            return 0.0

        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate / 252

        portfolio_return = statistics.mean(portfolio_returns) * 252
        benchmark_return = statistics.mean(benchmark_returns) * 252

        expected_return = risk_free_rate + beta * (benchmark_return - risk_free_rate)
        alpha = (portfolio_return - expected_return) * 100

        return round(alpha, 2)

    def calculate_var(self, returns: List[float], confidence_level: float = 0.05,
                     portfolio_value: float = 100000) -> float:
        """Calculate Value at Risk"""
        if len(returns) < 2:
            return 0.0

        # Sort returns in ascending order
        sorted_returns = sorted(returns)

        # Find the percentile
        index = int(confidence_level * len(sorted_returns))
        var_return = sorted_returns[index] if index < len(sorted_returns) else sorted_returns[0]

        # Convert to portfolio value
        var_amount = var_return * portfolio_value
        return round(var_amount, 0)

    def compare_to_benchmarks(self, portfolio_returns: List[float]) -> Dict[str, float]:
        """Compare portfolio performance to benchmarks"""
        if len(portfolio_returns) < 2:
            return {name: 0.0 for name in self.benchmarks.keys()}

        portfolio_annual_return = statistics.mean(portfolio_returns) * 252 * 100

        comparisons = {}
        for name, benchmark_returns in self.benchmarks.items():
            # Use subset of benchmark data to match portfolio length
            benchmark_subset = benchmark_returns[:len(portfolio_returns)]
            if benchmark_subset:
                benchmark_annual_return = statistics.mean(benchmark_subset) * 252 * 100
                outperformance = portfolio_annual_return - benchmark_annual_return
                comparisons[name] = round(outperformance, 2)
            else:
                comparisons[name] = 0.0

        return comparisons

class PerformanceService:
    """Enhanced performance service that integrates with existing Account/Asset models"""

    def __init__(self, db: Session):
        self.db = db
        self.calculator = PerformanceCalculator()
        self.market_data = MarketDataService()
        self.logger = logging.getLogger(__name__)

    async def get_all_portfolio_performance(self):
        """Get performance analysis for all portfolios (accounts)"""
        accounts = self.db.query(Account).all()
        performance_results = []

        for account in accounts:
            try:
                performance = await self._calculate_account_performance(account)
                performance_results.append(performance)
            except Exception as e:
                self.logger.error(f"Error calculating performance for account {account.id}: {e}")
                # Add a basic response for failed accounts
                performance_results.append(self._get_fallback_performance(account))

        return performance_results

    async def get_portfolio_summary(self):
        """Get summary statistics across all portfolios"""
        accounts = self.db.query(Account).all()

        if not accounts:
            return {
                "total_portfolios": 0,
                "total_value": 0.0,
                "average_return": 0.0,
                "average_sharpe_ratio": 0.0
            }

        total_value = 0.0
        total_return = 0.0
        total_sharpe = 0.0
        valid_accounts = 0

        for account in accounts:
            try:
                performance = await self._calculate_account_performance(account)
                total_value += performance.get("total_value", 0)
                total_return += performance.get("total_return", 0)
                total_sharpe += performance.get("sharpe_ratio", 0)
                valid_accounts += 1
            except Exception as e:
                self.logger.warning(f"Skipping account {account.id} in summary due to error: {e}")

        if valid_accounts == 0:
            return {
                "total_portfolios": len(accounts),
                "total_value": 0.0,
                "average_return": 0.0,
                "average_sharpe_ratio": 0.0
            }

        return {
            "total_portfolios": len(accounts),
            "total_value": total_value,
            "average_return": total_return / valid_accounts,
            "average_sharpe_ratio": total_sharpe / valid_accounts
        }

    async def get_portfolio_performance(self, account_id: str):
        """Get performance metrics for a specific portfolio (account)"""
        try:
            account_id_int = int(account_id)
        except ValueError:
            raise ValueError(f"Invalid account ID: {account_id}")

        account = self.db.query(Account).filter(Account.id == account_id_int).first()
        if not account:
            raise ValueError(f"Account not found: {account_id}")

        return await self._calculate_account_performance(account)

    async def _calculate_account_performance(self, account: Account) -> Dict[str, Any]:
        """Calculate performance metrics for a single account"""
        # Convert Account/Assets to PortfolioHolding objects
        holdings = []
        total_cost = 0.0

        for asset in account.assets:
            holding = PortfolioHolding(
                symbol=asset.symbol,
                quantity=asset.shares,
                purchase_price=asset.avg_cost,
                current_price=asset.current_price or asset.avg_cost,
                purchase_date=asset.last_updated.strftime("%Y-%m-%d") if asset.last_updated else "2024-01-01"
            )
            holdings.append(holding)
            total_cost += asset.shares * asset.avg_cost

        # Generate price history (mock for now - in production, store historical data)
        current_value = sum(h.quantity * h.current_price for h in holdings)
        price_history = self._generate_mock_price_history(total_cost, current_value)

        # Calculate performance metrics
        total_return = self.calculator.calculate_total_return(holdings, total_cost)

        # Calculate days held (use the oldest asset purchase date)
        if holdings:
            try:
                oldest_date = min(datetime.strptime(h.purchase_date, "%Y-%m-%d") for h in holdings)
                days_held = (datetime.now() - oldest_date).days
            except:
                days_held = 365  # Default to 1 year
        else:
            days_held = 365

        annualized_return = self.calculator.calculate_annualized_return(total_return, days_held)

        # Calculate returns series and risk metrics
        portfolio_returns = self.calculator.calculate_portfolio_returns(price_history)
        volatility = self.calculator.calculate_volatility(portfolio_returns)
        sharpe_ratio = self.calculator.calculate_sharpe_ratio(portfolio_returns)
        sortino_ratio = self.calculator.calculate_sortino_ratio(portfolio_returns)
        max_drawdown = self.calculator.calculate_max_drawdown(price_history)

        # Calculate beta and alpha (using S&P 500 as benchmark)
        sp500_returns = self.calculator.benchmarks["S&P 500"][:len(portfolio_returns)]
        beta = self.calculator.calculate_beta(portfolio_returns, sp500_returns)
        alpha = self.calculator.calculate_alpha(portfolio_returns, sp500_returns, beta)

        # Calculate VaR
        var = self.calculator.calculate_var(portfolio_returns, portfolio_value=current_value)

        # Benchmark comparisons
        benchmark_comparisons = self.calculator.compare_to_benchmarks(portfolio_returns)

        # Estimate expense ratio based on asset types (simple heuristic)
        expense_ratio = self._estimate_expense_ratio(holdings)

        return {
            "id": str(account.id),
            "name": account.name,
            "type": account.account_type,
            "total_return": total_return,
            "annualized_return": annualized_return,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "total_value": current_value,
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "benchmark_comparisons": [
                {"name": name, "performance": performance}
                for name, performance in benchmark_comparisons.items()
            ],
            "risk_metrics": {
                "beta": beta,
                "volatility": volatility,
                "alpha": alpha,
                "expense_ratio": expense_ratio,
                "sortino_ratio": sortino_ratio,
                "value_at_risk": var
            }
        }

    def _generate_mock_price_history(self, start_value: float, end_value: float,
                                   days: int = 365) -> List[float]:
        """Generate mock price history for performance calculations"""
        if days <= 1:
            return [start_value, end_value]

        # Calculate the daily growth rate needed
        if start_value <= 0:
            start_value = 10000  # Default starting value

        growth_rate = (end_value / start_value) ** (1 / days) - 1

        prices = [start_value]
        current_price = start_value

        # Add some volatility to make it realistic
        import random
        for i in range(1, days):
            # Add random volatility around the trend
            volatility = random.normalvariate(0, 0.02)  # 2% daily volatility
            daily_return = growth_rate + volatility
            current_price *= (1 + daily_return)
            prices.append(max(current_price, 0.01))  # Ensure positive prices

        # Ensure the last price matches the target
        prices[-1] = end_value

        return prices

    def _estimate_expense_ratio(self, holdings: List[PortfolioHolding]) -> float:
        """Estimate expense ratio based on holdings (simple heuristic)"""
        if not holdings:
            return 0.5

        total_expense = 0.0
        total_weight = 0.0

        # Simple expense ratio estimates based on asset types
        expense_estimates = {
            "ETF": 0.2,    # Low-cost ETFs
            "INDEX": 0.1,  # Index funds
            "STOCK": 0.0,  # Individual stocks
            "CRYPTO": 0.5, # Crypto has higher fees
            "MUTUAL": 0.8  # Actively managed mutual funds
        }

        for holding in holdings:
            weight = holding.quantity * holding.current_price
            total_weight += weight

            # Categorize asset type based on symbol
            if holding.symbol.endswith("-USD"):
                asset_type = "CRYPTO"
            elif holding.symbol in ["SPY", "QQQ", "VTI", "IWM"]:
                asset_type = "ETF"
            elif len(holding.symbol) <= 4 and holding.symbol.isalpha():
                asset_type = "STOCK"
            else:
                asset_type = "ETF"  # Default

            expense = expense_estimates.get(asset_type, 0.5)
            total_expense += weight * expense

        if total_weight == 0:
            return 0.5

        weighted_expense = total_expense / total_weight
        return round(weighted_expense, 2)

    def _get_fallback_performance(self, account: Account) -> Dict[str, Any]:
        """Get basic fallback performance data when calculation fails"""
        current_value = sum(asset.shares * (asset.current_price or asset.avg_cost)
                          for asset in account.assets)

        return {
            "id": str(account.id),
            "name": account.name,
            "type": account.account_type,
            "total_return": 0.0,
            "annualized_return": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0,
            "total_value": current_value,
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "benchmark_comparisons": [
                {"name": "S&P 500", "performance": 0.0},
                {"name": "NASDAQ 100", "performance": 0.0},
                {"name": "Total Stock Market", "performance": 0.0},
                {"name": "60/40 Portfolio", "performance": 0.0}
            ],
            "risk_metrics": {
                "beta": 1.0,
                "volatility": 0.0,
                "alpha": 0.0,
                "expense_ratio": 0.5,
                "sortino_ratio": 0.0,
                "value_at_risk": 0.0
            }
        }

    # Additional methods for portfolio management
    async def create_portfolio_with_holdings(self, portfolio_data) -> Dict[str, Any]:
        """Create a new portfolio (account) with initial holdings"""
        # Create account
        account = Account(
            name=portfolio_data.name,
            account_type=portfolio_data.type,
            balance=0.0  # Will be calculated from assets
        )
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)

        # Add holdings as assets
        for holding in portfolio_data.holdings:
            asset = Asset(
                account_id=account.id,
                symbol=holding.symbol,
                shares=holding.quantity,
                avg_cost=holding.purchase_price,
                current_price=holding.purchase_price,  # Start with purchase price
                last_updated=datetime.strptime(holding.purchase_date, "%Y-%m-%d")
            )
            self.db.add(asset)

        self.db.commit()

        # Return performance data for new portfolio
        return await self._calculate_account_performance(account)

    async def update_portfolio(self, account_id: str, update_data) -> Dict[str, Any]:
        """Update portfolio and recalculate performance"""
        try:
            account_id_int = int(account_id)
        except ValueError:
            raise ValueError(f"Invalid account ID: {account_id}")

        account = self.db.query(Account).filter(Account.id == account_id_int).first()
        if not account:
            raise ValueError(f"Account not found: {account_id}")

        # Update account fields
        if update_data.name is not None:
            account.name = update_data.name
        if update_data.type is not None:
            account.account_type = update_data.type

        self.db.commit()

        return await self._calculate_account_performance(account)

    async def delete_portfolio(self, account_id: str):
        """Delete portfolio and all related data"""
        try:
            account_id_int = int(account_id)
        except ValueError:
            raise ValueError(f"Invalid account ID: {account_id}")

        account = self.db.query(Account).filter(Account.id == account_id_int).first()
        if not account:
            raise ValueError(f"Account not found: {account_id}")

        # Delete all assets first
        self.db.query(Asset).filter(Asset.account_id == account_id_int).delete()

        # Delete account
        self.db.delete(account)
        self.db.commit()

    async def get_portfolio_holdings(self, account_id: str):
        """Get detailed holdings with performance metrics"""
        try:
            account_id_int = int(account_id)
        except ValueError:
            raise ValueError(f"Invalid account ID: {account_id}")

        account = self.db.query(Account).filter(Account.id == account_id_int).first()
        if not account:
            raise ValueError(f"Account not found: {account_id}")

        holdings_response = []
        for asset in account.assets:
            market_value = asset.shares * (asset.current_price or asset.avg_cost)
            cost_basis = asset.shares * asset.avg_cost
            gain_loss = market_value - cost_basis
            gain_loss_percentage = (gain_loss / cost_basis) * 100 if cost_basis > 0 else 0

            holdings_response.append({
                "symbol": asset.symbol,
                "quantity": asset.shares,
                "purchase_price": asset.avg_cost,
                "current_price": asset.current_price or asset.avg_cost,
                "purchase_date": asset.last_updated.strftime("%Y-%m-%d") if asset.last_updated else "2024-01-01",
                "market_value": round(market_value, 2),
                "gain_loss": round(gain_loss, 2),
                "gain_loss_percentage": round(gain_loss_percentage, 2)
            })

        return holdings_response

    async def add_holdings_to_portfolio(self, account_id: str, holdings_data):
        """Add holdings to existing portfolio"""
        try:
            account_id_int = int(account_id)
        except ValueError:
            raise ValueError(f"Invalid account ID: {account_id}")

        account = self.db.query(Account).filter(Account.id == account_id_int).first()
        if not account:
            raise ValueError(f"Account not found: {account_id}")

        for holding in holdings_data:
            # Check if asset already exists
            existing_asset = self.db.query(Asset).filter(
                Asset.account_id == account_id_int,
                Asset.symbol == holding.symbol
            ).first()

            if existing_asset:
                # Update existing position (average cost)
                total_cost = (existing_asset.shares * existing_asset.avg_cost +
                            holding.quantity * holding.purchase_price)
                existing_asset.shares += holding.quantity
                existing_asset.avg_cost = total_cost / existing_asset.shares
            else:
                # Create new asset
                new_asset = Asset(
                    account_id=account_id_int,
                    symbol=holding.symbol,
                    shares=holding.quantity,
                    avg_cost=holding.purchase_price,
                    current_price=holding.purchase_price,
                    last_updated=datetime.strptime(holding.purchase_date, "%Y-%m-%d")
                )
                self.db.add(new_asset)

        self.db.commit()
        return {"message": "Holdings added successfully"}

    async def update_daily_data(self, account_id: str, daily_data):
        """Update daily price data for account holdings"""
        try:
            account_id_int = int(account_id)
        except ValueError:
            raise ValueError(f"Invalid account ID: {account_id}")

        account = self.db.query(Account).filter(Account.id == account_id_int).first()
        if not account:
            raise ValueError(f"Account not found: {account_id}")

        updated_assets = 0
        for asset in account.assets:
            if asset.symbol in daily_data.holdings_prices:
                asset.current_price = daily_data.holdings_prices[asset.symbol]
                asset.last_updated = datetime.strptime(daily_data.date, "%Y-%m-%d")
                updated_assets += 1

        # Update account balance
        account.balance = sum(asset.shares * (asset.current_price or asset.avg_cost)
                            for asset in account.assets)

        self.db.commit()
        return {"updated_assets": updated_assets}

    async def recalculate_performance(self, account_id: str):
        """Force recalculation of portfolio performance"""
        return await self.get_portfolio_performance(account_id)