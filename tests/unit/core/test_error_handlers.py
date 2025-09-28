"""
Unit tests for global exception handlers.

Tests the behavior of all global exception handlers,
error response formatting, and error logging.
"""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.error_handlers import (
    custom_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    generic_exception_handler,
    create_error_response,
    generate_request_id
)
from app.core.exceptions import (
    HorseBreedServiceException,
    NotFoundError,
    ConflictError,
    ValidationError,
    DatabaseError,
    AuthenticationError
)


class TestExceptionHandlers:
    """Test suite for global exception handlers."""
    
    @pytest.fixture
    def mock_request(self):
        """Create a mock request object."""
        request = Mock(spec=Request)
        request.method = "GET"
        request.url = Mock()
        request.url.path = "/api/v1/breeds/test"
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {"user-agent": "test-client"}
        request.state = Mock()
        request.state.correlation_id = "test_correlation_123"
        return request
    
    @pytest.fixture
    def mock_logger(self):
        """Mock logger for testing logging behavior."""
        with patch('app.core.error_handlers.logger') as mock_log:
            mock_log.error = Mock()
            mock_log.warning = Mock()
            mock_log.info = Mock()
            yield mock_log


class TestBaseExceptionHandler(TestExceptionHandlers):
    """Test the base service exception handler."""
    
    async def test_base_exception_handler_success(self, mock_request, mock_logger):
        """Test successful handling of BaseServiceException."""
        exception = NotFoundError(
            resource="horse_breed", 
            identifier="arabian"
        )
        
        response = await base_exception_handler(mock_request, exception)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 404
        
        # Parse response content
        content = json.loads(response.body.decode())
        
        # Verify response structure
        assert content["error"] is True
        assert content["error_type"] == "NotFoundError"
        assert "not found" in content["message"].lower()
        assert content["correlation_id"] == "test_correlation_123"
        assert content["path"] == "/api/v1/breeds/test"
        assert "timestamp" in content
        
        # Verify details are included
        assert "details" in content
        assert content["details"]["resource"] == "horse_breed"
        assert content["details"]["identifier"] == "arabian"
    
    async def test_base_exception_handler_without_correlation_id(self, mock_request, mock_logger):
        """Test handler when correlation ID is not available."""
        # Remove correlation ID from request state
        del mock_request.state.correlation_id
        
        exception = ValidationError("test", "field", "value")
        response = await base_exception_handler(mock_request, exception)
        
        content = json.loads(response.body.decode())
        
        # Should generate a correlation ID
        assert "correlation_id" in content
        assert content["correlation_id"] is not None
        assert len(content["correlation_id"]) > 0
    
    async def test_base_exception_handler_logging(self, mock_request, mock_logger):
        """Test that exceptions are properly logged."""
        exception = DatabaseError(
            message="Connection failed",
            operation="SELECT",
            table="horse_breeds"
        )
        
        await base_exception_handler(mock_request, exception)
        
        # Verify error was logged
        mock_logger.error.assert_called_once()
        log_call = mock_logger.error.call_args
        
        # Check log message contains important info
        log_message = log_call[0][0]
        assert "DatabaseError" in log_message
        assert "Connection failed" in log_message
    
    @pytest.mark.parametrize("exception_class,expected_status", [
        (NotFoundError, 404),
        (ConflictError, 409),
        (ValidationError, 422),
        (DatabaseError, 500),
        (AuthenticationError, 401),
    ])
    async def test_base_exception_handler_status_codes(
        self, mock_request, mock_logger, exception_class, expected_status
    ):
        """Test that different exceptions return correct status codes."""
        if exception_class == ValidationError:
            exception = exception_class("test", "field", "value")
        else:
            exception = exception_class("test message")
        
        response = await base_exception_handler(mock_request, exception)
        
        assert response.status_code == expected_status


class TestHTTPExceptionHandler(TestExceptionHandlers):
    """Test the FastAPI HTTPException handler."""
    
    async def test_http_exception_handler_success(self, mock_request, mock_logger):
        """Test successful handling of HTTPException."""
        exception = HTTPException(
            status_code=404,
            detail="Resource not found"
        )
        
        response = await http_exception_handler(mock_request, exception)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 404
        
        content = json.loads(response.body.decode())
        
        # Verify response structure
        assert content["error"] is True
        assert content["error_type"] == "HTTPException"
        assert content["message"] == "Resource not found"
        assert content["correlation_id"] == "test_correlation_123"
        assert content["path"] == "/api/v1/breeds/test"
    
    async def test_http_exception_handler_with_headers(self, mock_request, mock_logger):
        """Test HTTPException with custom headers."""
        exception = HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"Retry-After": "60"}
        )
        
        response = await http_exception_handler(mock_request, exception)
        
        # Custom headers should be preserved
        assert response.headers.get("Retry-After") == "60"
    
    @pytest.mark.parametrize("status_code,detail", [
        (400, "Bad Request"),
        (401, "Unauthorized"),
        (403, "Forbidden"),
        (404, "Not Found"),
        (422, "Validation Error"),
        (500, "Internal Server Error"),
    ])
    async def test_http_exception_handler_various_statuses(
        self, mock_request, mock_logger, status_code, detail
    ):
        """Test HTTP exception handler with various status codes."""
        exception = HTTPException(status_code=status_code, detail=detail)
        
        response = await http_exception_handler(mock_request, exception)
        
        assert response.status_code == status_code
        content = json.loads(response.body.decode())
        assert content["message"] == detail


