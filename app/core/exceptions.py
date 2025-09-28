"""
Custom exception classes for the Horse Breed Service.

This module defines custom exceptions that provide more specific error handling
and better user experience than generic exceptions.
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class HorseBreedServiceException(Exception):
    """Base exception class for the Horse Breed Service."""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = "GENERIC_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(HorseBreedServiceException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details
        )
        self.field = field


class NotFoundError(HorseBreedServiceException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, resource: str, identifier: Any, details: Optional[Dict[str, Any]] = None):
        message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(
            message=message,
            error_code="RESOURCE_NOT_FOUND",
            details=details
        )
        self.resource = resource
        self.identifier = identifier


class ConflictError(HorseBreedServiceException):
    """Raised when there's a conflict with existing data."""
    
    def __init__(self, message: str, conflicting_field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="RESOURCE_CONFLICT",
            details=details
        )
        self.conflicting_field = conflicting_field


class DatabaseError(HorseBreedServiceException):
    """Raised when database operations fail."""
    
    def __init__(self, message: str, operation: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details=details
        )
        self.operation = operation


class ExternalServiceError(HorseBreedServiceException):
    """Raised when external service calls fail."""
    
    def __init__(self, service: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"External service '{service}' error: {message}",
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details
        )
        self.service = service


class AuthenticationError(HorseBreedServiceException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            details=details
        )


class AuthorizationError(HorseBreedServiceException):
    """Raised when authorization fails."""
    
    def __init__(self, message: str = "Insufficient permissions", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            details=details
        )


class RateLimitError(HorseBreedServiceException):
    """Raised when rate limits are exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details
        )
        self.retry_after = retry_after


# HTTP Exception mapping for custom exceptions
def map_exception_to_http_status(exception: HorseBreedServiceException) -> int:
    """Map custom exceptions to appropriate HTTP status codes."""
    exception_status_map = {
        ValidationError: status.HTTP_400_BAD_REQUEST,
        NotFoundError: status.HTTP_404_NOT_FOUND,
        ConflictError: status.HTTP_409_CONFLICT,
        DatabaseError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ExternalServiceError: status.HTTP_502_BAD_GATEWAY,
        AuthenticationError: status.HTTP_401_UNAUTHORIZED,
        AuthorizationError: status.HTTP_403_FORBIDDEN,
        RateLimitError: status.HTTP_429_TOO_MANY_REQUESTS,
    }
    
    return exception_status_map.get(type(exception), status.HTTP_500_INTERNAL_SERVER_ERROR)


def create_http_exception(exception: HorseBreedServiceException, request_id: Optional[str] = None) -> HTTPException:
    """Create an HTTPException from a custom exception."""
    status_code = map_exception_to_http_status(exception)
    
    error_detail = {
        "error_code": exception.error_code,
        "message": exception.message,
        "details": exception.details,
    }
    
    if request_id:
        error_detail["request_id"] = request_id
    
    # Add specific fields for certain exception types
    if isinstance(exception, ValidationError) and exception.field:
        error_detail["field"] = exception.field
    elif isinstance(exception, NotFoundError):
        error_detail["resource"] = exception.resource
        error_detail["identifier"] = str(exception.identifier)
    elif isinstance(exception, ConflictError) and exception.conflicting_field:
        error_detail["conflicting_field"] = exception.conflicting_field
    elif isinstance(exception, DatabaseError):
        error_detail["operation"] = exception.operation
    elif isinstance(exception, ExternalServiceError):
        error_detail["service"] = exception.service
    elif isinstance(exception, RateLimitError) and exception.retry_after:
        error_detail["retry_after"] = exception.retry_after
    
    return HTTPException(
        status_code=status_code,
        detail=error_detail,
        headers={"X-Error-Code": exception.error_code} if exception.error_code else None
    )