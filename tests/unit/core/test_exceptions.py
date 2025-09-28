"""
Working unit tests for custom exception classes.

These tests match the actual implementation of our exception classes.
"""

import pytest
from fastapi import status
from unittest.mock import Mock, patch

from app.core.exceptions import (
    HorseBreedServiceException,
    NotFoundError,
    ConflictError,
    ValidationError,
    DatabaseError,
    ExternalServiceError,
    AuthenticationError,
    AuthorizationError,
    RateLimitError,
    map_exception_to_http_status,
    create_http_exception
)


class TestHorseBreedServiceException:
    """Test the base service exception class."""
    
    def test_base_exception_creation(self):
        """Test basic exception creation."""
        exception = HorseBreedServiceException(
            message="Test error",
            error_code="TEST_ERROR"
        )
        
        assert exception.message == "Test error"
        assert exception.error_code == "TEST_ERROR"
        assert exception.details == {}
        assert str(exception) == "Test error"
    
    def test_base_exception_with_details(self):
        """Test exception creation with details."""
        details = {"field": "name", "value": "invalid"}
        exception = HorseBreedServiceException(
            message="Validation failed",
            error_code="VALIDATION_ERROR",
            details=details
        )
        
        assert exception.message == "Validation failed"
        assert exception.error_code == "VALIDATION_ERROR"
        assert exception.details == details
    
    def test_base_exception_default_error_code(self):
        """Test exception with default error code."""
        exception = HorseBreedServiceException("Test message")
        
        assert exception.message == "Test message"
        assert exception.error_code == "GENERIC_ERROR"
        assert exception.details == {}
    
    def test_base_exception_inheritance(self):
        """Test that base exception inherits from Exception."""
        exception = HorseBreedServiceException("Test")
        
        assert isinstance(exception, Exception)
        assert isinstance(exception, HorseBreedServiceException)


class TestNotFoundError:
    """Test NotFoundError exception."""
    
    def test_not_found_error_creation(self):
        """Test NotFoundError creation with resource and identifier."""
        error = NotFoundError("HorseBreed", 123)
        
        assert "HorseBreed with identifier '123' not found" in error.message
        assert error.error_code == "RESOURCE_NOT_FOUND"
        assert error.resource == "HorseBreed"
        assert error.identifier == 123
        assert isinstance(error, HorseBreedServiceException)
    
    def test_not_found_error_with_string_identifier(self):
        """Test NotFoundError with string identifier."""
        error = NotFoundError("User", "john_doe")
        
        assert "User with identifier 'john_doe' not found" in error.message
        assert error.resource == "User"
        assert error.identifier == "john_doe"
    
    def test_not_found_error_with_details(self):
        """Test NotFoundError with additional details."""
        details = {"query": "name='Arabian'"}
        error = NotFoundError("HorseBreed", 456, details=details)
        
        assert error.details == details
        assert error.resource == "HorseBreed"
        assert error.identifier == 456


class TestConflictError:
    """Test ConflictError exception."""
    
    def test_conflict_error_creation(self):
        """Test ConflictError creation."""
        error = ConflictError("Resource already exists")
        
        assert error.message == "Resource already exists"
        assert error.error_code == "RESOURCE_CONFLICT"
        assert error.conflicting_field is None
        assert isinstance(error, HorseBreedServiceException)
    
    def test_conflict_error_with_field(self):
        """Test ConflictError with conflicting field."""
        error = ConflictError("Name already exists", conflicting_field="name")
        
        assert error.message == "Name already exists"
        assert error.conflicting_field == "name"
        assert error.error_code == "RESOURCE_CONFLICT"
    
    def test_conflict_error_with_details(self):
        """Test ConflictError with details."""
        details = {"existing_id": 123, "attempted_name": "Arabian"}
        error = ConflictError("Duplicate name", details=details)
        
        assert error.details == details


class TestValidationError:
    """Test ValidationError exception."""
    
    def test_validation_error_creation(self):
        """Test ValidationError creation."""
        error = ValidationError("Invalid input")
        
        assert error.message == "Invalid input"
        assert error.error_code == "VALIDATION_ERROR"
        assert error.field is None
        assert isinstance(error, HorseBreedServiceException)
    
    def test_validation_error_with_field(self):
        """Test ValidationError with field."""
        error = ValidationError("Name is required", field="name")
        
        assert error.message == "Name is required"
        assert error.field == "name"
        assert error.error_code == "VALIDATION_ERROR"
    
    def test_validation_error_with_details(self):
        """Test ValidationError with details."""
        details = {"min_length": 3, "max_length": 100}
        error = ValidationError("Name length invalid", field="name", details=details)
        
        assert error.field == "name"
        assert error.details == details


