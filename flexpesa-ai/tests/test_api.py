"""
API endpoint tests for Investment Portfolio API
Tests all API endpoints for correct responses, error handling, and data validation
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import status
from fastapi.testclient import TestClient

from conftest import (
    assert_valid_portfolio_response, 
    assert_valid_account_response,
    assert_valid_asset_response,
    skip_if_production
)

class TestHealthEndpoints:
    """Test health check and root endpoints"""

    def test_root_endpoint(self, test_client: TestClient):
        """Test root endpoint returns API information"""
        response = test_client.get("/")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"
        assert "endpoints" in data
        assert "features" in data

    def test_health_endpoint(self, test_client: TestClient):
        """Test health endpoint"""
        response = test_client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "checks" in data
        assert "database" in data["checks"]

    def test_detailed_health_endpoint(self, test_client: TestClient):
        """Test detailed health endpoint"""
        response = test_client.get("/api/v1/health/detailed")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "status" in data
        assert "services" in data
        assert "database" in data["services"]


class TestAuthenticationEndpoints:
    """Test authentication-related endpoints"""

    def test_auth_config_endpoint(self, test_client: TestClient):
        """Test authentication configuration endpoint"""
        response = test_client.get("/api/v1/auth/config")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "provider" in data
        assert "configured" in data
        assert data["provider"] == "clerk"

    @patch('app.api.routes.get_current_user')
    def test_auth_profile_endpoint(self, mock_auth, test_client: TestClient, mock_authenticated_user):
        """Test authenticated user profile endpoint"""
        mock_auth.return_value = mock_authenticated_user
        
        response = test_client.get("/api/v1/auth/profile")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "user_id" in data
        assert "email" in data
        assert "total_accounts" in data
        assert "total_portfolio_value" in data

    def test_auth_profile_unauthorized(self, test_client: TestClient):
        """Test profile endpoint without authentication"""
        response = test_client.get("/api/v1/auth/profile")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestPortfolioEndpoints:
    """Test portfolio-related endpoints"""

    @patch('app.api.routes.get_current_user')
    def test_portfolio_summary(self, mock_auth, test_client: TestClient, 
                             sample_portfolio_data, mock_market_data_service, mock_ai_service):
        """Test portfolio summary endpoint"""
        mock_auth.return_value = sample_portfolio_data["user"]
        
        response = test_client.get("/api/v1/portfolio/summary")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert_valid_portfolio_response(data)
        
        # Check that we have the expected account
        assert len(data["accounts"]) == 1
        account = data["accounts"][0]
        assert account["name"] == "Test Portfolio"
        assert len(account["assets"]) == 3

    def test_portfolio_summary_unauthorized(self, test_client: TestClient):
        """Test portfolio summary without authentication"""
        response = test_client.get("/api/v1/portfolio/summary")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch('app.api.routes.get_current_user')
    def test_update_prices(self, mock_auth, test_client: TestClient, 
                          sample_portfolio_data, mock_market_data_service):
        """Test price update endpoint"""
        mock_auth.return_value = sample_portfolio_data["user"]
        
        response = test_client.post("/api/v1/portfolio/update-prices")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "updated_assets" in data
        assert "total_assets" in data
        assert "duration" in data
        assert isinstance(data["updated_assets"], int)

    @patch('app.api.routes.get_current_user')
    def test_update_prices_rate_limit(self, mock_auth, test_client: TestClient,
                                    sample_portfolio_data):
        """Test rate limiting on price updates"""
        mock_auth.return_value = sample_portfolio_data["user"]
        
        # Mock rate limiter to return False
        with patch('app.middleware.rate_limit.market_data_limiter.is_allowed', return_value=False):
            response = test_client.post("/api/v1/portfolio/update-prices")
            assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


class TestAccountEndpoints:
    """Test account management endpoints"""

    @patch('app.api.routes.get_current_user')
    def test_create_account(self, mock_auth, test_client: TestClient, 
                           mock_authenticated_user, sample_account_data):
        """Test creating a new account"""
        mock_auth.return_value = mock_authenticated_user
        
        response = test_client.post("/api/v1/accounts/", json=sample_account_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert_valid_account_response(data)
        assert data["name"] == sample_account_data["name"]
        assert data["account_type"] == sample_account_data["account_type"]

    @patch('app.api.routes.get_current_user')
    def test_get_accounts(self, mock_auth, test_client: TestClient, sample_portfolio_data):
        """Test getting user accounts"""
        mock_auth.return_value = sample_portfolio_data["user"]
        
        response = test_client.get("/api/v1/accounts/")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert_valid_account_response(data[0])

    def test_create_account_unauthorized(self, test_client: TestClient, sample_account_data):
        """Test creating account without authentication"""
        response = test_client.post("/api/v1/accounts/", json=sample_account_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch('app.api.routes.get_current_user')
    def test_create_account_invalid_data(self, mock_auth, test_client: TestClient, mock_authenticated_user):
        """Test creating account with invalid data"""
        mock_auth.return_value = mock_authenticated_user
        
        invalid_data = {"name": "", "account_type": ""}
        response = test_client.post("/api/v1/accounts/", json=invalid_data)
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_400_BAD_REQUEST]


class TestAssetEndpoints:
    """Test asset management endpoints"""

    @patch('app.api.routes.get_current_user')
    def test_add_asset(self, mock_auth, test_client: TestClient, 
                      sample_portfolio_data, sample_asset_data):
        """Test adding an asset to an account"""
        mock_auth.return_value = sample_portfolio_data["user"]
        account = sample_portfolio_data["account"]
        
        asset_data = {**sample_asset_data, "account_id": account.id}
        
        response = test_client.post("/api/v1/assets/", json=asset_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert_valid_asset_response(data)
        assert data["symbol"] == asset_data["symbol"]
        assert data["shares"] == asset_data["shares"]

    @patch('app.api.routes.get_current_user')
    def test_add_asset_to_nonexistent_account(self, mock_auth, test_client: TestClient,
                                            mock_authenticated_user, sample_asset_data):
        """Test adding asset to account that doesn't exist"""
        mock_auth.return_value = mock_authenticated_user
        
        asset_data = {**sample_asset_data, "account_id": 99999}
        
        response = test_client.post("/api/v1/assets/", json=asset_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_add_asset_unauthorized(self, test_client: TestClient, sample_asset_data):
        """Test adding asset without authentication"""
        asset_data = {**sample_asset_data, "account_id": 1}
        response = test_client.post("/api/v1/assets/", json=asset_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAnalysisEndpoints:
    """Test AI analysis endpoints"""

    @patch('app.api.routes.get_current_user')
    def test_asset_analysis(self, mock_auth, test_client: TestClient, 
                           mock_authenticated_user, mock_ai_service):
        """Test enhanced asset analysis endpoint"""
        mock_auth.return_value = mock_authenticated_user
        
        response = test_client.post("/api/v1/analysis/asset/AAPL")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "success" in data
        assert "symbol" in data
        assert "analysis" in data
        assert data["symbol"] == "AAPL"

    @patch('app.api.routes.get_current_user')
    def test_quick_analysis(self, mock_auth, test_client: TestClient, mock_authenticated_user):
        """Test quick analysis endpoint"""
        mock_auth.return_value = mock_authenticated_user
        
        symbols = ["AAPL", "MSFT", "GOOGL"]
        response = test_client.post("/api/v1/analysis/quick", json=symbols)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "analysis" in data
        assert len(data["analysis"]) == len(symbols)

    @patch('app.api.routes.get_current_user')
    def test_quick_analysis_too_many_symbols(self, mock_auth, test_client: TestClient, mock_authenticated_user):
        """Test quick analysis with too many symbols"""
        mock_auth.return_value = mock_authenticated_user
        
        # Create a list with more than 20 symbols
        symbols = [f"TEST{i}" for i in range(25)]
        response = test_client.post("/api/v1/analysis/quick", json=symbols)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_analysis_unauthorized(self, test_client: TestClient):
        """Test analysis endpoints without authentication"""
        response = test_client.post("/api/v1/analysis/asset/AAPL")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestPerformanceEndpoints:
    """Test performance analysis endpoints"""

    @patch('app.api.routes.get_current_user')
    def test_all_portfolio_performance(self, mock_auth, test_client: TestClient, sample_portfolio_data):
        """Test getting performance for all portfolios"""
        mock_auth.return_value = sample_portfolio_data["user"]
        
        response = test_client.get("/api/v1/portfolios/performance")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, list)

    @patch('app.api.routes.get_current_user')
    def test_portfolio_performance_summary(self, mock_auth, test_client: TestClient, sample_portfolio_data):
        """Test getting portfolio performance summary"""
        mock_auth.return_value = sample_portfolio_data["user"]
        
        response = test_client.get("/api/v1/portfolios/performance/summary")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "total_portfolios" in data
        assert "total_value" in data
        assert "average_return" in data

    @patch('app.api.routes.get_current_user')
    def test_single_portfolio_performance(self, mock_auth, test_client: TestClient, sample_portfolio_data):
        """Test getting performance for specific portfolio"""
        mock_auth.return_value = sample_portfolio_data["user"]
        account_id = sample_portfolio_data["account"].id
        
        response = test_client.get(f"/api/v1/portfolios/{account_id}/performance")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "id" in data
        assert "name" in data
        assert "total_return" in data
        assert "sharpe_ratio" in data

    @patch('app.api.routes.get_current_user')
    def test_performance_nonexistent_portfolio(self, mock_auth, test_client: TestClient, mock_authenticated_user):
        """Test performance endpoint with nonexistent portfolio"""
        mock_auth.return_value = mock_authenticated_user
        
        response = test_client.get("/api/v1/portfolios/99999/performance")
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestPublicEndpoints:
    """Test public endpoints that don't require authentication"""

    def test_market_status(self, test_client: TestClient):
        """Test market status endpoint (public)"""
        response = test_client.get("/api/v1/market/status")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "authenticated" in data

    def test_available_benchmarks(self, test_client: TestClient):
        """Test available benchmarks endpoint"""
        response = test_client.get("/api/v1/portfolios/performance/benchmarks")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "benchmarks" in data
        assert isinstance(data["benchmarks"], list)

    def test_available_metrics(self, test_client: TestClient):
        """Test available metrics endpoint"""
        response = test_client.get("/api/v1/portfolios/performance/metrics")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "metrics" in data
        assert isinstance(data["metrics"], dict)


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_invalid_endpoint(self, test_client: TestClient):
        """Test accessing invalid endpoint"""
        response = test_client.get("/api/v1/nonexistent")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_invalid_method(self, test_client: TestClient):
        """Test using invalid HTTP method"""
        response = test_client.patch("/api/v1/portfolio/summary")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    @patch('app.api.routes.get_current_user')
    def test_server_error_handling(self, mock_auth, test_client: TestClient, mock_authenticated_user):
        """Test server error handling"""
        mock_auth.return_value = mock_authenticated_user
        
        # Mock a service to raise an exception
        with patch('app.api.routes.PortfolioService') as mock_service:
            mock_service.side_effect = Exception("Test exception")
            
            response = test_client.get("/api/v1/portfolio/summary")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            
            data = response.json()
            assert "error" in data or "detail" in data

    def test_malformed_json(self, test_client: TestClient):
        """Test handling malformed JSON requests"""
        response = test_client.post(
            "/api/v1/accounts/",
            data="invalid json",
            headers={"content-type": "application/json"}
        )
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST
        ]


