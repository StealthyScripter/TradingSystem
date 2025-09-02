"""
Financial calculations and performance metrics tests
Tests all financial calculations for accuracy and edge cases
"""

import pytest
import math
from typing import List
from datetime import datetime, timedelta

from app.services.perfomance import (
    PerformanceCalculator, 
    PortfolioHolding,
    PerformanceService
)
from app.models.portfolio import Account, Asset
from conftest import skip_if_production


class TestPerformanceCalculator:
    """Test performance calculation methods"""

    @pytest.fixture
    def calculator(self):
        """Create performance calculator instance"""
        return PerformanceCalculator()

    @pytest.fixture 
    def sample_holdings(self):
        """Create sample portfolio holdings for testing"""
        return [
            PortfolioHolding(
                symbol="AAPL",
                quantity=100,
                purchase_price=150.0,
                current_price=160.0,
                purchase_date="2024-01-01"
            ),
            PortfolioHolding(
                symbol="MSFT",
                quantity=50,
                purchase_price=300.0,
                current_price=320.0,
                purchase_date="2024-02-01"
            ),
            PortfolioHolding(
                symbol="GOOGL",
                quantity=25,
                purchase_price=100.0,
                current_price=95.0,
                purchase_date="2024-03-01"
            )
        ]

    def test_calculate_total_return(self, calculator, sample_holdings):
        """Test total return calculation"""
        initial_investment = 32500.0  # (100*150) + (50*300) + (25*100)
        
        total_return = calculator.calculate_total_return(sample_holdings, initial_investment)
        
        # Current value: (100*160) + (50*320) + (25*95) = 16000 + 16000 + 2375 = 34375
        # Return: (34375 - 32500) / 32500 * 100 = 5.77%
        expected_return = ((34375 - 32500) / 32500) * 100
        assert abs(total_return - expected_return) < 0.01

    def test_calculate_total_return_zero_investment(self, calculator, sample_holdings):
        """Test total return with zero initial investment"""
        total_return = calculator.calculate_total_return(sample_holdings, 0)
        assert total_return == 0.0

    def test_calculate_total_return_negative_investment(self, calculator, sample_holdings):
        """Test total return with negative initial investment"""
        total_return = calculator.calculate_total_return(sample_holdings, -1000)
        assert total_return == 0.0

    def test_calculate_annualized_return(self, calculator):
        """Test annualized return calculation"""
        # 20% return over 2 years should be about 9.54% annualized
        annualized = calculator.calculate_annualized_return(20.0, 730)  # 2 years
        expected = (pow(1.20, 1/2) - 1) * 100
        assert abs(annualized - expected) < 0.01

    def test_calculate_annualized_return_zero_days(self, calculator):
        """Test annualized return with zero days"""
        result = calculator.calculate_annualized_return(10.0, 0)
        assert result == 0.0

    def test_calculate_annualized_return_negative_days(self, calculator):
        """Test annualized return with negative days"""
        result = calculator.calculate_annualized_return(10.0, -100)
        assert result == 0.0

    def test_calculate_portfolio_returns(self, calculator):
        """Test portfolio returns calculation from price history"""
        price_history = [100, 105, 102, 108, 110]
        returns = calculator.calculate_portfolio_returns(price_history)
        
        expected_returns = [0.05, -0.0286, 0.0588, 0.0185]  # Approximate
        assert len(returns) == 4
        for i, ret in enumerate(returns):
            assert abs(ret - expected_returns[i]) < 0.01

    def test_calculate_portfolio_returns_empty_list(self, calculator):
        """Test portfolio returns with empty price history"""
        returns = calculator.calculate_portfolio_returns([])
        assert returns == []

    def test_calculate_portfolio_returns_single_price(self, calculator):
        """Test portfolio returns with single price"""
        returns = calculator.calculate_portfolio_returns([100])
        assert returns == []

    def test_calculate_volatility(self, calculator):
        """Test volatility calculation"""
        returns = [0.01, -0.02, 0.03, -0.01, 0.02]
        volatility = calculator.calculate_volatility(returns)
        
        # Should be around 2.8% annualized
        assert volatility > 0
        assert volatility < 10  # Reasonable range

    def test_calculate_volatility_insufficient_data(self, calculator):
        """Test volatility with insufficient data"""
        volatility = calculator.calculate_volatility([0.01])
        assert volatility == 0.0

    def test_calculate_sharpe_ratio(self, calculator):
        """Test Sharpe ratio calculation"""
        # Returns with positive average
        returns = [0.02, 0.01, 0.03, -0.01, 0.02]
        sharpe = calculator.calculate_sharpe_ratio(returns, risk_free_rate=0.02)
        
        # Should be positive with good returns
        assert isinstance(sharpe, float)
        assert abs(sharpe) < 10  # Reasonable range

    def test_calculate_sharpe_ratio_zero_volatility(self, calculator):
        """Test Sharpe ratio with zero volatility"""
        returns = [0.01] * 10  # Same return every period
        sharpe = calculator.calculate_sharpe_ratio(returns)
        assert sharpe == 0.0

    def test_calculate_sharpe_ratio_insufficient_data(self, calculator):
        """Test Sharpe ratio with insufficient data"""
        sharpe = calculator.calculate_sharpe_ratio([0.01])
        assert sharpe == 0.0

    def test_calculate_sortino_ratio(self, calculator):
        """Test Sortino ratio calculation"""
        returns = [0.05, -0.02, 0.03, -0.04, 0.01]
        sortino = calculator.calculate_sortino_ratio(returns)
        
        assert isinstance(sortino, float)
        # Sortino should typically be higher than Sharpe for same data

    def test_calculate_sortino_ratio_no_downside(self, calculator):
        """Test Sortino ratio with no downside returns"""
        returns = [0.01, 0.02, 0.03, 0.01, 0.02]  # All positive
        sortino = calculator.calculate_sortino_ratio(returns)
        assert sortino == 0.0

    def test_calculate_max_drawdown(self, calculator):
        """Test maximum drawdown calculation"""
        price_history = [100, 110, 105, 95, 105, 115]
        max_dd = calculator.calculate_max_drawdown(price_history)
        
        # Max drawdown should be from 110 to 95 = -13.64%
        expected_dd = (95 - 110) / 110 * 100
        assert abs(max_dd - expected_dd) < 0.01

    def test_calculate_max_drawdown_no_drawdown(self, calculator):
        """Test max drawdown with only increasing prices"""
        price_history = [100, 105, 110, 115, 120]
        max_dd = calculator.calculate_max_drawdown(price_history)
        assert max_dd == 0.0

    def test_calculate_max_drawdown_insufficient_data(self, calculator):
        """Test max drawdown with insufficient data"""
        max_dd = calculator.calculate_max_drawdown([100])
        assert max_dd == 0.0

    def test_calculate_beta(self, calculator):
        """Test beta calculation"""
        portfolio_returns = [0.02, -0.01, 0.03, -0.02, 0.01]
        benchmark_returns = [0.015, -0.005, 0.025, -0.015, 0.008]
        
        beta = calculator.calculate_beta(portfolio_returns, benchmark_returns)
        
        # Beta should be positive correlation
        assert isinstance(beta, float)
        assert 0.5 < beta < 2.0  # Reasonable range

    def test_calculate_beta_zero_benchmark_variance(self, calculator):
        """Test beta with zero benchmark variance"""
        portfolio_returns = [0.02, -0.01, 0.03]
        benchmark_returns = [0.01, 0.01, 0.01]  # No variance
        
        beta = calculator.calculate_beta(portfolio_returns, benchmark_returns)
        assert beta == 1.0

    def test_calculate_beta_mismatched_lengths(self, calculator):
        """Test beta with mismatched return lengths"""
        portfolio_returns = [0.02, -0.01]
        benchmark_returns = [0.015, -0.005, 0.025]
        
        beta = calculator.calculate_beta(portfolio_returns, benchmark_returns)
        assert beta == 1.0

    def test_calculate_alpha(self, calculator):
        """Test alpha calculation"""
        portfolio_returns = [0.03, 0.01, 0.04, -0.01, 0.02]
        benchmark_returns = [0.02, 0.005, 0.03, -0.005, 0.015]
        beta = 1.2
        
        alpha = calculator.calculate_alpha(portfolio_returns, benchmark_returns, beta, 0.02)
        
        assert isinstance(alpha, float)
        # Alpha can be positive or negative

    def test_calculate_alpha_insufficient_data(self, calculator):
        """Test alpha with insufficient data"""
        alpha = calculator.calculate_alpha([0.01], [0.01], 1.0)
        assert alpha == 0.0

    def test_calculate_var(self, calculator):
        """Test Value at Risk calculation"""
        returns = [-0.05, -0.02, 0.01, 0.03, -0.01, 0.02, -0.03, 0.04, -0.02, 0.01]
        portfolio_value = 100000
        
        var = calculator.calculate_var(returns, confidence_level=0.05, portfolio_value=portfolio_value)
        
        # VaR should be negative (representing loss)
        assert var < 0
        assert var > -portfolio_value  # Can't lose more than total value

    def test_calculate_var_insufficient_data(self, calculator):
        """Test VaR with insufficient data"""
        var = calculator.calculate_var([0.01], portfolio_value=100000)
        assert var == 0.0

    def test_compare_to_benchmarks(self, calculator):
        """Test benchmark comparison"""
        portfolio_returns = [0.02, 0.01, 0.03, -0.01, 0.02]
        
        comparisons = calculator.compare_to_benchmarks(portfolio_returns)
        
        assert isinstance(comparisons, dict)
        assert len(comparisons) > 0
        
        for benchmark, performance in comparisons.items():
            assert isinstance(performance, float)

    def test_compare_to_benchmarks_insufficient_data(self, calculator):
        """Test benchmark comparison with insufficient data"""
        comparisons = calculator.compare_to_benchmarks([0.01])
        
        assert isinstance(comparisons, dict)
        for value in comparisons.values():
            assert value == 0.0


