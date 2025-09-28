"""
Integration tests for complete system validation.

Tests end-to-end functionality including database interactions,
error handling, logging, and monitoring in realistic scenarios.
"""

import pytest
import asyncio
import json
import time
import logging
from unittest.mock import patch, Mock
from httpx import AsyncClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import tempfile
import os

from app.main import app
from app.db.database import get_db, engine
from app.core.config import settings
from app.models.horse_breed import HorseBreed
from app.core.enhanced_logging import get_logger


@pytest.mark.integration
class TestSystemIntegration:
    """Integration tests for complete system functionality."""
    
    @pytest.fixture(autouse=True)
    async def setup_test_environment(self):
        """Set up test environment for integration tests."""
        # Set test environment
        os.environ["TESTING"] = "true"
        
        yield
        
        # Cleanup
        os.environ.pop("TESTING", None)
    
    @pytest.mark.asyncio
    async def test_complete_api_flow_with_database(self, test_db_session):
        """Test complete API flow with real database operations."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 1. Check health endpoint
            health_response = await client.get("/api/v1/monitoring/health")
            assert health_response.status_code == 200
            assert health_response.json()["status"] == "healthy"
            
            # 2. Create a new horse breed
            breed_data = {
                "name": "Integration Test Breed",
                "origin": "Test Country",
                "characteristics": {
                    "size": "medium",
                    "temperament": "calm",
                    "uses": ["riding", "testing"]
                },
                "description": "A breed created for integration testing"
            }
            
            create_response = await client.post("/api/v1/breeds", json=breed_data)
            assert create_response.status_code == 201
            created_breed = create_response.json()
            assert created_breed["name"] == "Integration Test Breed"
            breed_id = created_breed["id"]
            
            # 3. Retrieve the created breed
            get_response = await client.get(f"/api/v1/breeds/{breed_id}")
            assert get_response.status_code == 200
            retrieved_breed = get_response.json()
            assert retrieved_breed["name"] == "Integration Test Breed"
            
            # 4. Update the breed
            update_data = {
                "description": "Updated description for integration test"
            }
            update_response = await client.patch(f"/api/v1/breeds/{breed_id}", json=update_data)
            assert update_response.status_code == 200
            updated_breed = update_response.json()
            assert updated_breed["description"] == "Updated description for integration test"
            
            # 5. List all breeds (should include our test breed)
            list_response = await client.get("/api/v1/breeds")
            assert list_response.status_code == 200
            breeds_list = list_response.json()
            assert any(breed["id"] == breed_id for breed in breeds_list)
            
            # 6. Delete the breed
            delete_response = await client.delete(f"/api/v1/breeds/{breed_id}")
            assert delete_response.status_code == 204
            
            # 7. Verify deletion
            get_deleted_response = await client.get(f"/api/v1/breeds/{breed_id}")
            assert get_deleted_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_error_handling_integration(self):
        """Test error handling across the complete system."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Test 404 error
            response = await client.get("/api/v1/breeds/99999")
            assert response.status_code == 404
            error_data = response.json()
            assert "error_code" in error_data
            assert "message" in error_data
            assert "request_id" in error_data
            
            # Test validation error
            invalid_breed_data = {
                "name": "",  # Invalid empty name
                "origin": "Test"
            }
            response = await client.post("/api/v1/breeds", json=invalid_breed_data)
            assert response.status_code == 422
            error_data = response.json()
            assert "detail" in error_data
            
            # Test method not allowed
            response = await client.patch("/api/v1/breeds")  # PATCH without ID
            assert response.status_code == 405
    
    @pytest.mark.asyncio
    async def test_logging_integration(self, caplog):
        """Test logging integration across the system."""
        with caplog.at_level(logging.INFO):
            async with AsyncClient(app=app, base_url="http://test") as client:
                # Make request that should be logged
                response = await client.get("/api/v1/monitoring/health")
                assert response.status_code == 200
                
                # Check that request was logged
                log_records = [record for record in caplog.records if "GET" in record.message]
                assert len(log_records) > 0
                
                # Check log format includes correlation ID
                for record in log_records:
                    if hasattr(record, 'correlation_id'):
                        assert record.correlation_id is not None
    
    @pytest.mark.asyncio
    async def test_monitoring_integration(self):
        """Test monitoring endpoints integration."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Test basic health check
            health_response = await client.get("/api/v1/monitoring/health")
            assert health_response.status_code == 200
            health_data = health_response.json()
            assert health_data["status"] == "healthy"
            assert "uptime_seconds" in health_data
            
            # Test detailed health check
            detailed_response = await client.get("/api/v1/monitoring/health/detailed")
            assert detailed_response.status_code == 200
            detailed_data = detailed_response.json()
            assert "system" in detailed_data
            assert "service" in detailed_data
            assert "components" in detailed_data
            
            # Test metrics endpoint
            metrics_response = await client.get("/api/v1/monitoring/metrics")
            assert metrics_response.status_code == 200
            metrics_data = metrics_response.json()
            assert "service" in metrics_data
            assert "system" in metrics_data
            
            # Test service status
            status_response = await client.get("/api/v1/monitoring/status")
            assert status_response.status_code == 200
            status_data = status_response.json()
            assert "status" in status_data
            assert "uptime_seconds" in status_data


@pytest.mark.integration
class TestDatabaseIntegration:
    """Integration tests for database operations."""
    
    @pytest.mark.asyncio
    async def test_database_connection_handling(self):
        """Test database connection handling and error recovery."""
        # Test normal database operations
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/breeds")
            assert response.status_code == 200
        
        # Simulate database connection error
        with patch('app.db.database.engine.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database connection failed")
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/api/v1/breeds")
                assert response.status_code == 500
                error_data = response.json()
                assert "correlation_id" in error_data
    
    @pytest.mark.asyncio
    async def test_database_transaction_rollback(self, test_db_session):
        """Test database transaction rollback on errors."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create valid breed data
            breed_data = {
                "name": "Transaction Test Breed",
                "origin": "Test Country",
                "characteristics": {"size": "large"},
                "description": "Test breed for transaction rollback"
            }
            
            # Mock a database error during creation
            with patch('app.services.horse_breed_service.HorseBreedService.create_breed') as mock_create:
                mock_create.side_effect = Exception("Simulated database error")
                
                response = await client.post("/api/v1/breeds", json=breed_data)
                assert response.status_code == 500
                
                # Verify the breed was not created (transaction rolled back)
                list_response = await client.get("/api/v1/breeds")
                breeds = list_response.json()
                assert not any(breed["name"] == "Transaction Test Breed" for breed in breeds)
    
    @pytest.mark.asyncio
    async def test_concurrent_database_operations(self, test_db_session):
        """Test concurrent database operations."""
        async def create_breed(client, name):
            breed_data = {
                "name": f"Concurrent Breed {name}",
                "origin": "Test Country",
                "characteristics": {"size": "medium"},
                "description": f"Concurrent test breed {name}"
            }
            response = await client.post("/api/v1/breeds", json=breed_data)
            return response
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create multiple breeds concurrently
            tasks = []
            for i in range(5):
                task = create_breed(client, i)
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check that all requests were processed
            success_count = sum(1 for r in responses if hasattr(r, 'status_code') and r.status_code == 201)
            assert success_count >= 3  # Allow some failures due to concurrency


