"""
API tests - simplified and reliable
Tests core API endpoints with auth disabled
"""

import pytest
from fastapi import status

class TestHealthEndpoints:
    """Test basic health and info endpoints"""

    def test_root_endpoint(self, test_client):
        """Test root endpoint returns API info"""
        response = test_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data

    def test_health_endpoint(self, test_client):
        """Test health check endpoint"""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data

class TestAuthConfiguration:
    """Test authentication configuration"""

    def test_auth_config_endpoint(self, test_client):
        """Test auth configuration endpoint"""
        response = test_client.get("/api/v1/auth/config")
        assert response.status_code == 200
        data = response.json()
        assert "provider" in data
        assert "disabled" in data

class TestAccountEndpoints:
    """Test account management endpoints"""

    def test_create_account(self, test_client):
        """Test creating an account"""
        account_data = {
            "name": "Test Brokerage Account",
            "account_type": "brokerage"
        }
        response = test_client.post("/api/v1/accounts/", json=account_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == account_data["name"]
        assert data["account_type"] == account_data["account_type"]
        assert "id" in data

    def test_get_accounts(self, test_client, sample_account):
        """Test getting user accounts"""
        response = test_client.get("/api/v1/accounts/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_create_account_invalid_data(self, test_client):
        """Test creating account with invalid data"""
        invalid_data = {"name": ""}  # Missing account_type
        response = test_client.post("/api/v1/accounts/", json=invalid_data)
        assert response.status_code == 422  # Validation error

class TestAssetEndpoints:
    """Test asset management endpoints"""

    def test_add_asset(self, test_client, sample_account):
        """Test adding an asset"""
        asset_data = {
            "account_id": sample_account.id,
            "symbol": "MSFT",
            "shares": 5,
            "avg_cost": 300.0
        }
        response = test_client.post("/api/v1/assets/", json=asset_data)
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == asset_data["symbol"]
        assert data["shares"] == asset_data["shares"]
        assert data["account_id"] == asset_data["account_id"]

    def test_add_asset_to_nonexistent_account(self, test_client):
        """Test adding asset to account that doesn't exist"""
        asset_data = {
            "account_id": 99999,  # Non-existent
            "symbol": "AAPL",
            "shares": 10,
            "avg_cost": 150.0
        }
        response = test_client.post("/api/v1/assets/", json=asset_data)
        assert response.status_code == 404

    def test_add_asset_invalid_data(self, test_client, sample_account):
        """Test adding asset with invalid data"""
        invalid_data = {
            "account_id": sample_account.id,
            "symbol": "",  # Empty symbol
            "shares": -1,  # Negative shares
            "avg_cost": 150.0
        }
        response = test_client.post("/api/v1/assets/", json=invalid_data)
        assert response.status_code == 422

class TestPortfolioEndpoints:
    """Test portfolio summary endpoints"""

    def test_portfolio_summary_basic(self, test_client, sample_account, sample_asset):
        """Test basic portfolio summary"""
        response = test_client.get("/api/v1/portfolio/summary")
        assert response.status_code == 200
        data = response.json()

        # Check basic structure
        assert "user_id" in data
        assert "accounts" in data
        assert "summary" in data

        # Check we have the account and asset
        assert len(data["accounts"]) >= 1
        assert len(data["accounts"][0]["assets"]) >= 1

    def test_portfolio_summary_empty(self, test_client):
        """Test portfolio summary with no data"""
        response = test_client.get("/api/v1/portfolio/summary")
        assert response.status_code == 200
        data = response.json()

        assert "accounts" in data
        assert "summary" in data
        assert data["summary"]["total_value"] == 0

class TestMarketEndpoints:
    """Test market data endpoints"""

    def test_market_status_public(self, test_client):
        """Test market status (public endpoint)"""
        response = test_client.get("/api/v1/market/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data

class TestBasicIntegration:
    """Test basic workflow integration"""

    def test_create_account_and_add_asset_workflow(self, test_client):
        """Test complete workflow: create account -> add asset -> check summary"""
        # Step 1: Create account
        account_data = {
            "name": "Integration Test Account",
            "account_type": "brokerage"
        }
        account_response = test_client.post("/api/v1/accounts/", json=account_data)
        assert account_response.status_code == 200
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
        assert asset_response.status_code == 200

        # Step 3: Check portfolio summary
        summary_response = test_client.get("/api/v1/portfolio/summary")
        assert summary_response.status_code == 200
        summary = summary_response.json()

        # Verify the workflow worked
        found_account = None
        for acc in summary["accounts"]:
            if acc["id"] == account_id:
                found_account = acc
                break

        assert found_account is not None
        assert len(found_account["assets"]) >= 1
        assert found_account["assets"][0]["symbol"] == "AAPL"

class TestErrorHandling:
    """Test basic error handling"""

    def test_invalid_endpoint(self, test_client):
        """Test 404 for invalid endpoints"""
        response = test_client.get("/api/v1/nonexistent")
        assert response.status_code == 404

    def test_malformed_json(self, test_client):
        """Test handling of malformed JSON"""
        response = test_client.post(
            "/api/v1/accounts/",
            data="invalid json",
            headers={"content-type": "application/json"}
        )
        assert response.status_code in [400, 422]