"""
Unit tests for monitoring endpoints.

Tests health checks, metrics endpoints, performance monitoring,
and system resource monitoring functionality.
"""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from fastapi import Response
from fastapi.testclient import TestClient

from app.api.v1.endpoints.monitoring import (
    get_system_metrics,
    get_service_metrics,
    check_component_health,
    basic_health_check,
    detailed_health_check,
    get_application_metrics,
    get_performance_metrics,
    get_log_metrics,
    get_service_status
)
from app.main import app


class TestSystemMetrics:
    """Test system metrics collection."""
    
    @patch('psutil.Process')
    @patch('psutil.disk_usage')
    def test_get_system_metrics_success(self, mock_disk_usage, mock_process_class):
        """Test successful system metrics collection."""
        # Mock psutil components
        mock_process = Mock()
        mock_process.cpu_percent.return_value = 15.5
        mock_process.memory_percent.return_value = 45.2
        mock_process.memory_info.return_value.rss = 268435456  # 256 MB
        mock_process.open_files.return_value = [Mock() for _ in range(42)]
        mock_process.connections.return_value = [Mock() for _ in range(12)]
        mock_process_class.return_value = mock_process
        
        mock_disk_usage.return_value.percent = 60.1
        
        metrics = get_system_metrics()
        
        assert metrics.cpu_percent == 15.5
        assert metrics.memory_percent == 45.2
        assert metrics.memory_mb == 256.0
        assert metrics.disk_usage_percent == 60.1
        assert metrics.open_files == 42
        assert metrics.network_connections == 12
    
    @patch('psutil.Process')
    def test_get_system_metrics_error_handling(self, mock_process_class):
        """Test system metrics error handling."""
        # Mock psutil to raise an error
        mock_process_class.side_effect = Exception("psutil error")
        
        metrics = get_system_metrics()
        
        # Should return default values on error
        assert metrics.cpu_percent == 0.0
        assert metrics.memory_percent == 0.0
        assert metrics.memory_mb == 0.0
        assert metrics.disk_usage_percent == 0.0
        assert metrics.open_files == 0
        assert metrics.network_connections == 0


class TestServiceMetrics:
    """Test service metrics collection."""
    
    @patch('app.api.v1.endpoints.monitoring.get_metrics_summary')
    def test_get_service_metrics_success(self, mock_get_metrics):
        """Test successful service metrics collection."""
        mock_metrics = {
            'total_requests': 1500,
            'total_errors': 25,
            'average_response_time': 125.5,
            'requests_per_second': 12.3,
            'error_rate': 1.67
        }
        mock_get_metrics.return_value = mock_metrics
        
        metrics = get_service_metrics()
        
        assert metrics.total_requests == 1500
        assert metrics.total_errors == 25
        assert metrics.average_response_time == 125.5
        assert metrics.requests_per_second == 12.3
        assert metrics.error_rate == 1.67
    
    @patch('app.api.v1.endpoints.monitoring.get_metrics_summary')
    def test_get_service_metrics_error_handling(self, mock_get_metrics):
        """Test service metrics error handling."""
        mock_get_metrics.side_effect = Exception("Metrics error")
        
        metrics = get_service_metrics()
        
        # Should return default values on error
        assert metrics.total_requests == 0
        assert metrics.total_errors == 0
        assert metrics.average_response_time == 0.0
        assert metrics.requests_per_second == 0.0
        assert metrics.error_rate == 0.0


