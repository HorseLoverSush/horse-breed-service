"""
Demonstration script for efficient error handling in the Horse Breed Service.

This script shows examples of how the new error handling system works:
1. Custom exceptions with detailed context
2. Automatic HTTP status code mapping
3. Structured error responses
4. Request tracking and logging
5. Database error handling
"""
import asyncio
import json
import sys
from typing import Dict, Any

# Add the app directory to the Python path for imports
sys.path.append('.')

from app.core.exceptions import (
    NotFoundError, 
    ConflictError, 
    ValidationError, 
    DatabaseError,
    create_http_exception
)
from app.core.logging import setup_logging, get_logger


def demonstrate_custom_exceptions():
    """Demonstrate the custom exception system."""
    print("🔍 DEMONSTRATING CUSTOM EXCEPTIONS")
    print("=" * 50)
    
    # 1. NotFoundError
    print("\n1. NotFoundError Example:")
    try:
        raise NotFoundError(
            resource="Horse breed",
            identifier=999,
            details={"operation": "get_by_id", "table": "horse_breeds"}
        )
    except NotFoundError as e:
        print(f"   Exception: {e}")
        print(f"   Error Code: {e.error_code}")
        print(f"   Resource: {e.resource}")
        print(f"   Identifier: {e.identifier}")
        print(f"   Details: {e.details}")
        
        # Show HTTP exception conversion
        http_exc = create_http_exception(e, "req-123")
        print(f"   HTTP Status: {http_exc.status_code}")
        print(f"   HTTP Detail: {json.dumps(http_exc.detail, indent=2)}")
    
    # 2. ConflictError
    print("\n2. ConflictError Example:")
    try:
        raise ConflictError(
            message="Horse breed with name 'Arabian' already exists",
            conflicting_field="name",
            details={
                "existing_breed_id": 1,
                "attempted_name": "Arabian",
                "operation": "create"
            }
        )
    except ConflictError as e:
        print(f"   Exception: {e}")
        print(f"   Error Code: {e.error_code}")
        print(f"   Conflicting Field: {e.conflicting_field}")
        
        http_exc = create_http_exception(e, "req-124")
        print(f"   HTTP Status: {http_exc.status_code}")
        print(f"   HTTP Detail: {json.dumps(http_exc.detail, indent=2)}")
    
    # 3. ValidationError
    print("\n3. ValidationError Example:")
    try:
        raise ValidationError(
            message="Invalid height value: must be positive",
            field="height",
            details={
                "provided_value": -50,
                "min_value": 0,
                "max_value": 300
            }
        )
    except ValidationError as e:
        print(f"   Exception: {e}")
        print(f"   Error Code: {e.error_code}")
        print(f"   Field: {e.field}")
        
        http_exc = create_http_exception(e, "req-125")
        print(f"   HTTP Status: {http_exc.status_code}")
        print(f"   HTTP Detail: {json.dumps(http_exc.detail, indent=2)}")
    
    # 4. DatabaseError
    print("\n4. DatabaseError Example:")
    try:
        raise DatabaseError(
            message="Connection to database failed",
            operation="create_breed",
            details={
                "database_url": "postgresql://localhost:5432/horse_db",
                "timeout": 30,
                "retry_count": 3
            }
        )
    except DatabaseError as e:
        print(f"   Exception: {e}")
        print(f"   Error Code: {e.error_code}")
        print(f"   Operation: {e.operation}")
        
        http_exc = create_http_exception(e, "req-126")
        print(f"   HTTP Status: {http_exc.status_code}")
        print(f"   HTTP Detail: {json.dumps(http_exc.detail, indent=2)}")


def demonstrate_error_response_structure():
    """Show the standardized error response structure."""
    print("\n\n📋 STANDARDIZED ERROR RESPONSE STRUCTURE")
    print("=" * 50)
    
    sample_error_responses = [
        {
            "name": "Validation Error",
            "response": {
                "error": {
                    "request_id": "req-12345-abcde",
                    "error_code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "field": "name",
                    "details": {
                        "validation_errors": [
                            {
                                "field": "name",
                                "message": "Field required",
                                "type": "missing",
                                "input": None
                            }
                        ]
                    },
                    "timestamp": "2025-09-28T10:30:45.123Z"
                }
            }
        },
        {
            "name": "Not Found Error",
            "response": {
                "error": {
                    "request_id": "req-67890-fghij",
                    "error_code": "RESOURCE_NOT_FOUND",
                    "message": "Horse breed with identifier '999' not found",
                    "resource": "Horse breed",
                    "identifier": "999",
                    "details": {
                        "operation": "get_by_id"
                    },
                    "timestamp": "2025-09-28T10:31:20.456Z"
                }
            }
        },
        {
            "name": "Database Error",
            "response": {
                "error": {
                    "request_id": "req-11111-klmno",
                    "error_code": "DATABASE_ERROR",
                    "message": "Failed to create horse breed",
                    "operation": "create_breed",
                    "details": {
                        "database_error": "Connection timeout after 30 seconds"
                    },
                    "timestamp": "2025-09-28T10:32:10.789Z"
                }
            }
        }
    ]
    
    for example in sample_error_responses:
        print(f"\n{example['name']}:")
        print(json.dumps(example['response'], indent=2))


