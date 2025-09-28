"""
Middleware for request tracking, logging, and error handling.

This middleware adds request tracking, timing, and ensures consistent
error response formatting across the application.
"""
import time
import uuid
import logging
from typing import Callable
from datetime import datetime, timezone
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track requests with unique IDs and timing information.
    
    This middleware:
    - Generates unique request IDs for tracking
    - Logs request/response information
    - Measures request processing time
    - Adds standard headers to responses
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Store request ID in request state for use in handlers
        request.state.request_id = request_id
        
        # Start timing
        start_time = time.time()
        start_timestamp = datetime.now(timezone.utc)
        
        # Log incoming request
        logger.info(
            "Incoming request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_host": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "timestamp": start_timestamp.isoformat(),
            }
        )
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log successful response
            logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "process_time": round(process_time, 4),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
            
            # Add standard headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(round(process_time, 4))
            
            # If this is an error response with JSON content, add timestamp
            if (response.status_code >= 400 and 
                hasattr(response, 'body') and 
                response.headers.get("content-type", "").startswith("application/json")):
                
                try:
                    import json
                    content = json.loads(response.body.decode())
                    if isinstance(content, dict) and "error" in content:
                        content["error"]["timestamp"] = start_timestamp.isoformat()
                        # Create new response with updated content
                        response = JSONResponse(
                            content=content,
                            status_code=response.status_code,
                            headers=dict(response.headers)
                        )
                except (json.JSONDecodeError, AttributeError, UnicodeDecodeError):
                    # If we can't parse/modify the response, just return as is
                    pass
            
            return response
            
        except Exception as exc:
            # Calculate processing time for failed requests
            process_time = time.time() - start_time
            
            # Log the exception
            logger.error(
                "Request failed with unhandled exception",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "process_time": round(process_time, 4),
                    "error": str(exc),
                    "error_type": exc.__class__.__name__,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
                exc_info=True
            )
            
            # Re-raise the exception to be handled by exception handlers
            raise exc


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers and basic security measures.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Add HSTS header for HTTPS (only add if the request is HTTPS)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware.
    
    Note: This is a basic implementation suitable for single-instance deployments.
    For production with multiple instances, consider using Redis-based rate limiting.
    """
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls  # Number of calls allowed
        self.period = period  # Time period in seconds
        self.clients = {}  # In-memory storage for client requests
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health check endpoints
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Get client identifier (IP address)
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Clean up old entries
        self._cleanup_old_entries(current_time)
        
        # Check rate limit for this client
        if client_ip in self.clients:
            client_requests = self.clients[client_ip]
            
            # Count requests in the current time window
            recent_requests = [
                req_time for req_time in client_requests 
                if current_time - req_time < self.period
            ]
            
            if len(recent_requests) >= self.calls:
                # Rate limit exceeded
                request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
                
                logger.warning(
                    "Rate limit exceeded",
                    extra={
                        "request_id": request_id,
                        "client_ip": client_ip,
                        "requests_count": len(recent_requests),
                        "rate_limit": self.calls,
                        "period": self.period,
                    }
                )
                
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": {
                            "request_id": request_id,
                            "error_code": "RATE_LIMIT_EXCEEDED",
                            "message": "Too many requests",
                            "details": {
                                "limit": self.calls,
                                "period": self.period,
                                "retry_after": self.period
                            },
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }
                    },
                    headers={
                        "X-RateLimit-Limit": str(self.calls),
                        "X-RateLimit-Period": str(self.period),
                        "X-RateLimit-Remaining": "0",
                        "Retry-After": str(self.period)
                    }
                )
            
            # Update the request times
            self.clients[client_ip] = recent_requests + [current_time]
        else:
            # First request from this client
            self.clients[client_ip] = [current_time]
        
        # Process the request
        response = await call_next(request)
        
        # Add rate limiting headers to successful responses
        if client_ip in self.clients:
            recent_requests = [
                req_time for req_time in self.clients[client_ip] 
                if current_time - req_time < self.period
            ]
            remaining = max(0, self.calls - len(recent_requests))
            
            response.headers["X-RateLimit-Limit"] = str(self.calls)
            response.headers["X-RateLimit-Period"] = str(self.period)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response
    
    def _cleanup_old_entries(self, current_time: float):
        """Remove old entries from the clients dictionary."""
        for client_ip in list(self.clients.keys()):
            # Keep only recent requests
            recent_requests = [
                req_time for req_time in self.clients[client_ip] 
                if current_time - req_time < self.period
            ]
            
            if recent_requests:
                self.clients[client_ip] = recent_requests
            else:
                # Remove client if no recent requests
                del self.clients[client_ip]