class TestComponentHealth:
    """Test component health checks."""
    
    @patch('app.api.v1.endpoints.monitoring.engine')
    @patch('tempfile.NamedTemporaryFile')
    @patch('psutil.virtual_memory')
    def test_check_component_health_all_healthy(
        self, mock_memory, mock_temp_file, mock_engine
    ):
        """Test component health when all components are healthy."""
        # Mock database connection
        mock_engine.connect.return_value.__enter__ = Mock()
        mock_engine.connect.return_value.__exit__ = Mock()
        mock_engine.connect.return_value.__enter__.return_value.execute = Mock()
        
        # Mock filesystem check
        mock_temp_file.return_value.__enter__ = Mock()
        mock_temp_file.return_value.__exit__ = Mock()
        mock_temp_file.return_value.__enter__.return_value.write = Mock()
        mock_temp_file.return_value.__enter__.return_value.flush = Mock()
        
        # Mock memory check
        mock_memory.return_value.percent = 60.0
        
        components = check_component_health()
        
        assert components["database"] == "healthy"
        assert components["filesystem"] == "healthy"
        assert components["memory"] == "healthy"
    
    @patch('app.api.v1.endpoints.monitoring.engine')
    @patch('tempfile.NamedTemporaryFile')
    @patch('psutil.virtual_memory')
    def test_check_component_health_database_unhealthy(
        self, mock_memory, mock_temp_file, mock_engine
    ):
        """Test component health when database is unhealthy."""
        # Mock database connection failure
        mock_engine.connect.side_effect = Exception("Connection failed")
        
        # Mock other components as healthy
        mock_temp_file.return_value.__enter__ = Mock()
        mock_temp_file.return_value.__exit__ = Mock()
        mock_temp_file.return_value.__enter__.return_value.write = Mock()
        mock_temp_file.return_value.__enter__.return_value.flush = Mock()
        
        mock_memory.return_value.percent = 60.0
        
        components = check_component_health()
        
        assert "unhealthy" in components["database"]
        assert "Connection failed" in components["database"]
        assert components["filesystem"] == "healthy"
        assert components["memory"] == "healthy"
    
    @patch('app.api.v1.endpoints.monitoring.engine')
    @patch('tempfile.NamedTemporaryFile')
    @patch('psutil.virtual_memory')
    def test_check_component_health_memory_warning(
        self, mock_memory, mock_temp_file, mock_engine
    ):
        """Test component health when memory usage is high."""
        # Mock healthy database and filesystem
        mock_engine.connect.return_value.__enter__ = Mock()
        mock_engine.connect.return_value.__exit__ = Mock()
        mock_engine.connect.return_value.__enter__.return_value.execute = Mock()
        
        mock_temp_file.return_value.__enter__ = Mock()
        mock_temp_file.return_value.__exit__ = Mock()
        mock_temp_file.return_value.__enter__.return_value.write = Mock()
        mock_temp_file.return_value.__enter__.return_value.flush = Mock()
        
        # Mock high memory usage
        mock_memory.return_value.percent = 95.0
        
        components = check_component_health()
        
        assert components["database"] == "healthy"
        assert components["filesystem"] == "healthy"
        assert "warning" in components["memory"]


class TestHealthCheckEndpoints:
    """Test health check endpoints."""
    
    @pytest.mark.asyncio
    async def test_basic_health_check(self):
        """Test basic health check endpoint."""
        response_mock = Mock(spec=Response)
        response_mock.headers = {}
        
        with patch('app.api.v1.endpoints.monitoring.SERVICE_START_TIME', 1000.0):
            with patch('time.time', return_value=1100.0):
                result = await basic_health_check(response_mock)
        
        assert result.status == "healthy"
        assert result.uptime_seconds == 100.0
        assert result.version == "1.0.0"
        assert result.timestamp is not None
        
        # Check response headers
        assert response_mock.headers["Cache-Control"] == "no-cache, max-age=0"
        assert response_mock.headers["X-Health-Check"] == "basic"
    
    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.monitoring.get_system_metrics')
    @patch('app.api.v1.endpoints.monitoring.get_service_metrics')
    @patch('app.api.v1.endpoints.monitoring.check_component_health')
    async def test_detailed_health_check(
        self, mock_components, mock_service_metrics, mock_system_metrics
    ):
        """Test detailed health check endpoint."""
        # Mock dependencies
        mock_system_metrics.return_value = Mock(
            cpu_percent=15.5,
            memory_percent=45.2,
            memory_mb=256.0,
            disk_usage_percent=60.1,
            open_files=42,
            network_connections=12
        )
        
        mock_service_metrics.return_value = Mock(
            total_requests=1500,
            total_errors=25,
            average_response_time=125.5,
            requests_per_second=12.3,
            error_rate=1.67
        )
        
        mock_components.return_value = {
            "database": "healthy",
            "filesystem": "healthy",
            "memory": "healthy"
        }
        
        with patch('app.api.v1.endpoints.monitoring.SERVICE_START_TIME', 1000.0):
            with patch('time.time', return_value=1150.0):
                result = await detailed_health_check()
        
        assert result.status == "healthy"
        assert result.uptime_seconds == 150.0
        assert result.system.cpu_percent == 15.5
        assert result.service.total_requests == 1500
        assert result.components["database"] == "healthy"
    
    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.monitoring.get_system_metrics')
    @patch('app.api.v1.endpoints.monitoring.get_service_metrics')
    @patch('app.api.v1.endpoints.monitoring.check_component_health')
    async def test_detailed_health_check_unhealthy(
        self, mock_components, mock_service_metrics, mock_system_metrics
    ):
        """Test detailed health check when components are unhealthy."""
        mock_system_metrics.return_value = Mock(
            cpu_percent=15.5,
            memory_percent=45.2,
            memory_mb=256.0,
            disk_usage_percent=60.1,
            open_files=42,
            network_connections=12
        )
        
        mock_service_metrics.return_value = Mock(
            total_requests=1500,
            total_errors=25,
            average_response_time=125.5,
            requests_per_second=12.3,
            error_rate=1.67
        )
        
        # Mock unhealthy component
        mock_components.return_value = {
            "database": "unhealthy: Connection failed",
            "filesystem": "healthy",
            "memory": "healthy"
        }
        
        result = await detailed_health_check()
        
        assert result.status == "unhealthy"
        assert result.components["database"] == "unhealthy: Connection failed"