def demonstrate_logging_integration():
    """Show how logging integrates with error handling."""
    print("\n\n📝 LOGGING INTEGRATION")
    print("=" * 50)
    
    # Initialize logging
    setup_logging()
    logger = get_logger("demo")
    
    print("\n1. Basic Logging Examples:")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    print("\n2. Structured Logging with Context:")
    logger.info(
        "User action performed",
        extra={
            "user_id": 12345,
            "action": "create_breed",
            "breed_name": "Friesian",
            "request_id": "req-demo-001"
        }
    )
    
    print("\n3. Error Logging with Exception:")
    try:
        raise ValueError("This is a test exception")
    except ValueError as e:
        logger.error(
            "Operation failed with validation error",
            extra={
                "operation": "create_breed",
                "breed_name": "Invalid Breed",
                "error_type": e.__class__.__name__,
                "request_id": "req-demo-002"
            },
            exc_info=True
        )


def demonstrate_middleware_features():
    """Show what the middleware provides."""
    print("\n\n🔧 MIDDLEWARE FEATURES")
    print("=" * 50)
    
    features = [
        {
            "name": "Request Tracking Middleware",
            "features": [
                "✅ Generates unique request IDs for tracing",
                "✅ Logs incoming requests with metadata",
                "✅ Measures request processing time",
                "✅ Adds standard headers (X-Request-ID, X-Process-Time)",
                "✅ Handles unhandled exceptions gracefully"
            ]
        },
        {
            "name": "Security Middleware", 
            "features": [
                "✅ Adds security headers (X-Content-Type-Options, X-Frame-Options, etc.)",
                "✅ HSTS header for HTTPS connections",
                "✅ XSS protection headers",
                "✅ Referrer policy enforcement"
            ]
        },
        {
            "name": "Rate Limiting Middleware",
            "features": [
                "✅ In-memory rate limiting (100 requests/minute by default)",
                "✅ Per-client IP tracking",
                "✅ Automatic cleanup of old entries", 
                "✅ Rate limit headers in responses",
                "✅ Graceful rate limit exceeded responses"
            ]
        }
    ]
    
    for feature_group in features:
        print(f"\n{feature_group['name']}:")
        for feature in feature_group['features']:
            print(f"  {feature}")


def main():
    """Run all demonstrations."""
    print("🐎 HORSE BREED SERVICE - EFFICIENT ERROR HANDLING DEMONSTRATION")
    print("=" * 70)
    
    demonstrate_custom_exceptions()
    demonstrate_error_response_structure()
    demonstrate_logging_integration()
    demonstrate_middleware_features()
    
    print("\n\n🎯 KEY BENEFITS OF THIS ERROR HANDLING SYSTEM:")
    print("=" * 70)
    benefits = [
        "✅ Consistent error response format across all endpoints",
        "✅ Detailed error context for better debugging",
        "✅ Automatic HTTP status code mapping",
        "✅ Request tracking with unique IDs", 
        "✅ Structured JSON logging for easy parsing",
        "✅ Performance monitoring built-in",
        "✅ Security headers automatically added",
        "✅ Rate limiting to prevent abuse",
        "✅ Centralized exception handling (no boilerplate in endpoints)",
        "✅ Easy to extend with new exception types",
        "✅ Production-ready logging with file rotation",
        "✅ Database error handling with rollback support"
    ]
    
    for benefit in benefits:
        print(f"  {benefit}")
    
    print(f"\n🚀 The system is now ready for production use!")
    print(f"📁 Check the 'logs' directory for structured log files")
    print(f"🔍 All errors include request IDs for easy tracing")
    print(f"📊 Performance metrics are logged automatically")


if __name__ == "__main__":
    main()