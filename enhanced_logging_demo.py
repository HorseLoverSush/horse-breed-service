"""
Enhanced Logging Demonstration for the Horse Breed Service.

This script demonstrates the advanced logging capabilities:
1. Structured JSON logging with correlation IDs
2. Performance monitoring and metrics
3. Business event logging
4. Security event detection
5. Async logging for high performance
6. Log sampling and filtering
7. Multiple log destinations
8. Context-aware logging
"""
import asyncio
import json
import sys
import time
from pathlib import Path

# Add the app directory to the Python path for imports
sys.path.append('.')

from app.core.enhanced_logging import (
    setup_enhanced_logging,
    get_logger,
    set_correlation_id,
    log_business_event,
    log_security_event,
    log_performance_metric,
    get_metrics_summary,
    log_performance,
    LoggingContext
)


def demonstrate_basic_logging():
    """Demonstrate basic enhanced logging features."""
    print("🔍 BASIC ENHANCED LOGGING")
    print("=" * 50)
    
    # Initialize enhanced logging
    setup_enhanced_logging()
    logger = get_logger("demo.basic")
    
    print("\n1. Basic logging with context:")
    logger.info("Service started successfully")
    logger.warning("Configuration parameter missing, using default")
    logger.error("Failed to connect to external service")
    
    print("\n2. Logging with correlation IDs:")
    # Set correlation context
    request_id = set_correlation_id(user_id="user123", session_id="session456")
    print(f"   Request ID: {request_id}")
    
    logger.info("User authenticated successfully", extra={
        "authentication_method": "OAuth2",
        "login_duration_ms": 234
    })
    
    logger.warning("Invalid input provided", extra={
        "field": "email",
        "provided_value": "invalid-email",
        "validation_rule": "email_format"
    })


def demonstrate_performance_logging():
    """Demonstrate performance monitoring and metrics."""
    print("\n\n⚡ PERFORMANCE MONITORING")
    print("=" * 50)
    
    logger = get_logger("demo.performance")
    
    print("\n1. Performance decorator example:")
    
    @log_performance("database_query", threshold_ms=100.0, include_args=True)
    def simulate_database_query(table_name: str, query_type: str = "SELECT"):
        """Simulate a database query with random delay."""
        import random
        time.sleep(random.uniform(0.05, 0.3))  # 50-300ms delay
        return f"Query result from {table_name}"
    
    # Test the decorated function
    result = simulate_database_query("horse_breeds", "SELECT")
    print(f"   Query result: {result}")
    
    print("\n2. Manual performance metrics:")
    start_time = time.time()
    time.sleep(0.1)  # Simulate work
    execution_time = (time.time() - start_time) * 1000
    
    log_performance_metric(
        logger, 
        "cache_operation", 
        execution_time, 
        "ms",
        operation_type="read",
        cache_hit=True
    )
    
    print("\n3. Logging context manager:")
    with LoggingContext("data_processing", logger, batch_size=100, processor="v2"):
        time.sleep(0.05)  # Simulate processing
        logger.info("Processing batch completed", extra={"records_processed": 100})


def demonstrate_business_events():
    """Demonstrate business event logging."""
    print("\n\n📊 BUSINESS EVENT LOGGING")
    print("=" * 50)
    
    logger = get_logger("demo.business")
    
    print("\n1. User actions:")
    log_business_event(
        logger,
        "user_registration",
        {
            "user_id": "user789",
            "registration_method": "email",
            "account_type": "premium",
            "referral_source": "google_ads"
        },
        user_agent="Mozilla/5.0...",
        ip_address="192.168.1.100"
    )
    
    print("\n2. System events:")
    log_business_event(
        logger,
        "data_export_completed",
        {
            "export_id": "exp_456",
            "format": "CSV",
            "record_count": 1500,
            "file_size_mb": 2.3,
            "duration_seconds": 45
        }
    )
    
    print("\n3. Financial events:")
    log_business_event(
        logger,
        "payment_processed",
        {
            "transaction_id": "txn_789",
            "amount": 29.99,
            "currency": "USD",
            "payment_method": "credit_card",
            "status": "completed"
        },
        merchant_id="merchant123"
    )


def demonstrate_security_logging():
    """Demonstrate security event detection and logging."""
    print("\n\n🔒 SECURITY EVENT LOGGING")
    print("=" * 50)
    
    print("\n1. Authentication events:")
    log_security_event(
        "failed_login_attempt",
        {
            "username": "admin",
            "ip_address": "10.0.0.1",
            "user_agent": "curl/7.68.0",
            "attempt_count": 5
        },
        level="warning",
        source_ip="10.0.0.1"
    )
    
    print("\n2. Authorization events:")
    log_security_event(
        "unauthorized_access_attempt",
        {
            "user_id": "user456",
            "requested_resource": "/admin/users",
            "user_role": "standard",
            "required_role": "admin"
        },
        level="error"
    )
    
    print("\n3. Suspicious activity:")
    log_security_event(
        "rate_limit_exceeded",
        {
            "client_ip": "203.0.113.1",
            "endpoint": "/api/v1/breeds",
            "request_count": 150,
            "time_window": "60s",
            "limit": 100
        },
        level="critical"
    )