class TestPortfolioHolding:
    """Test PortfolioHolding dataclass"""

    def test_portfolio_holding_creation(self):
        """Test creating portfolio holding"""
        holding = PortfolioHolding(
            symbol="AAPL",
            quantity=100,
            purchase_price=150.0,
            current_price=160.0,
            purchase_date="2024-01-01"
        )
        
        assert holding.symbol == "AAPL"
        assert holding.quantity == 100
        assert holding.purchase_price == 150.0
        assert holding.current_price == 160.0

    def test_portfolio_holding_calculations(self):
        """Test implicit calculations in portfolio holding"""
        holding = PortfolioHolding(
            symbol="TEST",
            quantity=50,
            purchase_price=100.0,
            current_price=110.0,
            purchase_date="2024-01-01"
        )
        
        # These would be calculated in the service
        market_value = holding.quantity * holding.current_price
        cost_basis = holding.quantity * holding.purchase_price
        pnl = market_value - cost_basis
        
        assert market_value == 5500.0
        assert cost_basis == 5000.0
        assert pnl == 500.0


class TestPerformanceService:
    """Test PerformanceService integration"""

    def test_generate_mock_price_history(self, portfolio_service):
        """Test mock price history generation"""
        start_value = 10000.0
        end_value = 12000.0
        days = 365
        
        price_history = portfolio_service._generate_mock_price_history(start_value, end_value, days)
        
        assert len(price_history) == days
        assert price_history[0] == start_value
        assert price_history[-1] == end_value
        assert all(price > 0 for price in price_history)

    def test_estimate_expense_ratio(self, portfolio_service):
        """Test expense ratio estimation"""
        holdings = [
            PortfolioHolding("AAPL", 100, 150.0, 160.0, "2024-01-01"),  # Stock
            PortfolioHolding("SPY", 50, 400.0, 420.0, "2024-01-01"),    # ETF
            PortfolioHolding("BTC-USD", 1, 40000.0, 45000.0, "2024-01-01")  # Crypto
        ]
        
        expense_ratio = portfolio_service._estimate_expense_ratio(holdings)
        
        assert isinstance(expense_ratio, float)
        assert 0.0 <= expense_ratio <= 2.0  # Reasonable range

    def test_estimate_expense_ratio_empty_holdings(self, portfolio_service):
        """Test expense ratio with empty holdings"""
        expense_ratio = portfolio_service._estimate_expense_ratio([])
        assert expense_ratio == 0.5  # Default value


