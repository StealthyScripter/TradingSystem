import time
import asyncio
from collections import defaultdict, deque
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging
from typing import Dict, Deque
import hashlib

from app.core.config import settings

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with sliding window approach"""

    def __init__(self, app):
        super().__init__(app)
        self.requests: Dict[str, Deque[float]] = defaultdict(deque)
        self.window_size = 60  # 60 seconds window
        self.max_requests = settings.RATE_LIMIT_PER_MINUTE
        self.burst_limit = settings.RATE_LIMIT_BURST

        # Different limits for different endpoints
        self.endpoint_limits = {
            "/api/v1/portfolio/update-prices": 10,  # Lower limit for expensive operations
            "/api/v1/analysis/": 20,  # AI analysis endpoints
            "/api/v1/portfolio/summary": 30,  # Portfolio data
        }

        # Cleanup task
        self._cleanup_task = None
        self._start_cleanup_task()

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""

        # Skip rate limiting for health checks and docs
        if self._should_skip_rate_limit(request.url.path):
            return await call_next(request)

        # Get client identifier
        client_id = self._get_client_id(request)

        # Get rate limit for this endpoint
        rate_limit = self._get_rate_limit(request.url.path)

        # Check rate limit
        if not self._check_rate_limit(client_id, rate_limit):
            return self._rate_limit_response(client_id, rate_limit)

        # Record the request
        self._record_request(client_id)

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        remaining = self._get_remaining_requests(client_id, rate_limit)
        response.headers["X-Rate-Limit-Limit"] = str(rate_limit)
        response.headers["X-Rate-Limit-Remaining"] = str(max(0, remaining))
        response.headers["X-Rate-Limit-Reset"] = str(int(time.time() + self.window_size))

        return response

    def _should_skip_rate_limit(self, path: str) -> bool:
        """Check if path should skip rate limiting"""
        skip_paths = {
            "/", "/health", "/docs", "/redoc", "/openapi.json", "/metrics"
        }

        return path in skip_paths or path.startswith(("/docs", "/redoc"))

    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier for rate limiting"""

        # Try to get user ID from authentication
        if hasattr(request.state, 'user_id') and request.state.user_id:
            return f"user:{request.state.user_id}"

        # Use IP address as fallback
        # Check for forwarded IP (when behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        # Hash IP for privacy
        ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()[:16]
        return f"ip:{ip_hash}"

    def _get_rate_limit(self, path: str) -> int:
        """Get rate limit for specific endpoint"""

        # Check for specific endpoint limits
        for endpoint_pattern, limit in self.endpoint_limits.items():
            if path.startswith(endpoint_pattern):
                return limit

        # Default limit
        return self.max_requests

    def _check_rate_limit(self, client_id: str, rate_limit: int) -> bool:
        """Check if client has exceeded rate limit"""
        now = time.time()
        window_start = now - self.window_size

        # Get client's request history
        client_requests = self.requests[client_id]

        # Remove old requests outside the window
        while client_requests and client_requests[0] < window_start:
            client_requests.popleft()

        # Check if under rate limit
        return len(client_requests) < rate_limit

    def _record_request(self, client_id: str):
        """Record a new request for the client"""
        now = time.time()
        self.requests[client_id].append(now)

    def _get_remaining_requests(self, client_id: str, rate_limit: int) -> int:
        """Get remaining requests for client"""
        now = time.time()
        window_start = now - self.window_size

        # Get client's request history
        client_requests = self.requests[client_id]

        # Count requests in current window
        current_requests = sum(1 for req_time in client_requests if req_time >= window_start)

        return max(0, rate_limit - current_requests)

    def _rate_limit_response(self, client_id: str, rate_limit: int) -> JSONResponse:
        """Return rate limit exceeded response"""
        now = time.time()
        reset_time = int(now + self.window_size)
        remaining = self._get_remaining_requests(client_id, rate_limit)

        logger.warning(f"Rate limit exceeded for client: {client_id}")

        return JSONResponse(
            status_code=429,
            content={
                "error": True,
                "message": "Rate limit exceeded. Please try again later.",
                "status_code": 429,
                "details": {
                    "limit": rate_limit,
                    "remaining": remaining,
                    "reset_time": reset_time,
                    "retry_after": self.window_size
                }
            },
            headers={
                "X-Rate-Limit-Limit": str(rate_limit),
                "X-Rate-Limit-Remaining": str(remaining),
                "X-Rate-Limit-Reset": str(reset_time),
                "Retry-After": str(self.window_size)
            }
        )

    def _start_cleanup_task(self):
        """Start background task to clean up old request records"""
        if not self._cleanup_task or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_old_records())

    async def _cleanup_old_records(self):
        """Background task to clean up old request records"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes

                now = time.time()
                window_start = now - self.window_size

                # Clean up old records
                clients_to_remove = []
                for client_id, requests in self.requests.items():
                    # Remove old requests
                    while requests and requests[0] < window_start:
                        requests.popleft()

                    # Mark empty clients for removal
                    if not requests:
                        clients_to_remove.append(client_id)

                # Remove empty clients
                for client_id in clients_to_remove:
                    del self.requests[client_id]

                if clients_to_remove:
                    logger.debug(f"Cleaned up {len(clients_to_remove)} empty rate limit records")

            except Exception as e:
                logger.error(f"Error in rate limit cleanup task: {e}")
                await asyncio.sleep(60)  # Wait a bit before retrying

class RateLimiter:
    """Standalone rate limiter for specific use cases"""

    def __init__(self, max_requests: int = 60, window_size: int = 60):
        self.max_requests = max_requests
        self.window_size = window_size
        self.requests: Dict[str, Deque[float]] = defaultdict(deque)

    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed for client"""
        now = time.time()
        window_start = now - self.window_size

        # Get client's request history
        client_requests = self.requests[client_id]

        # Remove old requests
        while client_requests and client_requests[0] < window_start:
            client_requests.popleft()

        # Check rate limit
        if len(client_requests) >= self.max_requests:
            return False

        # Record request
        client_requests.append(now)
        return True

    def get_remaining(self, client_id: str) -> int:
        """Get remaining requests for client"""
        now = time.time()
        window_start = now - self.window_size

        client_requests = self.requests[client_id]
        current_requests = sum(1 for req_time in client_requests if req_time >= window_start)

        return max(0, self.max_requests - current_requests)

# Global rate limiter instances for specific use cases
market_data_limiter = RateLimiter(max_requests=30, window_size=60)  # 30 requests per minute
ai_analysis_limiter = RateLimiter(max_requests=10, window_size=60)   # 10 requests per minute