def demonstrate_structured_data():
    """Demonstrate structured data logging."""
    print("\n\n📋 STRUCTURED DATA LOGGING")
    print("=" * 50)
    
    logger = get_logger("demo.structured")
    
    print("\n1. Complex nested data:")
    user_profile = {
        "user_id": "user123",
        "profile": {
            "name": "John Doe",
            "email": "john@example.com",
            "preferences": {
                "theme": "dark",
                "notifications": {
                    "email": True,
                    "push": False,
                    "sms": True
                }
            }
        },
        "metadata": {
            "created_at": "2023-01-15T10:30:00Z",
            "last_login": "2023-09-28T08:15:30Z",
            "login_count": 45
        }
    }
    
    logger.info("User profile loaded", extra={"user_profile": user_profile})
    
    print("\n2. Array data:")
    api_metrics = {
        "endpoint": "/api/v1/breeds",
        "response_times_ms": [45, 67, 23, 89, 34, 56, 78],
        "status_codes": {"200": 145, "404": 3, "500": 1},
        "top_user_agents": [
            "Mozilla/5.0 (Chrome)",
            "Mozilla/5.0 (Firefox)", 
            "PostmanRuntime/7.29.0"
        ]
    }
    
    logger.info("API metrics collected", extra={"metrics": api_metrics})


def demonstrate_log_files():
    """Show the different log files created."""
    print("\n\n📁 LOG FILES GENERATED")
    print("=" * 50)
    
    log_dir = Path("logs")
    if log_dir.exists():
        log_files = list(log_dir.glob("*.log"))
        
        print(f"\nLog directory: {log_dir.absolute()}")
        print(f"Number of log files: {len(log_files)}")
        
        for log_file in sorted(log_files):
            size_mb = log_file.stat().st_size / (1024 * 1024)
            print(f"  📄 {log_file.name} ({size_mb:.2f} MB)")
            
            # Show first few lines of each log file
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:2]  # First 2 lines
                    if lines:
                        print(f"      Sample: {lines[0].strip()[:100]}...")
            except Exception as e:
                print(f"      Error reading file: {e}")
    else:
        print("No log directory found. Run the application first.")


def demonstrate_metrics_summary():
    """Show metrics collection summary."""
    print("\n\n📊 METRICS SUMMARY")
    print("=" * 50)
    
    # Simulate some metrics
    from app.core.enhanced_logging import record_request_metrics
    
    # Record some sample metrics
    endpoints = [
        ("/api/v1/breeds", "GET", 200, 0.045),
        ("/api/v1/breeds", "GET", 200, 0.067),
        ("/api/v1/breeds/1", "GET", 404, 0.023),
        ("/api/v1/breeds", "POST", 201, 0.234),
        ("/api/v1/breeds/2", "PUT", 200, 0.156),
        ("/api/v1/breeds/3", "DELETE", 204, 0.089),
    ]
    
    for endpoint, method, status, response_time in endpoints:
        record_request_metrics(endpoint, method, status, response_time)
    
    # Get and display metrics summary
    summary = get_metrics_summary()
    print(json.dumps(summary, indent=2))


async def demonstrate_async_logging():
    """Demonstrate async logging capabilities."""
    print("\n\n🔄 ASYNC LOGGING DEMONSTRATION")
    print("=" * 50)
    
    logger = get_logger("demo.async")
    
    print("\n1. Concurrent logging operations:")
    
    async def async_operation(operation_id: int):
        """Simulate an async operation with logging.""" 
        request_id = set_correlation_id()
        
        logger.info(f"Starting async operation {operation_id}", extra={
            "operation_id": operation_id,
            "operation_type": "data_processing"
        })
        
        # Simulate async work
        await asyncio.sleep(0.1)
        
        logger.info(f"Completed async operation {operation_id}", extra={
            "operation_id": operation_id,
            "status": "success",
            "processing_time_ms": 100
        })
    
    # Run multiple async operations concurrently
    tasks = [async_operation(i) for i in range(5)]
    await asyncio.gather(*tasks)
    
    print("   ✅ Concurrent operations completed with correlation tracking")


def main():
    """Run all enhanced logging demonstrations."""
    print("🐎 HORSE BREED SERVICE - ENHANCED LOGGING DEMONSTRATION")
    print("=" * 70)
    
    demonstrate_basic_logging()
    demonstrate_performance_logging()
    demonstrate_business_events()
    demonstrate_security_logging()
    demonstrate_structured_data()
    demonstrate_log_files()
    demonstrate_metrics_summary()
    
    # Run async demonstration
    asyncio.run(demonstrate_async_logging())
    
    print("\n\n🎯 ENHANCED LOGGING FEATURES:")
    print("=" * 70)
    features = [
        "✅ Structured JSON logging with rich context",
        "✅ Correlation IDs for request tracking across services",
        "✅ Automatic performance monitoring with thresholds",
        "✅ Business event logging for analytics",
        "✅ Security event detection and alerting",
        "✅ Async file handlers for high-performance logging",
        "✅ Log sampling to reduce volume in production",
        "✅ Multiple log destinations (console, files, metrics)",
        "✅ Context managers for operation logging",
        "✅ Automatic system metrics collection on errors",
        "✅ Log rotation with configurable sizes and counts",
        "✅ Filtering and enrichment of log events",
        "✅ Integration with monitoring systems",
        "✅ Thread-safe and async-safe logging",
        "✅ Configurable log levels per component"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print(f"\n🚀 Production Benefits:")
    print(f"  📊 Complete observability with correlation tracking")
    print(f"  🔍 Easy debugging with structured context")
    print(f"  📈 Performance insights and bottleneck detection")
    print(f"  🔒 Security monitoring and threat detection")
    print(f"  📉 Reduced storage costs with intelligent sampling")
    print(f"  ⚡ High performance with async processing")
    print(f"  🔧 Easy integration with monitoring tools")


if __name__ == "__main__":
    main()