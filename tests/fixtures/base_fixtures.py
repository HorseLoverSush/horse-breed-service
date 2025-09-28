"""
Test fixtures and base classes for Horse Breed Service tests.

This module provides reusable fixtures, test data, and utilities
for comprehensive testing of the service.
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, AsyncGenerator, Generator
from httpx import AsyncClient
from fastapi.testclient import TestClient

# Import app components
from app.main import app
from app.core.config import get_settings
from app.core.enhanced_logging import get_logger, setup_logging
from app.db.database import get_db
from app.models.horse_breed import HorseBreed


# Test configuration
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_horse_breeds.db"
TEST_LOG_DIR = Path("test_logs")


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment configuration."""
    import os
    os.environ["TESTING"] = "1"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    
    # Create test logs directory
    TEST_LOG_DIR.mkdir(exist_ok=True)
    
    # Setup test logging
    setup_logging()
    
    yield
    
    # Cleanup
    if TEST_LOG_DIR.exists():
        shutil.rmtree(TEST_LOG_DIR, ignore_errors=True)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for the FastAPI app."""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.fixture
def mock_db_session():
    """Mock database session for unit tests."""
    mock_session = AsyncMock()
    mock_session.add = Mock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.close = AsyncMock()
    mock_session.execute = AsyncMock()
    mock_session.scalar = AsyncMock()
    return mock_session


@pytest.fixture
def sample_horse_breed_data() -> Dict[str, Any]:
    """Sample horse breed data for testing."""
    return {
        "name": "Arabian",
        "origin": "Arabian Peninsula",
        "description": "One of the oldest horse breeds, known for endurance and intelligence.",
        "characteristics": {
            "height": "14.1-15.2 hands",
            "weight": "380-430 kg",
            "temperament": "Intelligent, energetic, gentle",
            "coat_colors": ["Bay", "Chestnut", "Black", "Grey"],
            "life_expectancy": "25-35 years"
        },
        "physical_traits": {
            "head_shape": "Refined, wedge-shaped",
            "neck": "Arched and elegant",
            "body": "Compact and muscular",
            "legs": "Strong and well-formed"
        },
        "historical_info": {
            "developed_period": "Ancient times",
            "original_purpose": "War horse, desert travel",
            "notable_bloodlines": ["Egyptian", "Polish", "Russian"]
        },
        "care_requirements": {
            "exercise_needs": "High - daily exercise required",
            "dietary_needs": "Quality hay, grains, fresh water",
            "common_health_issues": "Generally healthy, some genetic conditions",
            "habitat_requirements": "Adaptable to various climates",
            "grooming_needs": "Regular brushing, hoof care"
        }
    }


@pytest.fixture
def invalid_horse_breed_data() -> Dict[str, Any]:
    """Invalid horse breed data for testing validation errors."""
    return {
        "name": "",  # Invalid: empty name
        "origin": None,  # Invalid: None origin
        "description": "x",  # Invalid: too short
        "characteristics": "not a dict",  # Invalid: wrong type
    }


@pytest.fixture
def mock_logger():
    """Mock logger for testing logging functionality."""
    logger = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.debug = Mock()
    logger.critical = Mock()
    return logger


@pytest.fixture
def temp_log_file():
    """Create a temporary log file for testing."""
    temp_file = tempfile.NamedTemporaryFile(mode='w+', suffix='.log', delete=False)
    temp_file.close()
    
    yield Path(temp_file.name)
    
    # Cleanup
    try:
        Path(temp_file.name).unlink()
    except FileNotFoundError:
        pass


@pytest.fixture
def mock_system_metrics():
    """Mock system metrics for monitoring tests."""
    return {
        "cpu_percent": 15.5,
        "memory_percent": 45.2,
        "memory_mb": 256.7,
        "disk_usage_percent": 60.1,
        "open_files": 42,
        "network_connections": 12
    }


@pytest.fixture
def mock_service_metrics():
    """Mock service metrics for monitoring tests."""
    return {
        "total_requests": 1500,
        "total_errors": 25,
        "average_response_time": 125.5,
        "requests_per_second": 12.3,
        "error_rate": 1.67
    }


@pytest.fixture
def correlation_id():
    """Generate a test correlation ID."""
    return "test_req_123456789abcdef"


@pytest.fixture
def mock_psutil():
    """Mock psutil for system monitoring tests."""
    with patch('psutil.Process') as mock_process_class:
        mock_process = Mock()
        mock_process.cpu_percent.return_value = 15.5
        mock_process.memory_percent.return_value = 45.2
        mock_process.memory_info.return_value = Mock(rss=268435456)  # 256 MB in bytes
        mock_process.open_files.return_value = [Mock() for _ in range(42)]
        mock_process.connections.return_value = [Mock() for _ in range(12)]
        mock_process_class.return_value = mock_process
        
        with patch('psutil.disk_usage') as mock_disk_usage:
            mock_disk_usage.return_value = Mock(percent=60.1)
            
            with patch('psutil.virtual_memory') as mock_virtual_memory:
                mock_virtual_memory.return_value = Mock(percent=45.2)
                
                yield {
                    'process': mock_process,
                    'disk_usage': mock_disk_usage,
                    'virtual_memory': mock_virtual_memory
                }


@pytest.fixture
async def mock_database_error():
    """Mock database error for testing error handling."""
    from sqlalchemy.exc import SQLAlchemyError
    return SQLAlchemyError("Test database error")


@pytest.fixture
def mock_correlation_middleware():
    """Mock correlation middleware for testing."""
    async def mock_middleware(request, call_next):
        request.state.correlation_id = "test_correlation_123"
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = request.state.correlation_id
        return response
    return mock_middleware


class TestDataFactory:
    """Factory class for creating test data."""
    
    @staticmethod
    def create_horse_breed(**overrides) -> Dict[str, Any]:
        """Create horse breed data with optional overrides."""
        base_data = {
            "name": "Test Breed",
            "origin": "Test Origin",
            "description": "A test horse breed for unit testing purposes.",
            "characteristics": {
                "height": "15-16 hands",
                "weight": "450-500 kg",
                "temperament": "Calm and friendly",
                "coat_colors": ["Brown", "Black"],
                "life_expectancy": "20-25 years"
            },
            "physical_traits": {
                "head_shape": "Well-proportioned",
                "neck": "Strong",
                "body": "Athletic",
                "legs": "Sturdy"
            },
            "historical_info": {
                "developed_period": "Modern times",
                "original_purpose": "Testing",
                "notable_bloodlines": ["Test Line A", "Test Line B"]
            },
            "care_requirements": {
                "exercise_needs": "Moderate",
                "dietary_needs": "Standard feed",
                "common_health_issues": "None known",
                "habitat_requirements": "Standard stable",
                "grooming_needs": "Regular"
            }
        }
        base_data.update(overrides)
        return base_data
    
    @staticmethod
    def create_multiple_horse_breeds(count: int = 3) -> list[Dict[str, Any]]:
        """Create multiple horse breed data entries."""
        breeds = []
        for i in range(count):
            breed = TestDataFactory.create_horse_breed(
                name=f"Test Breed {i+1}",
                origin=f"Test Origin {i+1}"
            )
            breeds.append(breed)
        return breeds


@pytest.fixture
def test_data_factory():
    """Provide access to the test data factory."""
    return TestDataFactory


# Custom assertions for testing
class CustomAssertions:
    """Custom assertion helpers for testing."""
    
    @staticmethod
    def assert_response_has_correlation_id(response):
        """Assert that response has correlation ID header."""
        assert "X-Correlation-ID" in response.headers
        correlation_id = response.headers["X-Correlation-ID"]
        assert len(correlation_id) > 0
        assert correlation_id.startswith(("req_", "test_"))
    
    @staticmethod
    def assert_error_response_format(response_json: Dict[str, Any]):
        """Assert error response follows expected format."""
        required_fields = ["error", "error_type", "message", "correlation_id", "timestamp"]
        for field in required_fields:
            assert field in response_json, f"Missing field: {field}"
        
        assert response_json["error"] is True
        assert isinstance(response_json["error_type"], str)
        assert isinstance(response_json["message"], str)
        assert len(response_json["correlation_id"]) > 0
    
    @staticmethod
    def assert_health_check_response(response_json: Dict[str, Any]):
        """Assert health check response format."""
        required_fields = ["status", "timestamp", "version", "uptime_seconds"]
        for field in required_fields:
            assert field in response_json, f"Missing field: {field}"
        
        assert response_json["status"] in ["healthy", "unhealthy", "degraded"]
        assert isinstance(response_json["uptime_seconds"], (int, float))
    
    @staticmethod
    def assert_metrics_response(response_json: Dict[str, Any]):
        """Assert metrics response format."""
        required_sections = ["service", "system", "system_info"]
        for section in required_sections:
            assert section in response_json, f"Missing section: {section}"


@pytest.fixture
def custom_assertions():
    """Provide access to custom assertion helpers."""
    return CustomAssertions


# Mock services for external dependencies
@pytest.fixture
def mock_external_services():
    """Mock external services for integration testing."""
    mocks = {}
    
    # Mock email service
    mocks['email'] = Mock()
    mocks['email'].send_alert = AsyncMock(return_value=True)
    
    # Mock webhook service
    mocks['webhook'] = Mock()
    mocks['webhook'].send_notification = AsyncMock(return_value={"status": "sent"})
    
    # Mock metrics backend
    mocks['metrics'] = Mock()
    mocks['metrics'].record_metric = Mock()
    mocks['metrics'].get_metrics = Mock(return_value={"requests": 100, "errors": 5})
    
    return mocks


# Performance testing helpers
@pytest.fixture
def performance_timer():
    """Timer for performance testing."""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.perf_counter()
        
        def stop(self):
            self.end_time = time.perf_counter()
            return self.elapsed
        
        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
    
    return Timer


# Async test utilities
class AsyncTestUtils:
    """Utilities for async testing."""
    
    @staticmethod
    async def wait_for_condition(condition_func, timeout=5.0, interval=0.1):
        """Wait for a condition to become true."""
        import asyncio
        start_time = asyncio.get_event_loop().time()
        
        while True:
            if await condition_func():
                return True
            
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise TimeoutError(f"Condition not met within {timeout} seconds")
            
            await asyncio.sleep(interval)
    
    @staticmethod
    async def run_concurrently(tasks, max_concurrent=10):
        """Run tasks concurrently with limited concurrency."""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def limited_task(task):
            async with semaphore:
                return await task
        
        return await asyncio.gather(*[limited_task(task) for task in tasks])


@pytest.fixture
def async_test_utils():
    """Provide access to async testing utilities."""
    return AsyncTestUtils