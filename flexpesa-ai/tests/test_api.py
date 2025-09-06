"""
Basic API tests
Test core API endpoints and functionality
"""

import pytest
from unittest.mock import patch
from fastapi import status
from conftest import assert_account_valid, assert_asset_valid


class TestHealthEndpoints:
    """Test basic health and info endpoints"""

    def test_root_endpoint(self, test_client):
        """Test root endpoint returns API info"""
        response = test_client.get("/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "message" in data
        assert "status" in data
        assert data["status"] == "running"

    def test_health_endpoint(self, test_client):
        """Test health check endpoint"""
        response = test_client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "status" in data
        assert "timestamp" in data


class TestAuthConfiguration:
    """Test authentication configuration"""

    def test_auth_config_endpoint(self, test_client):
        """Test auth configuration endpoint"""
        response = test_client.get("/api/v1/auth/config")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "provider" in data
        assert "configured" in data


class TestAccountEndpoints:
    """Test account management endpoints (with mock auth)"""

    @patch('app.api.routes.get_current_user')
    def test_create_account(self, mock_auth, test_client, sample_user):
        """Test creating an account"""
        mock_auth.return_value = sample_user

        account_data = {
            "name": "Test Brokerage Account",
            "account_type": "brokerage"
        }

        response = test_client.post("/api/v1/accounts/", json=account_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert_account_valid(data)
        assert data["name"] == account_data["name"]
        assert data["account_type"] == account_data["account_type"]

    @patch('app.api.routes.get_current_user')
    def test_get_accounts(self, mock_auth, test_client, sample_user, sample_account):
        """Test getting user accounts"""
        mock_auth.return_value = sample_user

        response = test_client.get("/api/v1/accounts/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 1
        assert_account_valid(data[0])

    def test_create_account_unauthorized(self, test_client):
        """Test creating account without auth fails"""
        account_data = {
            "name": "Test Account",
            "account_type": "brokerage"
        }

        response = test_client.post("/api/v1/accounts/", json=account_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch('app.api.routes.get_current_user')
    def test_create_account_invalid_data(self, mock_auth, test_client, sample_user):
        """Test creating account with invalid data"""
        mock_auth.return_value = sample_user

        # Missing required fields
        invalid_data = {"name": ""}

        response = test_client.post("/api/v1/accounts/", json=invalid_data)
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST
        ]


class TestAssetEndpoints:
    """Test asset management endpoints"""

    @patch('app.api.routes.get_current_user')
    def test_add_asset(self, mock_auth, test_client, sample_user, sample_account):
        """Test adding an asset"""
        mock_auth.return_value = sample_user

        asset_data = {
            "account_id": sample_account.id,
            "symbol": "MSFT",
            "shares": 5,
            "avg_cost": 300.0
        }

        response = test_client.post("/api/v1/assets/", json=asset_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert_asset_valid(data)
        assert data["symbol"] == asset_data["symbol"]
        assert data["shares"] == asset_data["shares"]

    @patch('app.api.routes.get_current_user')
    def test_add_asset_to_nonexistent_account(self, mock_auth, test_client, sample_user):
        """Test adding asset to account that doesn't exist"""
        mock_auth.return_value = sample_user

        asset_data = {
            "account_id": 99999,  # Non-existent
            "symbol": "AAPL",
            "shares": 10,
            "avg_cost": 150.0
        }

        response = test_client.post("/api/v1/assets/", json=asset_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_add_asset_unauthorized(self, test_client):
        """Test adding asset without auth fails"""
        asset_data = {
            "account_id": 1,
            "symbol": "AAPL",
            "shares": 10,
            "avg_cost": 150.0
        }

        response = test_client.post("/api/v1/assets/", json=asset_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestPortfolioEndpoints:
    """Test portfolio summary endpoints"""

    @patch('app.api.routes.get_current_user')
    def test_portfolio_summary_basic(self, mock_auth, test_client, sample_user, sample_account, sample_asset):
        """Test basic portfolio summary"""
        mock_auth.return_value = sample_user

        response = test_client.get("/api/v1/portfolio/summary")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check basic structure
        assert "user_id" in data
        assert "accounts" in data
        assert "summary" in data
        assert data["user_id"] == sample_user["sub"]

        # Check we have the account and asset
        assert len(data["accounts"]) == 1
        account = data["accounts"][0]
        assert account["name"] == "Test Account"
        assert len(account["assets"]) == 1

    def test_portfolio_summary_unauthorized(self, test_client):
        """Test portfolio summary without auth fails"""
        response = test_client.get("/api/v1/portfolio/summary")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch('app.api.routes.get_current_user')
    def test_portfolio_summary_empty(self, mock_auth, test_client, sample_user):
        """Test portfolio summary with no data"""
        mock_auth.return_value = sample_user

        response = test_client.get("/api/v1/portfolio/summary")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["accounts"] == []
        assert data["summary"]["total_value"] == 0


class TestMarketEndpoints:
    """Test market data endpoints"""

    def test_market_status_public(self, test_client):
        """Test market status (public endpoint)"""
        response = test_client.get("/api/v1/market/status")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "status" in data
        assert "timestamp" in data


class TestErrorHandling:
    """Test basic error handling"""

    def test_invalid_endpoint(self, test_client):
        """Test 404 for invalid endpoints"""
        response = test_client.get("/api/v1/nonexistent")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_invalid_method(self, test_client):
        """Test 405 for invalid methods"""
        response = test_client.patch("/api/v1/market/status")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_malformed_json(self, test_client):
        """Test handling of malformed JSON"""
        response = test_client.post(
            "/api/v1/accounts/",
            data="invalid json",
            headers={"content-type": "application/json"}
        )
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST
        ]


class TestBasicIntegration:
    """Test basic workflow integration"""

    @patch('app.api.routes.get_current_user')
    def test_create_account_and_add_asset_workflow(self, mock_auth, test_client, sample_user):
        """Test complete workflow: create account -> add asset -> check summary"""
        mock_auth.return_value = sample_user

        # Step 1: Create account
        account_data = {
            "name": "Integration Test Account",
            "account_type": "brokerage"
        }

        account_response = test_client.post("/api/v1/accounts/", json=account_data)
        assert account_response.status_code == status.HTTP_200_OK

        account = account_response.json()
        account_id = account["id"]

        # Step 2: Add asset
        asset_data = {
            "account_id": account_id,
            "symbol": "AAPL",
            "shares": 10,
            "avg_cost": 150.0
        }

        asset_response = test_client.post("/api/v1/assets/", json=asset_data)
        assert asset_response.status_code == status.HTTP_200_OK

        # Step 3: Check portfolio summary
        summary_response = test_client.get("/api/v1/portfolio/summary")
        assert summary_response.status_code == status.HTTP_200_OK

        summary = summary_response.json()
        assert len(summary["accounts"]) == 1
        assert len(summary["accounts"][0]["assets"]) == 1
        assert summary["summary"]["total_assets"] == 1