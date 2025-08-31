#!/usr/bin/env python3
"""Test authentication system"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app

def test_auth():
    """Test authentication endpoints"""
    client = TestClient(app)

    print("🧪 Testing authentication...")

    # Test registration
    print("1. Testing user registration...")
    response = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User"
    })

    if response.status_code == 201:
        print("✅ Registration successful")
    else:
        print(f"⚠️ Registration: {response.status_code} - {response.text}")

    # Test login
    print("2. Testing login...")
    response = client.post("/api/v1/auth/cookie/login", data={
        "username": "admin@portfolio.com",
        "password": "password"
    })

    if response.status_code == 204:
        print("✅ Login successful")
        cookies = response.cookies
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return False

    # Test protected route
    print("3. Testing protected route...")
    response = client.get("/api/v1/portfolio/summary", cookies=cookies)

    if response.status_code == 200:
        print("✅ Protected route accessible")
        data = response.json()
        print(f"   Portfolio: {len(data.get('accounts', []))} accounts, ${data.get('total_value', 0):,.2f}")
    else:
        print(f"❌ Protected route failed: {response.status_code} - {response.text}")

    # Test unauthorized access
    print("4. Testing unauthorized access...")
    response = client.get("/api/v1/portfolio/summary")

    if response.status_code == 401:
        print("✅ Unauthorized access blocked")
    else:
        print(f"❌ Should be unauthorized: {response.status_code}")

    print("\n🎉 Authentication tests completed!")
    return True

if __name__ == "__main__":
    try:
        test_auth()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
        