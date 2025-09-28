#!/usr/bin/env python3
"""
Test script to verify PII filtering in the logging system.
This script demonstrates that sensitive data is properly filtered from logs.
"""
import asyncio
import time
from app.core.enhanced_logging import setup_enhanced_logging, get_logger, LoggingMiddleware

def test_pii_filtering():
    """Test PII filtering functionality."""
    
    # Setup logging
    setup_enhanced_logging()
    logger = get_logger(__name__)
    
    print("🧪 Testing PII Filtering System")
    print("=" * 50)
    
    # Test 1: Direct logging with sensitive data
    print("\n1. Testing direct logging with sensitive data...")
    logger.info("User login attempt", extra={
        "user_email": "john.doe@example.com",
        "password": "secret123",
        "credit_card": "4532-1234-5678-9012",
        "ssn": "123-45-6789",
        "phone": "+1-555-123-4567",
        "username": "johndoe"  # This should NOT be filtered
    })
    
    # Test 2: Test query string filtering
    print("\n2. Testing query string filtering...")
    middleware = LoggingMiddleware(None)
    
    test_queries = [
        "name=John&password=secret123&email=test@example.com",
        "search=horses&api_key=abc123&token=xyz789",
        "filter=active&phone=555-1234&normal_param=value"
    ]
    
    for query in test_queries:
        filtered = middleware._filter_query_string(query)
        print(f"Original: {query}")
        print(f"Filtered: {filtered}")
        print()
    
    # Test 3: Test header filtering
    print("\n3. Testing header filtering...")
    test_headers = {
        b'authorization': b'Bearer jwt-token-here',
        b'x-api-key': b'secret-api-key',
        b'content-type': b'application/json',
        b'user-agent': b'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        b'x-forwarded-for': b'192.168.1.1'
    }
    
    filtered_headers = middleware._filter_headers_for_logging(test_headers)
    for header, value in filtered_headers.items():
        print(f"{header}: {value}")
    
    print("\n✅ PII filtering test completed!")
    print("📝 Check the logs to verify sensitive data was filtered out.")
    print("🗂️  Log files are in: logs/horse_breed_service.log")

if __name__ == "__main__":
    test_pii_filtering()