# Test Configuration for Horse Breed Service
# This file configures pytest and testing behavior

import os
import sys
import pytest
import asyncio
from pathlib import Path

# Add the app directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent / "app"))

# Test environment configuration
os.environ["TESTING"] = "1"
os.environ["LOG_LEVEL"] = "DEBUG"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_horse_breeds.db"

# Configure asyncio for pytest
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "monitoring: mark test as a monitoring test"
    )
    config.addinivalue_line(
        "markers", "error_handling: mark test as an error handling test"
    )
    config.addinivalue_line(
        "markers", "logging: mark test as a logging test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )

# Test collection configuration
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add default markers."""
    for item in items:
        # Add unit test marker to tests in unit/ directory
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        # Add integration test marker to tests in integration/ directory
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)