@pytest.mark.slow
class TestRateLimiting:
    """Test rate limiting functionality"""

    @patch('app.api.routes.get_current_user')
    def test_rate_limit_headers(self, mock_auth, test_client: TestClient, mock_authenticated_user):
        """Test that rate limit headers are included in responses"""
        mock_auth.return_value = mock_authenticated_user
        
        response = test_client.get("/api/v1/portfolio/summary")
        assert response.status_code == status.HTTP_200_OK
        
        # Check for rate limit headers
        assert "X-Rate-Limit-Remaining" in response.headers


# Parametrized tests for different endpoints
@pytest.mark.parametrize("endpoint,method,expected_status", [
    ("/", "GET", status.HTTP_200_OK),
    ("/health", "GET", status.HTTP_200_OK),
    ("/api/v1/auth/config", "GET", status.HTTP_200_OK),
    ("/api/v1/market/status", "GET", status.HTTP_200_OK),
])
def test_public_endpoints(test_client: TestClient, endpoint: str, method: str, expected_status: int):
    """Parametrized test for public endpoints"""
    response = getattr(test_client, method.lower())(endpoint)
    assert response.status_code == expected_status


@pytest.mark.parametrize("endpoint,method", [
    ("/api/v1/portfolio/summary", "GET"),
    ("/api/v1/accounts/", "GET"),
    ("/api/v1/auth/profile", "GET"),
])
def test_protected_endpoints_unauthorized(test_client: TestClient, endpoint: str, method: str):
    """Parametrized test for protected endpoints without auth"""
    response = getattr(test_client, method.lower())(endpoint)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
