"""
Global exception handlers for the Horse Breed Service.

This module provides centralized exception handling for consistent error responses
and proper logging across the entire application.
"""
import logging
import uuid
from typing import Dict, Any
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import (
    HorseBreedServiceException, 
    DatabaseError,
    create_http_exception
)
from app.core.enhanced_logging import get_logger, log_security_event

# Configure logger
logger = get_logger("error_handlers")


def generate_request_id() -> str:
    """Generate a unique request ID for tracking."""
    return str(uuid.uuid4())


def create_error_response(
    request_id: str,
    error_code: str,
    message: str,
    status_code: int,
    details: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Create a standardized error response."""
    return {
        "error": {
            "request_id": request_id,
            "error_code": error_code,
            "message": message,
            "details": details or {},
            "timestamp": None  # Will be set by middleware
        }
    }


async def custom_exception_handler(request: Request, exc: HorseBreedServiceException) -> JSONResponse:
    """Handle custom application exceptions."""
    request_id = getattr(request.state, 'request_id', generate_request_id())
    
    # Log the exception
    logger.error(
        f"Custom exception occurred: {exc.__class__.__name__}",
        extra={
            "request_id": request_id,
            "error_code": exc.error_code,
            "error_message": exc.message,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method,
        }
    )
    
    # Convert to HTTP exception and extract details
    http_exc = create_http_exception(exc, request_id)
    
    return JSONResponse(
        status_code=http_exc.status_code,
        content=http_exc.detail,
        headers=http_exc.headers or {}
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions with consistent formatting."""
    request_id = getattr(request.state, 'request_id', generate_request_id())
    
    # Log the exception
    logger.warning(
        f"HTTP exception: {exc.status_code}",
        extra={
            "request_id": request_id,
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": request.url.path,
            "method": request.method,
        }
    )
    
    # If detail is already a dict (from our custom exceptions), use it
    if isinstance(exc.detail, dict):
        error_response = exc.detail
        if "request_id" not in error_response:
            error_response["request_id"] = request_id
    else:
        # Convert simple string detail to standardized format
        error_response = create_error_response(
            request_id=request_id,
            error_code="HTTP_ERROR",
            message=str(exc.detail),
            status_code=exc.status_code
        )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response,
        headers=exc.headers or {}
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors."""
    request_id = getattr(request.state, 'request_id', generate_request_id())
    
    # Extract validation error details
    validation_errors = []
    for error in exc.errors():
        validation_errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
            "input": error.get("input")
        })
    
    # Log the validation error
    logger.warning(
        "Validation error occurred",
        extra={
            "request_id": request_id,
            "validation_errors": validation_errors,
            "path": request.url.path,
            "method": request.method,
        }
    )
    
    error_response = create_error_response(
        request_id=request_id,
        error_code="VALIDATION_ERROR",
        message="Request validation failed",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details={"validation_errors": validation_errors}
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle SQLAlchemy database exceptions."""
    request_id = getattr(request.state, 'request_id', generate_request_id())
    
    # Log the database error
    logger.error(
        f"Database error occurred: {exc.__class__.__name__}",
        extra={
            "request_id": request_id,
            "error": str(exc),
            "path": request.url.path,
            "method": request.method,
        },
        exc_info=True
    )
    
    # Handle specific database errors
    if isinstance(exc, IntegrityError):
        # Handle database constraint violations
        error_response = create_error_response(
            request_id=request_id,
            error_code="INTEGRITY_ERROR",
            message="Database constraint violation",
            status_code=status.HTTP_409_CONFLICT,
            details={"database_error": "A record with this data already exists or violates constraints"}
        )
        status_code = status.HTTP_409_CONFLICT
    else:
        # Generic database error
        error_response = create_error_response(
            request_id=request_id,
            error_code="DATABASE_ERROR",
            message="An internal database error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"database_error": "Please try again later"}
        )
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    return JSONResponse(
        status_code=status_code,
        content=error_response
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle any unhandled exceptions."""
    request_id = getattr(request.state, 'request_id', generate_request_id())
    
    # Log the unexpected error
    logger.error(
        f"Unhandled exception occurred: {exc.__class__.__name__}",
        extra={
            "request_id": request_id,
            "error": str(exc),
            "path": request.url.path,
            "method": request.method,
        },
        exc_info=True
    )
    
    error_response = create_error_response(
        request_id=request_id,
        error_code="INTERNAL_ERROR",
        message="An unexpected error occurred",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details={"error": "Please try again later or contact support"}
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response
    )


# Exception handler mapping
EXCEPTION_HANDLERS = {
    HorseBreedServiceException: custom_exception_handler,
    HTTPException: http_exception_handler,
    StarletteHTTPException: http_exception_handler,
    RequestValidationError: validation_exception_handler,
    SQLAlchemyError: sqlalchemy_exception_handler,
    Exception: generic_exception_handler,
}