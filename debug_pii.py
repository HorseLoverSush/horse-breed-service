#!/usr/bin/env python3
"""
Debug script to understand what field names are being checked in PII filtering.
"""
from app.core.enhanced_logging import setup_enhanced_logging, get_logger

def debug_pii_filtering():
    """Debug PII filtering functionality."""
    
    # Setup logging
    setup_enhanced_logging()
    logger = get_logger(__name__)
    
    print("🔍 Debugging PII Filtering...")
    
    # Log with specific sensitive field names
    test_data = {
        "user_email": "john.doe@example.com",  # Contains 'email'
        "password": "secret123",                # Exact match 'password'
        "credit_card": "4532-1234-5678-9012",   # Exact match 'credit_card'
        "ssn": "123-45-6789",                   # Exact match 'ssn'
        "phone": "+1-555-123-4567",             # Exact match 'phone'
        "username": "johndoe"                   # Should NOT be filtered
    }
    
    print("\n📝 Logging data with these field names:")
    for field, value in test_data.items():
        print(f"  {field}: {value}")
    
    logger.warning("Test PII filtering", extra=test_data)
    
    print("\n✅ Debug test completed! Check logs to see what was filtered.")

if __name__ == "__main__":
    debug_pii_filtering()