from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional
from pydantic import BaseModel

# Simple auth models for now
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str

class User(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    is_active: bool = True

router = APIRouter()

@router.post("/auth/cookie/login")
async def mock_login(login_data: LoginRequest):
    """Mock login endpoint - replace with real authentication"""
    # For now, accept any login for development
    if login_data.email and login_data.password:
        return {"message": "Login successful", "status": "ok"}
    else:
        raise HTTPException(status_code=400, detail="Invalid credentials")

@router.post("/auth/register")
async def mock_register(user_data: RegisterRequest):
    """Mock registration endpoint - replace with real authentication"""
    # For now, accept any registration for development
    return {
        "id": "mock-user-id",
        "email": user_data.email,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "is_active": True
    }

@router.post("/auth/cookie/logout")
async def mock_logout():
    """Mock logout endpoint"""
    return {"message": "Logged out successfully"}

@router.get("/users/me")
async def get_current_user():
    """Mock current user endpoint - replace with real authentication"""
    # For development, return a mock user
    return {
        "id": "mock-user-id",
        "email": "admin@portfolio.com",
        "first_name": "Portfolio",
        "last_name": "Admin",
        "is_active": True
    }
