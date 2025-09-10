from fastapi import APIRouter, HTTPException, Depends, status, Request
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

# Response models matching frontend types
class User(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    is_active: bool = True

class UserProfile(BaseModel):
    user_id: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    total_accounts: int = 0
    total_portfolio_value: float = 0.0
    last_active: str

class AuthConfig(BaseModel):
    provider: str
    configured: bool
    disabled: bool
    publishable_key: Optional[str] = None
    domain: Optional[str] = None
    mock_user: Optional[dict] = None
    message: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str

class LoginResponse(BaseModel):
    user: User
    message: str = "Login successful"

router = APIRouter()

@router.get("/auth/config", response_model=AuthConfig)
async def get_auth_config():
    """Get authentication configuration for frontend"""
    return AuthConfig(
        provider="mock",
        configured=True,
        disabled=True,
        mock_user={
            "id": "mock-user-id",
            "email": "admin@portfolio.com",
            "first_name": "Portfolio",
            "last_name": "Admin"
        },
        message="Authentication is DISABLED - using mock user"
    )

@router.get("/auth/profile", response_model=UserProfile)
async def get_user_profile(request: Request):
    """Get current user's profile and portfolio summary"""
    return UserProfile(
        user_id="mock-user-id",
        email="admin@portfolio.com",
        first_name="Portfolio",
        last_name="Admin",
        total_accounts=4,
        total_portfolio_value=139230.50,
        last_active=datetime.utcnow().isoformat()
    )

@router.post("/auth/cookie/login", response_model=LoginResponse)
async def mock_login(login_data: LoginRequest):
    """Mock login endpoint - replace with real authentication"""
    if login_data.email and login_data.password:
        user = User(
            id="mock-user-id",
            email=login_data.email,
            first_name="Portfolio",
            last_name="Admin",
            is_active=True
        )
        return LoginResponse(user=user)
    else:
        raise HTTPException(status_code=400, detail="Invalid credentials")

@router.post("/auth/register", response_model=User)
async def mock_register(user_data: RegisterRequest):
    """Mock registration endpoint - replace with real authentication"""
    return User(
        id="mock-user-id",
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        is_active=True
    )

@router.post("/auth/cookie/logout")
async def mock_logout():
    """Mock logout endpoint"""
    return {"message": "Logged out successfully"}

@router.get("/users/me", response_model=User)
async def get_current_user():
    """Mock current user endpoint - replace with real authentication"""
    return User(
        id="mock-user-id",
        email="admin@portfolio.com",
        first_name="Portfolio",
        last_name="Admin",
        is_active=True
    )
    