@pytest.mark.integration
class TestPerformanceIntegration:
    """Integration tests for performance monitoring."""
    
    @pytest.mark.asyncio
    async def test_response_time_monitoring(self):
        """Test response time monitoring integration."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            start_time = time.time()
            
            # Make multiple requests
            for _ in range(10):
                response = await client.get("/api/v1/monitoring/health")
                assert response.status_code == 200
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Check performance metrics endpoint
            metrics_response = await client.get("/api/v1/monitoring/metrics/performance")
            assert metrics_response.status_code == 200
            metrics_data = metrics_response.json()
            
            # Verify metrics are being collected
            assert "request_metrics" in metrics_data
            assert "total_requests" in metrics_data["request_metrics"]
    
    @pytest.mark.asyncio
    async def test_memory_usage_monitoring(self):
        """Test memory usage monitoring during operations."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Get initial metrics
            initial_response = await client.get("/api/v1/monitoring/metrics")
            initial_data = initial_response.json()
            initial_memory = initial_data.get("system", {}).get("memory_percent", 0)
            
            # Perform memory-intensive operations
            breed_data = {
                "name": "Memory Test Breed",
                "origin": "Test Country",
                "characteristics": {"size": "large", "data": "x" * 10000},  # Large data
                "description": "Test breed for memory monitoring"
            }
            
            # Create multiple breeds
            created_ids = []
            for i in range(20):
                breed_data["name"] = f"Memory Test Breed {i}"
                response = await client.post("/api/v1/breeds", json=breed_data)
                if response.status_code == 201:
                    created_ids.append(response.json()["id"])
            
            # Check metrics after operations
            final_response = await client.get("/api/v1/monitoring/metrics")
            final_data = final_response.json()
            
            # Memory metrics should be available
            assert "system" in final_data
            assert "memory_percent" in final_data["system"]
            
            # Cleanup created breeds
            for breed_id in created_ids:
                await client.delete(f"/api/v1/breeds/{breed_id}")