class TestStarletteHTTPExceptionHandler(TestExceptionHandlers):
    """Test the Starlette HTTPException handler."""
    
    async def test_starlette_http_exception_handler(self, mock_request, mock_logger):
        """Test Starlette HTTPException handling."""
        exception = StarletteHTTPException(
            status_code=404,
            detail="Page not found"
        )
        
        response = await starlette_http_exception_handler(mock_request, exception)
        
        assert response.status_code == 404
        content = json.loads(response.body.decode())
        
        assert content["error"] is True
        assert content["error_type"] == "HTTPException"
        assert content["message"] == "Page not found"


class TestValidationExceptionHandler(TestExceptionHandlers):
    """Test the validation exception handler."""
    
    async def test_validation_exception_handler(self, mock_request, mock_logger):
        """Test validation exception handling."""
        from fastapi.exceptions import RequestValidationError
        from pydantic import ValidationError as PydanticValidationError
        
        # Create a mock validation error
        validation_errors = [
            {
                "loc": ("body", "name"),
                "msg": "field required",
                "type": "value_error.missing"
            },
            {
                "loc": ("body", "age"),
                "msg": "ensure this value is greater than 0",
                "type": "value_error.number.not_gt",
                "ctx": {"limit_value": 0}
            }
        ]
        
        # Mock the RequestValidationError
        exception = Mock(spec=RequestValidationError)
        exception.errors.return_value = validation_errors
        
        response = await validation_exception_handler(mock_request, exception)
        
        assert response.status_code == 422
        content = json.loads(response.body.decode())
        
        assert content["error"] is True
        assert content["error_type"] == "ValidationError"
        assert "validation failed" in content["message"].lower()
        assert "validation_errors" in content["details"]
        assert len(content["details"]["validation_errors"]) == 2
    
    async def test_validation_exception_handler_logging(self, mock_request, mock_logger):
        """Test that validation errors are logged."""
        from fastapi.exceptions import RequestValidationError
        
        validation_errors = [{"loc": ("name",), "msg": "required", "type": "missing"}]
        exception = Mock(spec=RequestValidationError)
        exception.errors.return_value = validation_errors
        
        await validation_exception_handler(mock_request, exception)
        
        # Verify warning was logged (validation errors are warnings, not errors)
        mock_logger.warning.assert_called_once()


class TestGeneralExceptionHandler(TestExceptionHandlers):
    """Test the general exception handler for unexpected errors."""
    
    async def test_general_exception_handler(self, mock_request, mock_logger):
        """Test handling of unexpected exceptions."""
        exception = ValueError("Unexpected error occurred")
        
        response = await general_exception_handler(mock_request, exception)
        
        assert response.status_code == 500
        content = json.loads(response.body.decode())
        
        assert content["error"] is True
        assert content["error_type"] == "InternalServerError"
        assert content["message"] == "An unexpected error occurred"
        # Original error details should not be exposed in production
        assert "details" not in content or content["details"] == {}
    
    async def test_general_exception_handler_logging(self, mock_request, mock_logger):
        """Test that unexpected exceptions are logged with full details."""
        exception = ZeroDivisionError("Division by zero")
        
        await general_exception_handler(mock_request, exception)
        
        # Verify error was logged
        mock_logger.error.assert_called_once()
        log_call = mock_logger.error.call_args
        
        # Should log the original exception details
        log_message = log_call[0][0]
        assert "ZeroDivisionError" in log_message
        assert "Division by zero" in log_message
    
    async def test_general_exception_handler_security(self, mock_request, mock_logger):
        """Test that sensitive information is not leaked in responses."""
        # Exception with potentially sensitive information
        exception = Exception("Database password: secret123, API key: key456")
        
        response = await general_exception_handler(mock_request, exception)
        
        content = json.loads(response.body.decode())
        
        # Sensitive information should not be in the response
        response_str = json.dumps(content)
        assert "secret123" not in response_str
        assert "key456" not in response_str
        assert "password" not in response_str.lower()


class TestErrorResponseFormat:
    """Test error response format consistency."""
    
    async def test_error_response_format_consistency(self):
        """Test that all error handlers return consistent format."""
        request = Mock(spec=Request)
        request.method = "POST"
        request.url = Mock()
        request.url.path = "/test"
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {}
        request.state = Mock()
        request.state.correlation_id = "test_123"
        
        # Test different exception handlers
        exceptions_and_handlers = [
            (NotFoundError("test"), base_exception_handler),
            (HTTPException(404, "Not found"), http_exception_handler),
            (ValueError("test"), general_exception_handler),
        ]
        
        required_fields = ["error", "error_type", "message", "correlation_id", "timestamp", "path"]
        
        for exception, handler in exceptions_and_handlers:
            response = await handler(request, exception)
            content = json.loads(response.body.decode())
            
            # Check all required fields are present
            for field in required_fields:
                assert field in content, f"Missing field '{field}' in {handler.__name__} response"
            
            # Check field types
            assert isinstance(content["error"], bool)
            assert content["error"] is True
            assert isinstance(content["error_type"], str)
            assert isinstance(content["message"], str)
            assert isinstance(content["correlation_id"], str)
            assert isinstance(content["timestamp"], str)
            assert isinstance(content["path"], str)