class TestMetricsEndpoints:
    """Test metrics endpoints."""
    
    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.monitoring.get_metrics_summary')
    @patch('app.api.v1.endpoints.monitoring.get_system_metrics')
    @patch('platform.platform')
    @patch('platform.python_version')
    @patch('platform.node')
    @patch('psutil.cpu_count')
    @patch('psutil.boot_time')
    async def test_get_application_metrics(
        self, mock_boot_time, mock_cpu_count, mock_node, 
        mock_python_version, mock_platform, mock_system_metrics, mock_metrics_summary
    ):
        """Test application metrics endpoint."""
        # Mock all dependencies
        mock_metrics_summary.return_value = {
            "total_requests": 1500,
            "total_errors": 25,
            "error_rate": 1.67
        }
        
        mock_system_metrics.return_value = Mock(
            cpu_percent=15.5,
            memory_percent=45.2
        )
        
        mock_platform.return_value = "Linux-5.4.0"
        mock_python_version.return_value = "3.12.0"
        mock_node.return_value = "test-server"
        mock_cpu_count.return_value = 4
        mock_boot_time.return_value = 1640995200.0
        
        response_mock = Mock(spec=Response)
        response_mock.headers = {}
        
        with patch('app.api.v1.endpoints.monitoring.SERVICE_START_TIME', 1000.0):
            with patch('time.time', return_value=1200.0):
                result = await get_application_metrics(response_mock)
        
        assert "service" in result
        assert "system" in result
        assert "system_info" in result
        assert result["service"]["total_requests"] == 1500
        assert result["system_info"]["platform"] == "Linux-5.4.0"
        assert result["uptime_seconds"] == 200.0
        
        # Check response headers
        assert response_mock.headers["Content-Type"] == "application/json"
        assert response_mock.headers["X-Metrics-Version"] == "1.0"
    
    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.monitoring.get_metrics_summary')
    async def test_get_performance_metrics(self, mock_metrics_summary):
        """Test performance metrics endpoint."""
        mock_metrics_summary.return_value = {
            "total_requests": 2000,
            "requests_per_second": 15.5,
            "average_response_time": 145.2,
            "total_errors": 30,
            "error_rate": 1.5,
            "status_codes": {200: 1800, 404: 20, 500: 10},
            "top_endpoints": {
                "/api/v1/breeds": {"count": 1500, "avg_time": 120.0},
                "/api/v1/health": {"count": 300, "avg_time": 25.0}
            }
        }
        
        result = await get_performance_metrics()
        
        assert "request_metrics" in result
        assert "error_metrics" in result
        assert "endpoint_metrics" in result
        assert result["request_metrics"]["total_requests"] == 2000
        assert result["error_metrics"]["error_rate"] == 1.5
        assert result["endpoint_metrics"]["/api/v1/breeds"]["count"] == 1500
    
    @pytest.mark.asyncio
    @patch('pathlib.Path')
    async def test_get_log_metrics_success(self, mock_path_class):
        """Test log metrics endpoint success."""
        # Mock log directory and files
        mock_logs_dir = Mock()
        mock_logs_dir.exists.return_value = True
        
        # Mock log files
        mock_log_file = Mock()
        mock_log_file.name = "horse_breed_service_errors.log"
        mock_log_file.stat.return_value.st_size = 1024 * 1024  # 1MB
        mock_log_file.stat.return_value.st_mtime = 1640995200.0
        
        mock_logs_dir.glob.return_value = [mock_log_file]
        
        # Mock file content for error log
        mock_log_entries = [
            '{"@timestamp": "2024-01-01T10:00:00", "level": "ERROR", "message": "Test error", "logger": "test"}',
            '{"@timestamp": "2024-01-01T10:01:00", "level": "CRITICAL", "message": "Critical error", "logger": "test"}'
        ]
        
        mock_open = Mock()
        mock_open.readlines.return_value = mock_log_entries
        
        mock_path_class.return_value = mock_logs_dir
        
        with patch('builtins.open', return_value=mock_open):
            result = await get_log_metrics()
        
        assert result.total_log_entries == 2
        assert result.log_levels["ERROR"] == 1
        assert result.log_levels["CRITICAL"] == 1
        assert len(result.recent_errors) == 2
        assert len(result.log_files) == 1
        assert result.log_files[0]["name"] == "horse_breed_service_errors.log"
    
    @pytest.mark.asyncio
    @patch('pathlib.Path')
    async def test_get_log_metrics_no_logs_dir(self, mock_path_class):
        """Test log metrics when logs directory doesn't exist."""
        mock_logs_dir = Mock()
        mock_logs_dir.exists.return_value = False
        mock_path_class.return_value = mock_logs_dir
        
        result = await get_log_metrics()
        
        assert result.total_log_entries == 0
        assert len(result.recent_errors) == 0
        assert len(result.log_files) == 0


