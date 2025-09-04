"""
Conditional authentication module
Provides mock authentication when DISABLE_AUTH is True
"""

from fastapi import Request, HTTPException
from typing import Optional, Dict, Any
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

def get_mock_user() -> Dict[str, Any]:
    """Get mock user data for development/testing"""
    return {
        "sub": settings.MOCK_USER_ID,
        "email": settings.MOCK_USER_EMAIL,
        "first_name": settings.MOCK_USER_FIRST_NAME,
        "last_name": settings.MOCK_USER_LAST_NAME,
        "iss": "mock-auth-provider",
        "aud": "mock-audience"
    }

async def get_current_user(request: Request) -> Dict[str, Any]:
    """Get current authenticated user (real or mock)"""

    if settings.DISABLE_AUTH:
        # Return mock user
        logger.debug(f"🔓 Using mock user: {settings.MOCK_USER_EMAIL}")
        return get_mock_user()
    else:
        # Use real Clerk authentication
        from app.middleware.clerk_auth import get_current_user as _get_current_user
        return await _get_current_user(request)

async def get_current_user_optional(request: Request) -> Optional[Dict[str, Any]]:
    """Get current user if authenticated (optional)"""

    if settings.DISABLE_AUTH:
        # Return mock user
        return get_mock_user()
    else:
        # Use real Clerk authentication
        from app.middleware.clerk_auth import get_current_user_optional as _get_current_user_optional
        return await _get_current_user_optional(request)

async def get_user_id(request: Request) -> str:
    """Get current user ID"""

    if settings.DISABLE_AUTH:
        return settings.MOCK_USER_ID
    else:
        # Use real Clerk authentication
        from app.middleware.clerk_auth import get_user_id as _get_user_id
        return await _get_user_id(request)

def is_authenticated(request: Request) -> bool:
    """Check if user is authenticated"""

    if settings.DISABLE_AUTH:
        return True  # Always authenticated in mock mode
    else:
        # Use real Clerk authentication
        from app.middleware.clerk_auth import is_authenticated as _is_authenticated
        return _is_authenticated(request)