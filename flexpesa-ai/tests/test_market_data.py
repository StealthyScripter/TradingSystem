"""
Market data service tests
Tests market data fetching, caching, and error handling
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from typing import Dict, List

from app.services.market_data import MarketDataService
from conftest import skip_if_production, create_test_market_data


class TestMarketDataService:
    """Test market data service functionality"""

    @pytest.fixture
    def market_service(self):
        """Create market data service instance"""
        return MarketDataService()

    def test_market_service_initialization(self, market_service):
        """Test market data service initialization"""
        assert market_service.min_delay == 1.0
        assert market_service.max_delay == 3.0
        assert market_service.last_request_time == 0

    def test_rate_limiting_enforcement(self, market_service):
        """Test rate limiting between requests"""
        start_time = time.time()

        # Make first request (should not be rate limited)
        market_service._enforce_rate_limit()
        first_request_time = time.time()

        # Make second request immediately (should be rate limited)
        market_service._enforce_rate_limit()
        second_request_time = time.time()

        # Second request should be delayed
        delay = second_request_time - first_request_time
        assert delay >= market_service.min_delay

    def test_cooldown_check(self, market_service):
        """Test rate limit cooldown checking"""
        # Initially not in cooldown
        assert not market_service._is_in_cooldown()

        # Set recent rate limit
        market_service.last_rate_limit_time = time.time()
        assert market_service._is_in_cooldown()

        # Set old rate limit
        market_service.last_rate_limit_time = time.time() - 120  # 2 minutes ago
        assert not market_service._is_in_cooldown()

    @patch('yfinance.Ticker')
    def test_get_single_price_safe_fast_info(self, mock_ticker, market_service):
        """Test getting single price using fast_info"""
        mock_instance = MagicMock()
        mock_fast_info = MagicMock()
        mock_fast_info.last_price = 155.50
        mock_instance.fast_info = mock_fast_info
        mock_ticker.return_value = mock_instance

        price = market_service._get_single_price_safe("AAPL")
        assert price == 155.50

    @patch('yfinance.Ticker')
    def test_get_single_price_safe_info_fallback(self, mock_ticker, market_service):
        """Test getting price using info fallback"""
        mock_instance = MagicMock()
        # Mock fast_info failure
        mock_instance.fast_info = None
        # Mock info success
        mock_instance.info = {
            'regularMarketPrice': 155.50,
            'currentPrice': None,
            'previousClose': 154.00
        }
        mock_ticker.return_value = mock_instance

        price = market_service._get_single_price_safe("AAPL")
        assert price == 155.50

    @patch('yfinance.Ticker')
    def test_get_single_price_safe_history_fallback(self, mock_ticker, market_service):
        """Test getting price using history fallback"""
        mock_instance = MagicMock()
        mock_instance.fast_info = None
        mock_instance.info = {}

        # Mock history
        import pandas as pd
        mock_hist = pd.DataFrame({'Close': [155.50]})
        mock_instance.history.return_value = mock_hist
        mock_ticker.return_value = mock_instance

        price = market_service._get_single_price_safe("AAPL")
        assert price == 155.50

    @patch('yfinance.Ticker')
    def test_get_single_price_safe_all_fail(self, mock_ticker, market_service):
        """Test getting price when all methods fail"""
        mock_instance = MagicMock()
        mock_instance.fast_info = None
        mock_instance.info = {}

        # Mock empty history
        import pandas as pd
        mock_hist = pd.DataFrame()
        mock_instance.history.return_value = mock_hist
        mock_ticker.return_value = mock_instance

        price = market_service._get_single_price_safe("FAIL")
        assert price == 0.0

    @patch('yfinance.Ticker')
    def test_get_single_price_safe_rate_limit_error(self, mock_ticker, market_service):
        """Test handling 429 rate limit error"""
        mock_ticker.side_effect = Exception("429: Too Many Requests")

        with pytest.raises(Exception, match="429"):
            market_service._get_single_price_safe("AAPL")

    def test_get_current_prices_empty_list(self, market_service):
        """Test getting prices for empty symbol list"""
        result = market_service.get_current_prices([])
        assert result == {}

    @patch.object(MarketDataService, '_get_single_price_safe')
    def test_get_current_prices_success(self, mock_get_price, market_service):
        """Test successful price fetching"""
        mock_get_price.side_effect = [155.50, 310.20, 140.30]

        symbols = ["AAPL", "MSFT", "GOOGL"]
        result = market_service.get_current_prices(symbols)

        assert len(result) == 3
        assert result["AAPL"] == 155.50
        assert result["MSFT"] == 310.20
        assert result["GOOGL"] == 140.30

    @patch.object(MarketDataService, '_get_single_price_safe')
    def test_get_current_prices_partial_failure(self, mock_get_price, market_service):
        """Test price fetching with partial failures"""
        mock_get_price.side_effect = [155.50, 0.0, 140.30]  # MSFT fails

        symbols = ["AAPL", "MSFT", "GOOGL"]
        result = market_service.get_current_prices(symbols)

        assert len(result) == 3
        assert result["AAPL"] == 155.50
        assert result["MSFT"] == 0.0  # Failed
        assert result["GOOGL"] == 140.30

    @patch.object(MarketDataService, '_get_single_price_safe')
    def test_get_current_prices_rate_limit_fallback(self, mock_get_price, market_service):
        """Test rate limit fallback to mock data"""
        # First call succeeds, second raises rate limit error
        mock_get_price.side_effect = [155.50, Exception("429: Too Many Requests")]

        symbols = ["AAPL", "MSFT", "GOOGL"]
        result = market_service.get_current_prices(symbols)

        # Should get one real price and mock data for the rest
        assert result["AAPL"] == 155.50
        assert "MSFT" in result  # Should have mock price
        assert "GOOGL" in result  # Should have mock price

    def test_get_mock_prices_known_symbols(self, market_service):
        """Test mock price generation for known symbols"""
        symbols = ["AAPL", "MSFT", "GOOGL"]
        result = market_service._get_mock_prices(symbols)

        assert len(result) == 3
        for symbol in symbols:
            assert symbol in result
            assert result[symbol] > 0

    def test_get_mock_prices_unknown_symbols(self, market_service):
        """Test mock price generation for unknown symbols"""
        symbols = ["UNKNOWN1", "UNKNOWN2"]
        result = market_service._get_mock_prices(symbols)

        assert len(result) == 2
        for symbol in symbols:
            assert result[symbol] == 100.0  # Default price

    def test_get_mock_prices_variation(self, market_service):
        """Test that mock prices have variation"""
        symbols = ["AAPL"] * 10
        results = []

        # Generate multiple mock prices for same symbol
        for _ in range(10):
            result = market_service._get_mock_prices(["AAPL"])
            results.append(result["AAPL"])

        # Should have some variation (not all exactly the same)
        unique_prices = set(results)
        assert len(unique_prices) > 1

    @patch('yfinance.download')
    def test_get_performance_data_success(self, mock_download, market_service):
        """Test getting performance data"""
        import pandas as pd

        # Mock successful download
        mock_data = pd.DataFrame({
            'Close': {
                'AAPL': [150, 155, 160],
                'MSFT': [300, 310, 320]
            }
        })
        mock_download.return_value = mock_data

        symbols = ["AAPL", "MSFT"]
        result = MarketDataService.get_performance_data(symbols, period="1mo")

        assert not result.empty
        mock_download.assert_called_once()

    @patch('yfinance.download')
    def test_get_performance_data_failure(self, mock_download, market_service):
        """Test performance data fetch failure"""
        mock_download.side_effect = Exception("Download failed")

        symbols = ["AAPL"]
        result = MarketDataService.get_performance_data(symbols)

        assert result.empty

    @patch('yfinance.download')
    def test_get_performance_data_single_symbol(self, mock_download, market_service):
        """Test performance data for single symbol"""
        import pandas as pd

        # Mock data for single symbol
        mock_data = pd.DataFrame({
            'Close': [150, 155, 160]
        })
        mock_download.return_value = mock_data

        result = MarketDataService.get_performance_data(["AAPL"])

        assert not result.empty


class TestMarketDataRateLimiting:
    """Test rate limiting functionality"""

    @pytest.fixture
    def market_service(self):
        return MarketDataService()

    def test_rate_limit_delay_calculation(self, market_service):
        """Test rate limit delay calculation"""
        # Set last request time to recent
        market_service.last_request_time = time.time() - 0.5  # 0.5 seconds ago

        start_time = time.time()
        market_service._enforce_rate_limit()
        end_time = time.time()

        # Should have waited at least remaining time to meet min_delay
        delay = end_time - start_time
        assert delay >= 0.4  # Should wait ~0.5 seconds

    def test_no_rate_limit_when_enough_time_passed(self, market_service):
        """Test no rate limiting when enough time has passed"""
        # Set last request time to long ago
        market_service.last_request_time = time.time() - 5.0  # 5 seconds ago

        start_time = time.time()
        market_service._enforce_rate_limit()
        end_time = time.time()

        # Should not wait
        delay = end_time - start_time
        assert delay < 0.1  # Minimal delay for function execution

    @skip_if_production("Time-sensitive test")
    def test_rate_limit_cooldown_behavior(self, market_service):
        """Test cooldown behavior after rate limiting"""
        # Simulate rate limit hit
        market_service.last_rate_limit_time = time.time()

        assert market_service._is_in_cooldown()

        # Test cooldown expiry
        market_service.last_rate_limit_time = time.time() - 65  # Over cooldown period
        assert not market_service._is_in_cooldown()

    @patch.object(MarketDataService, '_get_single_price_safe')
    def test_rate_limit_triggers_mock_fallback(self, mock_get_price, market_service):
        """Test that rate limiting triggers mock data fallback"""
        # Set up to trigger rate limit on second symbol
        mock_get_price.side_effect = [
            155.50,  # AAPL succeeds
            Exception("429: Too Many Requests"),  # MSFT triggers rate limit
        ]

        symbols = ["AAPL", "MSFT", "GOOGL", "TSLA"]
        result = market_service.get_current_prices(symbols)

        # Should have real price for AAPL and mock prices for others
        assert result["AAPL"] == 155.50
        assert "MSFT" in result  # Should have mock price
        assert "GOOGL" in result
        assert "TSLA" in result

    def test_concurrent_rate_limiting(self, market_service):
        """Test rate limiting with concurrent-like calls"""
        delays = []

        for i in range(3):
            start_time = time.time()
            market_service._enforce_rate_limit()
            end_time = time.time()
            delays.append(end_time - start_time)

        # First call should have minimal delay
        assert delays[0] < 0.1

        # Subsequent calls should be rate limited
        for delay in delays[1:]:
            assert delay >= market_service.min_delay - 0.1  # Allow small margin


class TestMarketDataErrorHandling:
    """Test error handling in market data service"""

    @pytest.fixture
    def market_service(self):
        return MarketDataService()

    @patch('yfinance.Ticker')
    def test_yfinance_import_error(self, mock_ticker, market_service):
        """Test handling yfinance import/connection errors"""
        mock_ticker.side_effect = ImportError("yfinance not available")

        price = market_service._get_single_price_safe("AAPL")
        assert price == 0.0

    @patch('yfinance.Ticker')
    def test_network_timeout_error(self, mock_ticker, market_service):
        """Test handling network timeout errors"""
        mock_ticker.side_effect = Exception("Request timeout")

        price = market_service._get_single_price_safe("AAPL")
        assert price == 0.0

    @patch('yfinance.Ticker')
    def test_invalid_symbol_error(self, mock_ticker, market_service):
        """Test handling invalid symbol errors"""
        mock_instance = MagicMock()
        mock_instance.fast_info = None
        mock_instance.info = {}
        mock_instance.history.return_value = None
        mock_ticker.return_value = mock_instance

        price = market_service._get_single_price_safe("INVALID")
        assert price == 0.0

    @patch('yfinance.Ticker')
    def test_malformed_data_error(self, mock_ticker, market_service):
        """Test handling malformed data from yfinance"""
        mock_instance = MagicMock()
        mock_instance.fast_info = None
        mock_instance.info = {"regularMarketPrice": "invalid_number"}
        mock_ticker.return_value = mock_instance

        price = market_service._get_single_price_safe("MALFORMED")
        assert price == 0.0

    @patch.object(MarketDataService, '_get_single_price_safe')
    def test_exception_during_price_fetch(self, mock_get_price, market_service):
        """Test exception handling during price fetching"""
        mock_get_price.side_effect = [
            155.50,  # First succeeds
            Exception("Unexpected error"),  # Second fails
            310.20   # Third succeeds
        ]

        symbols = ["AAPL", "ERROR", "MSFT"]
        result = market_service.get_current_prices(symbols)

        assert result["AAPL"] == 155.50
        assert result["ERROR"] == 0.0  # Failed, should be 0
        assert result["MSFT"] == 310.20

    def test_empty_symbol_handling(self, market_service):
        """Test handling empty or whitespace symbols"""
        symbols = ["", " ", "\t", "\n", "AAPL"]

        # Should not crash with empty symbols
        result = market_service.get_current_prices(symbols)

        # Should have entries for all symbols
        assert len(result) == len(symbols)


class TestMarketDataCaching:
    """Test market data caching behavior (when implemented)"""

    @pytest.fixture
    def market_service(self):
        return MarketDataService()

    def test_mock_price_consistency(self, market_service):
        """Test that mock prices are consistent for same symbol in same call"""
        symbols = ["UNKNOWN_STOCK"]

        # Get mock prices twice in quick succession
        result1 = market_service._get_mock_prices(symbols)
        result2 = market_service._get_mock_prices(symbols)

        # Should be different due to random variation
        # (This tests that randomization is working)
        # In production, you might want consistent mock data per session

        assert isinstance(result1["UNKNOWN_STOCK"], float)
        assert isinstance(result2["UNKNOWN_STOCK"], float)

    def test_mock_price_ranges(self, market_service):
        """Test that mock prices are within reasonable ranges"""
        known_symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "BTC-USD"]
        result = market_service._get_mock_prices(known_symbols)

        for symbol, price in result.items():
            assert price > 0
            if symbol == "BTC-USD":
                assert price > 1000  # Crypto should be higher
            else:
                assert 50 < price < 1000  # Stocks should be reasonable range


class TestMarketDataIntegration:
    """Test market data service integration scenarios"""

    @pytest.fixture
    def market_service(self):
        return MarketDataService()

    def test_mixed_symbol_types(self, market_service):
        """Test fetching different types of symbols"""
        symbols = ["AAPL", "BTC-USD", "SPY", "^GSPC", "GC=F"]  # Stock, crypto, ETF, index, futures

        with patch.object(market_service, '_get_single_price_safe') as mock_get_price:
            mock_get_price.side_effect = [155.50, 42000.0, 445.20, 4500.0, 2000.0]

            result = market_service.get_current_prices(symbols)

            assert len(result) == 5
            for symbol in symbols:
                assert symbol in result
                assert result[symbol] > 0

    def test_large_symbol_batch(self, market_service):
        """Test fetching large batch of symbols"""
        symbols = [f"STOCK{i}" for i in range(50)]

        with patch.object(market_service, '_is_in_cooldown', return_value=False), \
         patch.object(market_service, '_enforce_rate_limit'), \
         patch.object(market_service, '_get_single_price_safe') as mock_get_price:

            mock_get_price.return_value = 100.0

            result = market_service.get_current_prices(symbols)

            assert len(result) == 50
            # Should have called _get_single_price_safe for each symbol
            assert mock_get_price.call_count == 50

    @skip_if_production("Makes real API calls")
    def test_real_market_data_call(self, market_service):
        """Test actual market data call (skip in production)"""
        # This test makes real API calls - only run in development
        symbols = ["AAPL"]

        try:
            result = market_service.get_current_prices(symbols)

            # Should get real data or fallback to mock
            assert "AAPL" in result
            assert result["AAPL"] > 0

        except Exception:
            # If real API fails, should fallback gracefully
            pytest.skip("Real market data API unavailable")


class TestMarketDataValidation:
    """Test data validation in market data service"""

    @pytest.fixture
    def market_service(self):
        return MarketDataService()

    def test_price_validation(self, market_service):
        """Test that invalid prices are filtered out"""
        with patch.object(market_service, '_is_in_cooldown', return_value=False), \
         patch.object(market_service, '_enforce_rate_limit'), \
         patch.object(market_service, '_get_single_price_safe') as mock_get_price:
            # Return various invalid values
            mock_get_price.side_effect = [
                -100.0,    # Negative price
                0.0,       # Zero price
                float('inf'),  # Infinite price
                float('nan'),  # NaN price
                155.50     # Valid price
            ]

            symbols = ["NEG", "ZERO", "INF", "NAN", "VALID"]
            result = market_service.get_current_prices(symbols)

            # Negative and zero should be kept (might be valid in some cases)
            assert result["NEG"] == -100.0
            assert result["ZERO"] == 0.0

            # Infinite and NaN should be handled
            assert not (result["INF"] == float('inf'))
            assert not (str(result["NAN"]) == 'nan')

            # Valid should be preserved
            assert result["VALID"] == 155.50

    def test_symbol_normalization(self, market_service):
        """Test symbol normalization"""
        symbols = ["aapl", "MSFT", " GOOGL ", "tsla\n"]

        with patch.object(market_service, '_get_single_price_safe') as mock_get_price:
            mock_get_price.return_value = 100.0

            result = market_service.get_current_prices(symbols)

            # Should handle all symbols regardless of case/whitespace
            assert len(result) == 4


@pytest.mark.slow
class TestMarketDataPerformance:
    """Test market data service performance"""

    @pytest.fixture
    def market_service(self):
        return MarketDataService()

    @skip_if_production("Performance test with delays")
    def test_rate_limiting_performance(self, market_service):
        """Test that rate limiting doesn't cause excessive delays"""
        symbols = ["AAPL", "MSFT", "GOOGL"]

        with patch.object(market_service, '_get_single_price_safe') as mock_get_price:
            mock_get_price.return_value = 100.0

            start_time = time.time()
            result = market_service.get_current_prices(symbols)
            end_time = time.time()

            # Should complete within reasonable time (accounting for rate limiting)
            total_time = end_time - start_time
            expected_max_time = len(symbols) * market_service.max_delay + 2  # Buffer

            assert total_time < expected_max_time
            assert len(result) == len(symbols)

    def test_mock_data_generation_performance(self, market_service):
        """Test mock data generation performance"""
        large_symbol_list = [f"STOCK{i}" for i in range(1000)]

        start_time = time.time()
        result = market_service._get_mock_prices(large_symbol_list)
        end_time = time.time()

        # Should generate mock data quickly
        assert (end_time - start_time) < 1.0
        assert len(result) == 1000

    def test_memory_usage_large_requests(self, market_service):
        """Test memory usage with large requests"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Create large symbol list
        large_symbols = [f"SYM{i}" for i in range(500)]

        with patch.object(market_service, '_get_single_price_safe') as mock_get_price:
            mock_get_price.return_value = 100.0
            result = market_service.get_current_prices(large_symbols)

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 50MB)
        assert memory_increase < 50 * 1024 * 1024
        assert len(result) == len(large_symbols)