class TestFinancialEdgeCases:
    """Test edge cases in financial calculations"""

    @pytest.fixture
    def calculator(self):
        return PerformanceCalculator()

    def test_extreme_negative_returns(self, calculator):
        """Test calculations with extreme negative returns"""
        returns = [-0.5, -0.3, -0.2, -0.1, 0.1]  # Severe losses
        
        volatility = calculator.calculate_volatility(returns)
        sharpe = calculator.calculate_sharpe_ratio(returns)
        
        assert volatility > 0
        assert sharpe < 0  # Should be negative with bad returns

    def test_extreme_positive_returns(self, calculator):
        """Test calculations with extreme positive returns"""
        returns = [0.5, 0.3, 0.2, 0.4, 0.1]  # Extreme gains
        
        volatility = calculator.calculate_volatility(returns)
        sharpe = calculator.calculate_sharpe_ratio(returns)
        
        assert volatility > 0
        assert sharpe > 0  # Should be positive with good returns

    def test_mixed_extreme_returns(self, calculator):
        """Test calculations with mixed extreme returns"""
        returns = [0.8, -0.6, 0.4, -0.3, 0.2]  # High volatility
        
        volatility = calculator.calculate_volatility(returns)
        max_dd = calculator.calculate_max_drawdown([100, 180, 72, 101, 71, 86])
        
        assert volatility > 20  # High volatility
        assert max_dd < -50     # Significant drawdown

    def test_zero_returns(self, calculator):
        """Test calculations with all zero returns"""
        returns = [0.0] * 10
        
        volatility = calculator.calculate_volatility(returns)
        sharpe = calculator.calculate_sharpe_ratio(returns)
        
        assert volatility == 0.0
        assert sharpe == 0.0

    def test_infinite_and_nan_handling(self, calculator):
        """Test handling of infinite and NaN values"""
        # Test with very small numbers that might cause division issues
        returns = [1e-10, -1e-10, 1e-15, -1e-15]
        
        volatility = calculator.calculate_volatility(returns)
        sharpe = calculator.calculate_sharpe_ratio(returns)
        
        assert not math.isnan(volatility)
        assert not math.isinf(volatility)
        assert not math.isnan(sharpe)
        assert not math.isinf(sharpe)

    def test_rounding_precision(self, calculator):
        """Test rounding precision in calculations"""
        # Test with numbers that might have precision issues
        returns = [0.123456789, -0.987654321, 0.555555555]
        
        volatility = calculator.calculate_volatility(returns)
        
        # Should be properly rounded
        assert volatility == round(volatility, 2)

    def test_large_portfolio_values(self, calculator):
        """Test calculations with very large portfolio values"""
        large_holdings = [
            PortfolioHolding("MEGA", 1000000, 1000.0, 1100.0, "2024-01-01")
        ]
        
        total_return = calculator.calculate_total_return(large_holdings, 1000000000.0)
        
        # Should handle large numbers correctly
        assert total_return == 10.0  # 10% return

    def test_fractional_shares(self, calculator):
        """Test calculations with fractional shares"""
        fractional_holdings = [
            PortfolioHolding("FRAC", 0.123, 100.0, 110.0, "2024-01-01"),
            PortfolioHolding("MICRO", 0.000001, 1000000.0, 1100000.0, "2024-01-01")
        ]
        
        total_return = calculator.calculate_total_return(fractional_holdings, 1.123)
        
        # Should handle fractional shares
        assert isinstance(total_return, float)

    def test_cryptocurrency_volatility(self, calculator):
        """Test calculations with cryptocurrency-like volatility"""
        # Simulate crypto price movements
        crypto_prices = [40000, 45000, 35000, 50000, 30000, 55000, 25000]
        returns = calculator.calculate_portfolio_returns(crypto_prices)
        
        volatility = calculator.calculate_volatility(returns)
        max_dd = calculator.calculate_max_drawdown(crypto_prices)
        
        # Should handle high volatility
        assert volatility > 50  # Very high volatility
        assert max_dd < -40     # Significant drawdown