class TestDatabaseError:
    """Test DatabaseError exception."""
    
    def test_database_error_creation(self):
        """Test DatabaseError creation."""
        error = DatabaseError("Connection failed", "connect")
        
        assert error.message == "Connection failed"
        assert error.error_code == "DATABASE_ERROR"
        assert error.operation == "connect"
        assert isinstance(error, HorseBreedServiceException)
    
    def test_database_error_with_details(self):
        """Test DatabaseError with details."""
        details = {"host": "localhost", "port": 5432}
        error = DatabaseError("Cannot connect to database", "connect", details=details)
        
        assert error.operation == "connect"
        assert error.details == details


class TestExternalServiceError:
    """Test ExternalServiceError exception."""
    
    def test_external_service_error_creation(self):
        """Test ExternalServiceError creation."""
        error = ExternalServiceError("payment_api", "Service unavailable")
        
        assert "External service 'payment_api' error: Service unavailable" in error.message
        assert error.error_code == "EXTERNAL_SERVICE_ERROR"
        assert error.service == "payment_api"
        assert isinstance(error, HorseBreedServiceException)
    
    def test_external_service_error_with_details(self):
        """Test ExternalServiceError with details."""
        details = {"status_code": 503, "retry_after": 30}
        error = ExternalServiceError("api", "Timeout", details=details)
        
        assert error.service == "api"
        assert error.details == details


class TestAuthenticationError:
    """Test AuthenticationError exception."""
    
    def test_authentication_error_default(self):
        """Test AuthenticationError with default message."""
        error = AuthenticationError()
        
        assert error.message == "Authentication failed"
        assert error.error_code == "AUTHENTICATION_ERROR"
        assert isinstance(error, HorseBreedServiceException)
    
    def test_authentication_error_custom_message(self):
        """Test AuthenticationError with custom message."""
        error = AuthenticationError("Invalid credentials")
        
        assert error.message == "Invalid credentials"
        assert error.error_code == "AUTHENTICATION_ERROR"
    
    def test_authentication_error_with_details(self):
        """Test AuthenticationError with details."""
        details = {"method": "basic", "user": "john"}
        error = AuthenticationError("Login failed", details=details)
        
        assert error.details == details


class TestAuthorizationError:
    """Test AuthorizationError exception."""
    
    def test_authorization_error_default(self):
        """Test AuthorizationError with default message."""
        error = AuthorizationError()
        
        assert error.message == "Insufficient permissions"
        assert error.error_code == "AUTHORIZATION_ERROR"
        assert isinstance(error, HorseBreedServiceException)
    
    def test_authorization_error_custom_message(self):
        """Test AuthorizationError with custom message."""
        error = AuthorizationError("Access denied")
        
        assert error.message == "Access denied"
        assert error.error_code == "AUTHORIZATION_ERROR"
    
    def test_authorization_error_with_details(self):
        """Test AuthorizationError with details."""
        details = {"required_role": "admin", "user_role": "user"}
        error = AuthorizationError("Admin access required", details=details)
        
        assert error.details == details


class TestRateLimitError:
    """Test RateLimitError exception."""
    
    def test_rate_limit_error_default(self):
        """Test RateLimitError with default message."""
        error = RateLimitError()
        
        assert error.message == "Rate limit exceeded"
        assert error.error_code == "RATE_LIMIT_EXCEEDED"
        assert error.retry_after is None
        assert isinstance(error, HorseBreedServiceException)
    
    def test_rate_limit_error_with_retry_after(self):
        """Test RateLimitError with retry_after."""
        error = RateLimitError("Too many requests", retry_after=60)
        
        assert error.message == "Too many requests"
        assert error.retry_after == 60
    
    def test_rate_limit_error_with_details(self):
        """Test RateLimitError with details."""
        details = {"limit": 100, "window": "1h", "current": 105}
        error = RateLimitError(details=details)
        
        assert error.details == details


