import time
import json
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging
from typing import Optional
from urllib.parse import unquote

from app.core.config import settings

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Enhanced logging middleware for request/response logging"""

    def __init__(self, app):
        super().__init__(app)
        self.sensitive_headers = {
            "authorization", "cookie", "x-api-key",
            "x-auth-token", "x-access-token"
        }
        self.sensitive_params = {
            "password", "token", "secret", "key", "api_key"
        }

    async def dispatch(self, request: Request, call_next):
        """Log request and response details"""

        # Generate unique request ID
        request_id = str(uuid.uuid4())[:8]

        # Start timing
        start_time = time.time()

        # Add request ID to request state
        request.state.request_id = request_id

        # Log request
        await self._log_request(request, request_id)

        # Process request
        try:
            response = await call_next(request)

            # Calculate processing time
            process_time = time.time() - start_time

            # Log response
            await self._log_response(request, response, request_id, process_time)

            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.4f}"

            return response

        except Exception as e:
            process_time = time.time() - start_time
            await self._log_error(request, e, request_id, process_time)
            raise

    async def _log_request(self, request: Request, request_id: str):
        """Log incoming request details"""

        # Extract basic request info
        method = request.method
        url = str(request.url)
        user_agent = request.headers.get("user-agent", "unknown")

        # Get client info
        client_ip = self._get_client_ip(request)

        # Get user info if available
        user_info = self._get_user_info(request)

        # Sanitize query parameters
        query_params = dict(request.query_params)
        sanitized_params = self._sanitize_data(query_params)

        # Create log entry
        log_data = {
            "type": "request",
            "request_id": request_id,
            "method": method,
            "url": unquote(url),
            "path": request.url.path,
            "query_params": sanitized_params,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "user_info": user_info,
            "headers": self._sanitize_headers(dict(request.headers)),
            "timestamp": time.time()
        }

        # Log at appropriate level
        if settings.DEBUG:
            logger.info(f"[{request_id}] {method} {request.url.path} - {client_ip}")
            logger.debug(f"Request details: {json.dumps(log_data, indent=2)}")
        else:
            logger.info(f"[{request_id}] {method} {request.url.path} - {client_ip} - {user_agent[:50]}")

    async def _log_response(self, request: Request, response: Response,
                          request_id: str, process_time: float):
        """Log response details"""

        status_code = response.status_code

        # Determine log level based on status code
        if status_code >= 500:
            log_level = logging.ERROR
            level_name = "ERROR"
        elif status_code >= 400:
            log_level = logging.WARNING
            level_name = "WARN"
        else:
            log_level = logging.INFO
            level_name = "INFO"

        # Create log entry
        log_data = {
            "type": "response",
            "request_id": request_id,
            "status_code": status_code,
            "process_time": round(process_time, 4),
            "method": request.method,
            "path": request.url.path,
            "user_info": self._get_user_info(request),
            "timestamp": time.time()
        }

        # Log response
        logger.log(
            log_level,
            f"[{request_id}] {request.method} {request.url.path} - "
            f"{status_code} - {process_time:.4f}s"
        )

        # Detailed debug logging
        if settings.DEBUG and status_code >= 400:
            logger.debug(f"Response details: {json.dumps(log_data, indent=2)}")

        # Log slow requests
        if process_time > 5.0:  # Requests taking more than 5 seconds
            logger.warning(
                f"[{request_id}] SLOW REQUEST: {request.method} {request.url.path} - "
                f"{process_time:.4f}s - {status_code}"
            )

    async def _log_error(self, request: Request, error: Exception,
                        request_id: str, process_time: float):
        """Log error details"""

        error_type = type(error).__name__
        error_message = str(error)

        log_data = {
            "type": "error",
            "request_id": request_id,
            "error_type": error_type,
            "error_message": error_message,
            "process_time": round(process_time, 4),
            "method": request.method,
            "path": request.url.path,
            "user_info": self._get_user_info(request),
            "timestamp": time.time()
        }

        logger.error(
            f"[{request_id}] ERROR: {request.method} {request.url.path} - "
            f"{error_type}: {error_message} - {process_time:.4f}s"
        )

        if settings.DEBUG:
            logger.debug(f"Error details: {json.dumps(log_data, indent=2)}")

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address, handling proxies"""

        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"

    def _get_user_info(self, request: Request) -> Optional[dict]:
        """Extract user information from request"""

        if not hasattr(request.state, 'user') or not request.state.user:
            return None

        user = request.state.user
        return {
            "user_id": user.get("sub") or user.get("user_id"),
            "email": user.get("email"),
            "authenticated": getattr(request.state, 'authenticated', False)
        }

    def _sanitize_headers(self, headers: dict) -> dict:
        """Remove sensitive headers from logs"""

        sanitized = {}
        for key, value in headers.items():
            if key.lower() in self.sensitive_headers:
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = value

        return sanitized

    def _sanitize_data(self, data: dict) -> dict:
        """Remove sensitive data from logs"""

        sanitized = {}
        for key, value in data.items():
            if key.lower() in self.sensitive_params:
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = value

        return sanitized

# Custom logger for business operations
class BusinessLogger:
    """Specialized logger for business operations"""

    def __init__(self):
        self.logger = logging.getLogger("business")

        # Create file handler if in production
        if settings.ENVIRONMENT == "production":
            import os
            from logging.handlers import RotatingFileHandler

            log_dir = "logs"
            os.makedirs(log_dir, exist_ok=True)

            file_handler = RotatingFileHandler(
                f"{log_dir}/business.log",
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(logging.INFO)

            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)

    def log_portfolio_update(self, user_id: str, portfolio_value: float,
                           assets_updated: int):
        """Log portfolio update"""
        self.logger.info(
            f"Portfolio updated - User: {user_id}, Value: ${portfolio_value:,.2f}, "
            f"Assets: {assets_updated}"
        )

    def log_market_data_fetch(self, symbols: list, success_count: int,
                            duration: float):
        """Log market data fetch operation"""
        self.logger.info(
            f"Market data fetch - Symbols: {len(symbols)}, Success: {success_count}, "
            f"Duration: {duration:.2f}s"
        )

    def log_ai_analysis(self, user_id: str, analysis_type: str,
                       processing_time: float):
        """Log AI analysis operation"""
        self.logger.info(
            f"AI analysis - User: {user_id}, Type: {analysis_type}, "
            f"Time: {processing_time:.2f}s"
        )

    def log_user_action(self, user_id: str, action: str, details: dict = None):
        """Log user action"""
        details_str = json.dumps(details) if details else ""
        self.logger.info(
            f"User action - User: {user_id}, Action: {action}, Details: {details_str}"
        )

# Global business logger instance
business_logger = BusinessLogger()