@pytest.mark.integration
class TestSecurityIntegration:
    """Integration tests for security features."""
    
    @pytest.mark.asyncio
    async def test_cors_headers_integration(self):
        """Test CORS headers in responses."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/monitoring/health")
            assert response.status_code == 200
            
            # Check for CORS headers (if configured)
            headers = response.headers
            # CORS headers might be added by middleware
            
    @pytest.mark.asyncio
    async def test_error_information_disclosure(self):
        """Test that errors don't disclose sensitive information."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Force a server error
            with patch('app.services.horse_breed_service.HorseBreedService.get_breeds') as mock_get:
                mock_get.side_effect = Exception("Database password is secret123!")
                
                response = await client.get("/api/v1/breeds")
                assert response.status_code == 500
                
                # Error response should not contain sensitive information
                response_text = response.text.lower()
                assert "password" not in response_text
                assert "secret123" not in response_text
    
    @pytest.mark.asyncio
    async def test_request_size_limits(self):
        """Test request size limits."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create very large request payload
            large_data = {
                "name": "Large Data Test",
                "origin": "Test Country",
                "characteristics": {"data": "x" * 1000000},  # 1MB of data
                "description": "Test breed with large data"
            }
            
            response = await client.post("/api/v1/breeds", json=large_data)
            # Should either succeed or fail gracefully with appropriate status
            assert response.status_code in [201, 413, 422, 500]


@pytest.mark.integration
class TestLoggingIntegration:
    """Integration tests for logging system."""
    
    @pytest.mark.asyncio
    async def test_structured_logging_integration(self, tmp_path):
        """Test structured logging integration."""
        # Create temporary log file
        log_file = tmp_path / "test_integration.log"
        
        # Configure logger to use temporary file
        logger = get_logger("test_integration")
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Make requests that should generate logs
            response = await client.get("/api/v1/monitoring/health")
            assert response.status_code == 200
            
            # Make request that causes error
            response = await client.get("/api/v1/breeds/99999")
            assert response.status_code == 404
        
        # Check log metrics endpoint
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/monitoring/logs/metrics")
            assert response.status_code == 200
            
            log_metrics = response.json()
            assert "total_log_entries" in log_metrics
            assert "log_levels" in log_metrics
    
    @pytest.mark.asyncio
    async def test_correlation_id_tracking(self):
        """Test correlation ID tracking across requests."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Make request and capture correlation ID
            response = await client.get("/api/v1/monitoring/health")
            assert response.status_code == 200
            
            # Correlation ID should be in response headers
            correlation_id = response.headers.get("X-Correlation-ID")
            if correlation_id:  # Only test if correlation ID is implemented
                assert len(correlation_id) > 0
                
                # Subsequent requests should have different correlation IDs
                response2 = await client.get("/api/v1/monitoring/health")
                correlation_id2 = response2.headers.get("X-Correlation-ID")
                if correlation_id2:
                    assert correlation_id != correlation_id2


@pytest.mark.integration
class TestSystemStress:
    """Stress tests for system integration."""
    
    @pytest.mark.asyncio
    async def test_concurrent_request_handling(self):
        """Test handling of concurrent requests."""
        async def make_request(client, endpoint):
            try:
                response = await client.get(endpoint)
                return response.status_code
            except Exception as e:
                return 500
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create concurrent requests
            tasks = []
            endpoints = [
                "/api/v1/monitoring/health",
                "/api/v1/monitoring/metrics",
                "/api/v1/breeds",
            ]
            
            for _ in range(50):  # 50 concurrent requests
                endpoint = endpoints[_ % len(endpoints)]
                task = make_request(client, endpoint)
                tasks.append(task)
            
            # Execute all requests concurrently
            status_codes = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Count successful responses
            success_count = sum(1 for code in status_codes if code == 200)
            
            # At least 80% should succeed
            assert success_count >= len(tasks) * 0.8
    
    @pytest.mark.asyncio
    async def test_resource_cleanup_under_load(self, test_db_session):
        """Test resource cleanup under load."""
        created_breeds = []
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            try:
                # Create many breeds rapidly
                for i in range(30):
                    breed_data = {
                        "name": f"Stress Test Breed {i}",
                        "origin": "Test Country",
                        "characteristics": {"size": "medium"},
                        "description": f"Stress test breed {i}"
                    }
                    
                    response = await client.post("/api/v1/breeds", json=breed_data)
                    if response.status_code == 201:
                        created_breeds.append(response.json()["id"])
                
                # Verify system is still responsive
                health_response = await client.get("/api/v1/monitoring/health")
                assert health_response.status_code == 200
                
            finally:
                # Cleanup created breeds
                for breed_id in created_breeds:
                    try:
                        await client.delete(f"/api/v1/breeds/{breed_id}")
                    except:
                        pass  # Ignore cleanup errors
    
    @pytest.mark.asyncio
    async def test_error_rate_under_stress(self):
        """Test error rate monitoring under stress conditions."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Generate mix of valid and invalid requests
            tasks = []
            
            # Valid requests
            for _ in range(20):
                task = client.get("/api/v1/monitoring/health")
                tasks.append(task)
            
            # Invalid requests
            for _ in range(10):
                task = client.get("/api/v1/breeds/invalid_id")
                tasks.append(task)
            
            # Execute all requests
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Count response types
            success_count = sum(1 for r in responses 
                              if hasattr(r, 'status_code') and r.status_code == 200)
            error_count = sum(1 for r in responses 
                            if hasattr(r, 'status_code') and r.status_code >= 400)
            
            assert success_count > 0
            assert error_count > 0
            
            # Check that metrics endpoint still works
            metrics_response = await client.get("/api/v1/monitoring/metrics/performance")
            assert metrics_response.status_code == 200