class TestPerformanceValidation:
    """Test performance calculation validation against known results"""

    @pytest.fixture
    def calculator(self):
        return PerformanceCalculator()

    def test_simple_return_validation(self, calculator):
        """Test simple return calculation with known result"""
        # $10,000 becomes $11,000 = 10% return
        holdings = [
            PortfolioHolding("TEST", 100, 100.0, 110.0, "2024-01-01")
        ]
        
        total_return = calculator.calculate_total_return(holdings, 10000.0)
        assert abs(total_return - 10.0) < 0.01

    def test_compound_return_validation(self, calculator):
        """Test compound return calculation"""
        # 20% return over 2 years = ~9.54% annualized
        annualized = calculator.calculate_annualized_return(20.0, 730)
        expected = (math.pow(1.20, 1/2) - 1) * 100
        assert abs(annualized - expected) < 0.01

    def test_sharpe_ratio_validation(self, calculator):
        """Test Sharpe ratio with known data"""
        # Portfolio with 12% return, 15% volatility, 2% risk-free rate
        # Should have Sharpe ratio of (12-2)/15 = 0.67
        
        # Create returns that average to 12% annually with 15% volatility
        daily_return = 0.12 / 252  # Daily return for 12% annual
        returns = [daily_return] * 252  # Simplified for testing
        
        # This is a simplified test - actual Sharpe would need proper volatility
        sharpe = calculator.calculate_sharpe_ratio(returns, risk_free_rate=0.02)
        
        # Should be positive for good risk-adjusted returns
        assert sharpe > 0

    def test_max_drawdown_validation(self, calculator):
        """Test max drawdown with known scenario"""
        # Portfolio goes from 100 to 120 to 80 to 100
        # Max drawdown should be (80-120)/120 = -33.33%
        prices = [100, 120, 80, 100]
        max_dd = calculator.calculate_max_drawdown(prices)
        
        expected_dd = (80 - 120) / 120 * 100
        assert abs(max_dd - expected_dd) < 0.01

    def test_beta_validation(self, calculator):
        """Test beta calculation with known relationship"""
        # Portfolio that moves 1.5x the benchmark
        benchmark_returns = [0.01, -0.01, 0.02, -0.015, 0.005]
        portfolio_returns = [r * 1.5 for r in benchmark_returns]
        
        beta = calculator.calculate_beta(portfolio_returns, benchmark_returns)
        
        # Should be approximately 1.5
        assert abs(beta - 1.5) < 0.1