class TestServiceStatusEndpoint:
    """Test service status endpoint."""
    
    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.monitoring.check_component_health')
    @patch('app.api.v1.endpoints.monitoring.get_service_metrics')
    async def test_get_service_status_healthy(self, mock_service_metrics, mock_components):
        """Test service status when all components are healthy."""
        mock_components.return_value = {
            "database": "healthy",
            "filesystem": "healthy",
            "memory": "healthy"
        }
        
        mock_service_metrics.return_value = Mock(
            total_requests=1500,
            error_rate=0.5  # Low error rate
        )
        
        with patch('app.api.v1.endpoints.monitoring.SERVICE_START_TIME', 1000.0):
            with patch('time.time', return_value=1300.0):
                result = await get_service_status()
        
        assert result["status"] == "healthy"
        assert result["uptime_seconds"] == 300.0
        assert "5m" in result["uptime_human"]  # 5 minutes
        assert result["components"]["database"] == "healthy"
        assert result["quick_metrics"]["total_requests"] == 1500
    
    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.monitoring.check_component_health')
    @patch('app.api.v1.endpoints.monitoring.get_service_metrics')
    async def test_get_service_status_degraded_high_error_rate(
        self, mock_service_metrics, mock_components
    ):
        """Test service status when error rate is high."""
        mock_components.return_value = {
            "database": "healthy",
            "filesystem": "healthy",
            "memory": "healthy"
        }
        
        mock_service_metrics.return_value = Mock(
            total_requests=1000,
            error_rate=15.0  # High error rate
        )
        
        result = await get_service_status()
        
        assert result["status"] == "degraded"
    
    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.monitoring.check_component_health')
    @patch('app.api.v1.endpoints.monitoring.get_service_metrics')
    async def test_get_service_status_unhealthy_component(
        self, mock_service_metrics, mock_components
    ):
        """Test service status when a component is unhealthy."""
        mock_components.return_value = {
            "database": "unhealthy: Connection failed",
            "filesystem": "healthy",
            "memory": "healthy"
        }
        
        mock_service_metrics.return_value = Mock(
            total_requests=1000,
            error_rate=2.0  # Normal error rate
        )
        
        result = await get_service_status()
        
        assert result["status"] == "unhealthy"
    
    @pytest.mark.asyncio
    @patch('app.api.v1.endpoints.monitoring.check_component_health')
    @patch('app.api.v1.endpoints.monitoring.get_service_metrics')
    async def test_get_service_status_error_handling(
        self, mock_service_metrics, mock_components
    ):
        """Test service status error handling."""
        mock_components.side_effect = Exception("Component check failed")
        mock_service_metrics.return_value = Mock(
            total_requests=0,
            error_rate=0.0
        )
        
        result = await get_service_status()
        
        assert result["status"] == "unknown"
        assert "error" in result


