import jwt
import requests
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging
from typing import Optional, Dict, Any
import time
from functools import lru_cache

from app.core.config import settings

logger = logging.getLogger(__name__)

class ClerkAuthMiddleware(BaseHTTPMiddleware):
    """Clerk JWT Authentication Middleware"""

    def __init__(self, app):
        super().__init__(app)
        self.clerk_secret_key = settings.CLERK_SECRET_KEY
        self.clerk_publishable_key = settings.CLERK_PUBLISHABLE_KEY

        # Public endpoints that don't require authentication
        self.public_endpoints = {
            "/",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/metrics"
        }

        # Cache for JWKS
        self._jwks_cache = {}
        self._jwks_cache_time = 0
        self._jwks_cache_ttl = 3600  # 1 hour

    async def dispatch(self, request: Request, call_next):
        """Process the request and validate Clerk JWT if required"""

        # Skip authentication for public endpoints
        if self._is_public_endpoint(request.url.path):
            return await call_next(request)

        # Skip authentication for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        try:
            # Extract and validate JWT token
            user_data = await self._validate_clerk_token(request)

            if user_data:
                # Add user data to request state
                request.state.user = user_data
                request.state.user_id = user_data.get("sub")
                request.state.authenticated = True
            else:
                request.state.authenticated = False

                # Return 401 for API endpoints requiring authentication
                if request.url.path.startswith("/api/"):
                    raise HTTPException(status_code=401, detail="Authentication required")

            response = await call_next(request)
            return response

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {e}")

            # Return 401 for API endpoints
            if request.url.path.startswith("/api/"):
                raise HTTPException(status_code=401, detail="Authentication failed")

            # For non-API endpoints, continue without authentication
            request.state.authenticated = False
            return await call_next(request)

    def _is_public_endpoint(self, path: str) -> bool:
        """Check if endpoint is public and doesn't require authentication"""
        # Exact match
        if path in self.public_endpoints:
            return True

        # Pattern matching for documentation endpoints
        if path.startswith(("/docs", "/redoc", "/openapi.json")):
            return True

        # Health check endpoints
        if path.startswith("/health"):
            return True

        return False

    async def _validate_clerk_token(self, request: Request) -> Optional[Dict[str, Any]]:
        """Validate Clerk JWT token and return user data"""

        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]

        try:
            # Get Clerk JWKS for token verification
            jwks = await self._get_clerk_jwks()

            # Decode and verify JWT
            header = jwt.get_unverified_header(token)
            key_id = header.get("kid")

            if not key_id or key_id not in jwks:
                logger.warning(f"Invalid key ID in JWT: {key_id}")
                return None

            # Get the public key
            public_key = jwks[key_id]

            # Verify and decode the token
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=settings.CLERK_PUBLISHABLE_KEY,
                options={"verify_exp": True, "verify_aud": True}
            )

            # Validate token claims
            if payload.get("iss") != f"https://{settings.CLERK_DOMAIN}":
                logger.warning("Invalid issuer in JWT")
                return None

            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
        except Exception as e:
            logger.error(f"JWT validation error: {e}")
            return None

    @lru_cache(maxsize=1)
    async def _get_clerk_jwks(self) -> Dict[str, Any]:
        """Get Clerk JWKS (JSON Web Key Set) for token verification"""

        # Check cache first
        current_time = time.time()
        if (self._jwks_cache and
            current_time - self._jwks_cache_time < self._jwks_cache_ttl):
            return self._jwks_cache

        try:
            # Fetch JWKS from Clerk
            jwks_url = f"https://{settings.CLERK_DOMAIN}/.well-known/jwks.json"
            response = requests.get(jwks_url, timeout=10)
            response.raise_for_status()

            jwks_data = response.json()

            # Process JWKS keys
            processed_keys = {}
            for key in jwks_data.get("keys", []):
                kid = key.get("kid")
                if kid:
                    # Convert JWK to PEM format for PyJWT
                    from jwt.algorithms import RSAAlgorithm
                    public_key = RSAAlgorithm.from_jwk(key)
                    processed_keys[kid] = public_key

            # Update cache
            self._jwks_cache = processed_keys
            self._jwks_cache_time = current_time

            return processed_keys

        except Exception as e:
            logger.error(f"Failed to fetch Clerk JWKS: {e}")

            # Return cached keys if available
            if self._jwks_cache:
                logger.warning("Using cached JWKS due to fetch failure")
                return self._jwks_cache

            return {}

# Dependency for protected routes
async def get_current_user(request: Request) -> Dict[str, Any]:
    """Dependency to get current authenticated user"""

    if not hasattr(request.state, 'authenticated') or not request.state.authenticated:
        raise HTTPException(status_code=401, detail="Authentication required")

    if not hasattr(request.state, 'user'):
        raise HTTPException(status_code=401, detail="User data not available")

    return request.state.user

# Optional dependency for routes that work with or without authentication
async def get_current_user_optional(request: Request) -> Optional[Dict[str, Any]]:
    """Optional dependency to get current user if authenticated"""

    if (hasattr(request.state, 'authenticated') and
        request.state.authenticated and
        hasattr(request.state, 'user')):
        return request.state.user

    return None

# Helper function to get user ID
async def get_user_id(request: Request) -> str:
    """Get current user ID"""
    user = await get_current_user(request)
    return user.get("sub") or user.get("user_id")

# Helper function to check if user is authenticated
def is_authenticated(request: Request) -> bool:
    """Check if user is authenticated"""
    return (hasattr(request.state, 'authenticated') and
            request.state.authenticated)