class TestExceptionMapping:
    """Test HTTP status code mapping."""
    
    def test_exception_status_mapping(self):
        """Test that exceptions map to correct HTTP status codes."""
        test_cases = [
            (ValidationError("test"), status.HTTP_400_BAD_REQUEST),
            (NotFoundError("Resource", 1), status.HTTP_404_NOT_FOUND),
            (ConflictError("test"), status.HTTP_409_CONFLICT),
            (DatabaseError("test", "op"), status.HTTP_500_INTERNAL_SERVER_ERROR),
            (ExternalServiceError("api", "test"), status.HTTP_502_BAD_GATEWAY),
            (AuthenticationError("test"), status.HTTP_401_UNAUTHORIZED),
            (AuthorizationError("test"), status.HTTP_403_FORBIDDEN),
            (RateLimitError("test"), status.HTTP_429_TOO_MANY_REQUESTS),
        ]
        
        for exception, expected_status in test_cases:
            status_code = map_exception_to_http_status(exception)
            assert status_code == expected_status
    
    def test_unknown_exception_mapping(self):
        """Test that unknown exceptions map to 500."""
        # Create a custom exception that's not in the mapping
        class CustomException(HorseBreedServiceException):
            pass
        
        exception = CustomException("test")
        status_code = map_exception_to_http_status(exception)
        assert status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestHTTPExceptionCreation:
    """Test HTTP exception creation."""
    
    def test_create_http_exception_basic(self):
        """Test creating HTTP exception from custom exception."""
        custom_error = ValidationError("Invalid name", field="name")
        http_exception = create_http_exception(custom_error)
        
        assert http_exception.status_code == status.HTTP_400_BAD_REQUEST
        assert http_exception.detail["error_code"] == "VALIDATION_ERROR"
        assert http_exception.detail["message"] == "Invalid name"
        assert http_exception.detail["field"] == "name"
    
    def test_create_http_exception_with_request_id(self):
        """Test creating HTTP exception with request ID."""
        custom_error = NotFoundError("User", 123)
        http_exception = create_http_exception(custom_error, request_id="req-123")
        
        assert http_exception.detail["request_id"] == "req-123"
        assert http_exception.detail["resource"] == "User"
        assert http_exception.detail["identifier"] == "123"
    
    def test_create_http_exception_with_details(self):
        """Test creating HTTP exception preserves details."""
        details = {"constraint": "unique", "table": "users"}
        custom_error = ConflictError("Duplicate entry", details=details)
        http_exception = create_http_exception(custom_error)
        
        assert http_exception.detail["details"] == details
        assert http_exception.status_code == status.HTTP_409_CONFLICT
    
    def test_create_http_exception_headers(self):
        """Test that HTTP exception includes proper headers."""
        custom_error = RateLimitError("Too many requests", retry_after=60)
        http_exception = create_http_exception(custom_error)
        
        assert http_exception.headers["X-Error-Code"] == "RATE_LIMIT_EXCEEDED"
        assert http_exception.detail["retry_after"] == 60


class TestExceptionInheritance:
    """Test exception inheritance hierarchy."""
    
    def test_all_exceptions_inherit_from_base(self):
        """Test that all custom exceptions inherit from base."""
        exceptions = [
            NotFoundError("test", 1),
            ConflictError("test"),
            ValidationError("test"),
            DatabaseError("test", "op"),
            ExternalServiceError("api", "test"),
            AuthenticationError("test"),
            AuthorizationError("test"), 
            RateLimitError("test"),
        ]
        
        for exc in exceptions:
            assert isinstance(exc, HorseBreedServiceException)
            assert isinstance(exc, Exception)
    
    def test_exception_str_representation(self):
        """Test string representation of exceptions."""
        error = ValidationError("Name is required", field="name")
        assert str(error) == "Name is required"
        
        error = NotFoundError("User", 123)
        assert "User with identifier '123' not found" in str(error)


@pytest.mark.performance
class TestExceptionPerformance:
    """Performance tests for exception creation."""
    
    def test_exception_creation_performance(self):
        """Test that exception creation is fast."""
        import time
        
        start_time = time.time()
        
        # Create many exceptions
        for i in range(1000):
            NotFoundError("Resource", i)
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        # Should create 1000 exceptions in less than 1 second
        assert elapsed < 1.0
    
    def test_http_exception_creation_performance(self):
        """Test HTTP exception creation performance."""
        import time
        
        start_time = time.time()
        
        # Create many HTTP exceptions
        for i in range(500):
            error = ValidationError(f"Error {i}", field="test")
            create_http_exception(error, request_id=f"req-{i}")
        
        end_time = time.time() 
        elapsed = end_time - start_time
        
        # Should create 500 HTTP exceptions in less than 1 second
        assert elapsed < 1.0