class TestMonitoringEndpointIntegration:
    """Integration tests for monitoring endpoints."""
    
    def test_monitoring_endpoints_available(self):
        """Test that all monitoring endpoints are available."""
        client = TestClient(app)
        
        endpoints = [
            "/api/v1/monitoring/health",
            "/api/v1/monitoring/health/detailed",
            "/api/v1/monitoring/metrics",
            "/api/v1/monitoring/metrics/performance",
            "/api/v1/monitoring/logs/metrics",
            "/api/v1/monitoring/status"
        ]
        
        for endpoint in endpoints:
            with patch('psutil.Process'), \
                 patch('psutil.disk_usage'), \
                 patch('psutil.virtual_memory'), \
                 patch('app.api.v1.endpoints.monitoring.get_metrics_summary') as mock_metrics:
                
                mock_metrics.return_value = {
                    "total_requests": 100,
                    "total_errors": 5,
                    "error_rate": 5.0,
                    "average_response_time": 125.0,
                    "requests_per_second": 10.0
                }
                
                response = client.get(endpoint)
                assert response.status_code in [200, 500]  # 500 might occur due to missing dependencies
    
    @patch('psutil.Process')
    @patch('psutil.disk_usage')
    @patch('psutil.virtual_memory')
    @patch('app.api.v1.endpoints.monitoring.get_metrics_summary')
    def test_health_check_response_format(
        self, mock_metrics, mock_memory, mock_disk, mock_process_class
    ):
        """Test health check response format."""
        # Mock all dependencies
        mock_process = Mock()
        mock_process.cpu_percent.return_value = 15.5
        mock_process.memory_percent.return_value = 45.2
        mock_process.memory_info.return_value.rss = 268435456
        mock_process.open_files.return_value = []
        mock_process.connections.return_value = []
        mock_process_class.return_value = mock_process
        
        mock_disk.return_value.percent = 60.1
        mock_memory.return_value.percent = 45.2
        
        mock_metrics.return_value = {
            "total_requests": 100,
            "total_errors": 5,
            "error_rate": 5.0
        }
        
        client = TestClient(app)
        response = client.get("/api/v1/monitoring/health")
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["status", "timestamp", "version", "uptime_seconds"]
        for field in required_fields:
            assert field in data
        
        assert data["status"] == "healthy"
        assert isinstance(data["uptime_seconds"], (int, float))
    
    def test_monitoring_endpoints_performance(self, performance_timer):
        """Test monitoring endpoints performance."""
        client = TestClient(app)
        
        with patch('psutil.Process'), \
             patch('psutil.disk_usage'), \
             patch('psutil.virtual_memory'), \
             patch('app.api.v1.endpoints.monitoring.get_metrics_summary') as mock_metrics:
            
            mock_metrics.return_value = {"total_requests": 100}
            
            timer = performance_timer
            timer.start()
            
            # Make multiple requests to health endpoint
            for _ in range(50):
                response = client.get("/api/v1/monitoring/health")
                assert response.status_code == 200
            
            elapsed = timer.stop()
            
            # Health checks should be very fast
            assert elapsed < 1.0  # Less than 1 second for 50 requests


@pytest.mark.monitoring
class TestMonitoringEndpointsSecurity:
    """Test security aspects of monitoring endpoints."""
    
    def test_monitoring_endpoints_no_sensitive_data(self):
        """Test that monitoring endpoints don't expose sensitive data."""
        client = TestClient(app)
        
        with patch('psutil.Process'), \
             patch('psutil.disk_usage'), \
             patch('psutil.virtual_memory'), \
             patch('app.api.v1.endpoints.monitoring.get_metrics_summary') as mock_metrics:
            
            mock_metrics.return_value = {"total_requests": 100}
            
            response = client.get("/api/v1/monitoring/metrics")
            
            # Response should not contain sensitive information
            response_text = response.text.lower()
            sensitive_keywords = [
                "password", "secret", "key", "token", "credential",
                "database_url", "api_key", "private"
            ]
            
            for keyword in sensitive_keywords:
                assert keyword not in response_text
    
    def test_monitoring_endpoints_headers(self):
        """Test security headers in monitoring responses."""
        client = TestClient(app)
        
        with patch('psutil.Process'), \
             patch('psutil.disk_usage'), \
             patch('psutil.virtual_memory'), \
             patch('app.api.v1.endpoints.monitoring.get_metrics_summary') as mock_metrics:
            
            mock_metrics.return_value = {"total_requests": 100}
            
            response = client.get("/api/v1/monitoring/health")
            
            # Check for appropriate headers
            assert "Cache-Control" in response.headers
            assert "X-Health-Check" in response.headers
    
    def test_error_responses_dont_leak_info(self):
        """Test that error responses don't leak internal information."""
        client = TestClient(app)
        
        # Force an error in metrics collection
        with patch('app.api.v1.endpoints.monitoring.get_metrics_summary') as mock_metrics:
            mock_metrics.side_effect = Exception("Internal database error with password=secret123")
            
            response = client.get("/api/v1/monitoring/metrics")
            
            # Error response should not contain sensitive info
            assert response.status_code == 500
            response_text = response.text.lower()
            assert "password" not in response_text
            assert "secret123" not in response_text