class TestErrorHandlerIntegration:
    """Test error handler integration scenarios."""
    
    async def test_correlation_id_propagation(self):
        """Test that correlation IDs are properly propagated through handlers."""
        request = Mock(spec=Request)
        request.method = "GET"
        request.url = Mock()
        request.url.path = "/test"
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {}
        request.state = Mock()
        
        test_correlation_id = "unique_test_correlation_id_123"
        request.state.correlation_id = test_correlation_id
        
        exception = NotFoundError("test resource")
        response = await base_exception_handler(request, exception)
        
        content = json.loads(response.body.decode())
        assert content["correlation_id"] == test_correlation_id
        
        # Also check response headers
        assert response.headers["X-Correlation-ID"] == test_correlation_id
    
    async def test_error_handler_performance(self, performance_timer):
        """Test that error handlers are performant."""
        request = Mock(spec=Request)
        request.method = "GET"
        request.url = Mock()
        request.url.path = "/test"
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {}
        request.state = Mock()
        request.state.correlation_id = "test_123"
        
        exception = DatabaseError("Complex database error with lots of details")
        
        timer = performance_timer
        timer.start()
        
        # Handle many errors
        for _ in range(100):
            await base_exception_handler(request, exception)
        
        elapsed = timer.stop()
        
        # Should be fast (less than 100ms for 100 error responses)
        assert elapsed < 0.1
    
    @patch('app.core.error_handlers.logger')
    async def test_error_context_enrichment(self, mock_logger):
        """Test that error context is enriched with request information."""
        request = Mock(spec=Request)
        request.method = "POST"
        request.url = Mock()
        request.url.path = "/api/v1/breeds"
        request.client = Mock()
        request.client.host = "192.168.1.100"
        request.headers = {
            "user-agent": "TestClient/1.0",
            "x-forwarded-for": "10.0.0.1"
        }
        request.state = Mock()
        request.state.correlation_id = "enrichment_test_123"
        
        exception = ValidationError("Invalid input", "name", "")
        
        await base_exception_handler(request, exception)
        
        # Verify logger was called with enriched context
        mock_logger.error.assert_called_once()
        log_call = mock_logger.error.call_args
        
        # Check that request details are included in logging
        log_kwargs = log_call[1] if len(log_call) > 1 else {}
        extra = log_kwargs.get('extra', {})
        
        # The logging should include request context
        assert 'correlation_id' in str(log_call) or 'correlation_id' in str(extra)


@pytest.mark.error_handling
class TestErrorHandlerEdgeCases:
    """Test edge cases and error conditions in error handlers."""
    
    async def test_handler_with_none_correlation_id(self):
        """Test handler behavior when correlation ID is None."""
        request = Mock(spec=Request)
        request.method = "GET"
        request.url = Mock()
        request.url.path = "/test"
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {}
        request.state = Mock()
        request.state.correlation_id = None
        
        exception = NotFoundError("test")
        response = await base_exception_handler(request, exception)
        
        content = json.loads(response.body.decode())
        
        # Should generate a new correlation ID
        assert content["correlation_id"] is not None
        assert len(content["correlation_id"]) > 0
    
    async def test_handler_with_missing_state(self):
        """Test handler behavior when request state is missing."""
        request = Mock(spec=Request)
        request.method = "GET"
        request.url = Mock()
        request.url.path = "/test"
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {}
        # No state attribute
        del request.state
        
        exception = NotFoundError("test")
        response = await base_exception_handler(request, exception)
        
        content = json.loads(response.body.decode())
        
        # Should handle gracefully and generate correlation ID
        assert content["correlation_id"] is not None
        assert len(content["correlation_id"]) > 0
    
    async def test_handler_with_circular_reference_in_details(self):
        """Test handler behavior with circular references in exception details."""
        # Create objects with circular references
        obj1 = {"name": "obj1"}
        obj2 = {"name": "obj2", "ref": obj1}
        obj1["ref"] = obj2
        
        request = Mock(spec=Request)
        request.method = "GET"
        request.url = Mock()
        request.url.path = "/test"
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {}
        request.state = Mock()
        request.state.correlation_id = "circular_test"
        
        # This would normally cause issues with JSON serialization
        exception = BaseServiceException("test", details={"circular": obj1})
        
        # Should handle gracefully without raising serialization errors
        response = await base_exception_handler(request, exception)
        
        assert response.status_code == 500
        content = json.loads(response.body.decode())
        assert content["error"] is True