@pytest.mark.slow
class TestPerformanceStress:
    """Stress test performance calculations"""

    @pytest.fixture
    def calculator(self):
        return PerformanceCalculator()

    def test_large_dataset_performance(self, calculator):
        """Test performance with large datasets"""
        # Create large return series
        large_returns = [0.01 * (i % 20 - 10) / 10 for i in range(10000)]
        
        import time
        start_time = time.time()
        
        volatility = calculator.calculate_volatility(large_returns)
        sharpe = calculator.calculate_sharpe_ratio(large_returns)
        
        calculation_time = time.time() - start_time
        
        # Should complete quickly even with large dataset
        assert calculation_time < 1.0
        assert isinstance(volatility, float)
        assert isinstance(sharpe, float)

    @skip_if_production("Resource intensive test")
    def test_memory_usage_large_portfolio(self, calculator):
        """Test memory usage with large portfolio"""
        # Create large portfolio
        large_holdings = []
        for i in range(1000):
            holding = PortfolioHolding(
                symbol=f"STOCK{i}",
                quantity=100,
                purchase_price=100.0,
                current_price=100.0 + (i % 20),
                purchase_date="2024-01-01"
            )
            large_holdings.append(holding)
        
        total_return = calculator.calculate_total_return(large_holdings, 10000000.0)
        
        # Should handle large portfolios
        assert isinstance(total_return, float)
        assert not math.isnan(total_return)
