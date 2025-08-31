
import requests
import sys

API_BASE = 'http://localhost:8000/api/v1'

def test_auth():
    """Simple authentication test using requests"""
    print("🧪 Testing authentication with requests...")

    # Test backend connection
    print("1. Testing backend connection...")
    try:
        response = requests.get(f"{API_BASE}/../")
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print(f"❌ Backend returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        print("   Start backend with: python run.py")
        return False

    # Test user registration
    print("2. Testing user registration...")
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User"
    }

    try:
        response = requests.post(f"{API_BASE}/auth/register", json=user_data)
        if response.status_code == 201:
            print("✅ User registration successful")
        elif response.status_code == 400:
            print("⚠️  User already exists, continuing...")
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Registration error: {e}")

    # Test login with default user
    print("3. Testing login...")
    login_data = {
        "username": "admin@portfolio.com",
        "password": "password"
    }

    try:
        response = requests.post(f"{API_BASE}/auth/jwt/login", data=login_data)
        if response.status_code == 200:
            print("✅ Login successful")
            # Extract cookies for next request
            cookies = response.cookies
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False

    # Test protected route
    print("4. Testing protected route...")
    try:
        response = requests.get(f"{API_BASE}/portfolio/summary", cookies=cookies)
        if response.status_code == 200:
            print("✅ Protected route accessible")
            data = response.json()
            print(f"   Portfolio: {len(data.get('accounts', []))} accounts")
        else:
            print(f"❌ Protected route failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Protected route error: {e}")

    print("🎉 Authentication tests completed!")
    return True

if __name__ == "__main__":
    try:
        test_auth()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)
