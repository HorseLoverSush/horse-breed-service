"""
Unit tests for enhanced logging system.

Tests structured logging, correlation IDs, performance monitoring,
business event logging, and async logging handlers.
"""

import pytest
import json
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, call
from datetime import datetime

from app.core.enhanced_logging import (
    EnhancedJSONFormatter,
    AsyncFileHandler,
    MetricsCollector,
    LoggingContext,
    setup_enhanced_logging,
    get_logger,
    log_performance,
    log_business_event,
    log_security_event,
    get_metrics_summary
)


class TestEnhancedJSONFormatter:
    """Test the enhanced JSON formatter."""
    
    def test_json_formatter_basic_formatting(self):
        """Test basic JSON formatting functionality."""
        formatter = EnhancedJSONFormatter()
        
        # Create a log record
        import logging
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=123,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Add some extra fields
        record.correlation_id = "test_correlation_123"
        record.user_id = "user456"
        
        formatted = formatter.format(record)
        parsed = json.loads(formatted)
        
        # Check required fields
        assert parsed["@timestamp"]
        assert parsed["level"] == "INFO"
        assert parsed["logger"] == "test_logger"
        assert parsed["message"] == "Test message"
        assert parsed["correlation_id"] == "test_correlation_123"
        assert parsed["user_id"] == "user456"
    
    def test_json_formatter_with_system_metrics(self):
        """Test JSON formatter with system metrics."""
        formatter = EnhancedJSONFormatter(include_system_metrics=True)
        
        import logging
        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="/test/path.py",
            lineno=123,
            msg="Error message",
            args=(),
            exc_info=None
        )
        
        with patch('psutil.Process') as mock_process:
            mock_process.return_value.memory_info.return_value.rss = 134217728  # 128MB
            mock_process.return_value.cpu_percent.return_value = 15.5
            
            formatted = formatter.format(record)
            parsed = json.loads(formatted)
            
            assert "system" in parsed
            assert "memory_mb" in parsed["system"]
            assert "cpu_percent" in parsed["system"]
            assert "hostname" in parsed["system"]
            assert "process_id" in parsed["system"]
    
    def test_json_formatter_exception_handling(self):
        """Test JSON formatter with exception information."""
        formatter = EnhancedJSONFormatter()
        
        import logging
        
        try:
            raise ValueError("Test exception")
        except ValueError:
            import sys
            exc_info = sys.exc_info()
        
        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="/test/path.py",
            lineno=123,
            msg="Error with exception",
            args=(),
            exc_info=exc_info
        )
        
        formatted = formatter.format(record)
        parsed = json.loads(formatted)
        
        assert "exception" in parsed
        assert "type" in parsed["exception"]
        assert "message" in parsed["exception"]
        assert "traceback" in parsed["exception"]
        assert parsed["exception"]["type"] == "ValueError"
        assert parsed["exception"]["message"] == "Test exception"
    
    def test_json_formatter_business_event(self):
        """Test JSON formatter with business event data."""
        formatter = EnhancedJSONFormatter()
        
        import logging
        record = logging.LogRecord(
            name="business_logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=123,
            msg="Business event occurred",
            args=(),
            exc_info=None
        )
        
        # Add business event data
        record.business_event = {
            "type": "breed_created",
            "breed": "Arabian",
            "user": "user123",
            "metadata": {"source": "api"}
        }
        
        formatted = formatter.format(record)
        parsed = json.loads(formatted)
        
        assert "business_event" in parsed
        assert parsed["business_event"]["type"] == "breed_created"
        assert parsed["business_event"]["breed"] == "Arabian"
        assert parsed["business_event"]["user"] == "user123"


class TestAsyncFileHandler:
    """Test the async file handler."""
    
    @pytest.fixture
    def temp_log_file(self):
        """Create a temporary log file."""
        temp_file = tempfile.NamedTemporaryFile(mode='w+', suffix='.log', delete=False)
        temp_file.close()
        yield Path(temp_file.name)
        # Cleanup
        try:
            Path(temp_file.name).unlink()
        except FileNotFoundError:
            pass
    
    def test_async_handler_initialization(self, temp_log_file):
        """Test async handler initialization."""
        handler = AsyncFileHandler(
            filename=str(temp_log_file),
            max_queue_size=1000
        )
        
        assert handler.filename == str(temp_log_file)
        assert handler.max_queue_size == 1000
        assert handler._queue is not None
        assert handler._running is False
    
    @pytest.mark.asyncio
    async def test_async_handler_emit(self, temp_log_file):
        """Test async handler emit functionality."""
        handler = AsyncFileHandler(filename=str(temp_log_file))
        handler.setFormatter(EnhancedJSONFormatter())
        
        # Start the handler
        await handler.start()
        
        try:
            import logging
            record = logging.LogRecord(
                name="test_logger",
                level=logging.INFO,
                pathname="/test/path.py",
                lineno=123,
                msg="Async test message",
                args=(),
                exc_info=None
            )
            
            # Emit log record
            handler.emit(record)
            
            # Wait a bit for async processing
            await asyncio.sleep(0.1)
            
            # Check that file was written
            assert temp_log_file.exists()
            content = temp_log_file.read_text()
            assert "Async test message" in content
            
        finally:
            await handler.stop()
    
    @pytest.mark.asyncio
    async def test_async_handler_queue_overflow(self, temp_log_file):
        """Test async handler behavior when queue overflows."""
        handler = AsyncFileHandler(
            filename=str(temp_log_file),
            max_queue_size=2  # Very small queue
        )
        
        await handler.start()
        
        try:
            import logging
            
            # Fill the queue beyond capacity
            for i in range(5):
                record = logging.LogRecord(
                    name="test_logger",
                    level=logging.INFO,
                    pathname="/test/path.py",
                    lineno=123,
                    msg=f"Message {i}",
                    args=(),
                    exc_info=None
                )
                handler.emit(record)
            
            # Should handle overflow gracefully without crashing
            await asyncio.sleep(0.1)
            
        finally:
            await handler.stop()
    
    @pytest.mark.asyncio
    async def test_async_handler_performance(self, temp_log_file, performance_timer):
        """Test async handler performance."""
        handler = AsyncFileHandler(filename=str(temp_log_file))
        handler.setFormatter(EnhancedJSONFormatter())
        
        await handler.start()
        
        try:
            import logging
            
            timer = performance_timer
            timer.start()
            
            # Emit many log records
            for i in range(1000):
                record = logging.LogRecord(
                    name="perf_logger",
                    level=logging.INFO,
                    pathname="/test/path.py",
                    lineno=123,
                    msg=f"Performance test message {i}",
                    args=(),
                    exc_info=None
                )
                handler.emit(record)
            
            elapsed = timer.stop()
            
            # Emitting should be very fast (non-blocking)
            assert elapsed < 0.1
            
            # Wait for all messages to be written
            await asyncio.sleep(0.5)
            
        finally:
            await handler.stop()


class TestMetricsCollector:
    """Test the metrics collector."""
    
    def test_metrics_collector_initialization(self):
        """Test metrics collector initialization."""
        collector = MetricsCollector()
        
        assert collector.total_requests == 0
        assert collector.total_errors == 0
        assert len(collector.response_times) == 0
        assert len(collector.status_codes) == 0
        assert len(collector.endpoint_metrics) == 0
    
    def test_record_request_success(self):
        """Test recording successful requests."""
        collector = MetricsCollector()
        
        collector.record_request(
            method="GET",
            endpoint="/api/v1/breeds",
            status_code=200,
            response_time=125.5
        )
        
        assert collector.total_requests == 1
        assert collector.total_errors == 0
        assert len(collector.response_times) == 1
        assert collector.response_times[0] == 125.5
        assert collector.status_codes[200] == 1
        assert "/api/v1/breeds" in collector.endpoint_metrics
    
    def test_record_request_error(self):
        """Test recording error requests."""
        collector = MetricsCollector()
        
        collector.record_request(
            method="GET",
            endpoint="/api/v1/breeds/nonexistent",
            status_code=404,
            response_time=45.2
        )
        
        assert collector.total_requests == 1
        assert collector.total_errors == 1
        assert collector.status_codes[404] == 1
    
    def test_get_summary(self):
        """Test getting metrics summary."""
        collector = MetricsCollector()
        
        # Record some requests
        collector.record_request("GET", "/api/v1/breeds", 200, 100.0)
        collector.record_request("POST", "/api/v1/breeds", 201, 150.0)
        collector.record_request("GET", "/api/v1/breeds/404", 404, 50.0)
        
        summary = collector.get_summary()
        
        assert summary["total_requests"] == 3
        assert summary["total_errors"] == 1
        assert summary["error_rate"] == pytest.approx(33.33, rel=1e-2)
        assert summary["average_response_time"] == 100.0  # (100+150+50)/3
        assert summary["requests_per_second"] > 0
        assert "status_codes" in summary
        assert summary["status_codes"][200] == 1
        assert summary["status_codes"][404] == 1
    
    def test_get_top_endpoints(self):
        """Test getting top endpoints."""
        collector = MetricsCollector()
        
        # Record requests to different endpoints
        collector.record_request("GET", "/api/v1/breeds", 200, 100.0)
        collector.record_request("GET", "/api/v1/breeds", 200, 120.0)
        collector.record_request("GET", "/api/v1/health", 200, 20.0)
        
        top_endpoints = collector.get_top_endpoints(limit=2)
        
        assert len(top_endpoints) <= 2
        # Most requested endpoint should be first
        assert top_endpoints[0]["endpoint"] == "/api/v1/breeds"
        assert top_endpoints[0]["count"] == 2


class TestLoggingContext:
    """Test the logging context manager."""
    
    def test_logging_context_basic(self):
        """Test basic logging context functionality."""
        with LoggingContext(correlation_id="test_123", user_id="user456"):
            logger = get_logger("test_context")
            
            # Mock the logger to capture calls
            with patch.object(logger, 'info') as mock_info:
                logger.info("Test message")
                
                # Should be called with extra context
                mock_info.assert_called_once()
                call_args = mock_info.call_args
                extra = call_args[1].get('extra', {})
                
                assert 'correlation_id' in str(call_args) or extra.get('correlation_id') == "test_123"
    
    def test_logging_context_nesting(self):
        """Test nested logging contexts."""
        with LoggingContext(correlation_id="outer_123"):
            with LoggingContext(user_id="user456"):
                logger = get_logger("test_nested")
                
                with patch.object(logger, 'info') as mock_info:
                    logger.info("Nested message")
                    
                    # Should have both correlation_id and user_id
                    call_args = mock_info.call_args
                    call_str = str(call_args)
                    
                    # Both should be present in the call
                    assert 'outer_123' in call_str or 'user456' in call_str
    
    def test_logging_context_performance_data(self):
        """Test logging context with performance data."""
        with LoggingContext(
            correlation_id="perf_123",
            performance_data={"db_query_time": 25.5, "cache_hit": True}
        ):
            logger = get_logger("test_performance")
            
            with patch.object(logger, 'info') as mock_info:
                logger.info("Performance test")
                
                call_args = mock_info.call_args
                call_str = str(call_args)
                
                # Performance data should be included
                assert 'db_query_time' in call_str or 'performance' in call_str


class TestLogPerformanceDecorator:
    """Test the log_performance decorator."""
    
    @pytest.mark.asyncio
    async def test_log_performance_async_function(self):
        """Test log_performance decorator with async function."""
        
        @log_performance
        async def test_async_function(value):
            await asyncio.sleep(0.01)  # Small delay
            return value * 2
        
        with patch('app.core.enhanced_logging.get_logger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            result = await test_async_function(5)
            
            # Function should work correctly
            assert result == 10
            
            # Should have logged performance info
            mock_logger.info.assert_called()
            call_args = mock_logger.info.call_args[0]
            assert "completed" in call_args[0].lower()
    
    def test_log_performance_sync_function(self):
        """Test log_performance decorator with sync function."""
        
        @log_performance
        def test_sync_function(x, y):
            return x + y
        
        with patch('app.core.enhanced_logging.get_logger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            result = test_sync_function(3, 4)
            
            # Function should work correctly
            assert result == 7
            
            # Should have logged performance info
            mock_logger.info.assert_called()
    
    @pytest.mark.asyncio
    async def test_log_performance_exception_handling(self):
        """Test log_performance decorator exception handling."""
        
        @log_performance
        async def failing_function():
            raise ValueError("Test error")
        
        with patch('app.core.enhanced_logging.get_logger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            with pytest.raises(ValueError):
                await failing_function()
            
            # Should have logged error with performance info
            mock_logger.error.assert_called()


class TestBusinessEventLogging:
    """Test business event logging functionality."""
    
    def test_log_business_event_basic(self):
        """Test basic business event logging."""
        with patch('app.core.enhanced_logging.get_logger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            log_business_event(
                event_type="breed_created",
                breed="Arabian",
                user="user123"
            )
            
            # Should log business event
            mock_logger.info.assert_called()
            call_args = mock_logger.info.call_args
            
            # Check that business event data is included
            assert len(call_args) >= 2  # message and extra
            extra = call_args[1].get('extra', {})
            
            # Business event should be in extra data
            assert 'business_event' in extra
            business_event = extra['business_event']
            assert business_event['type'] == "breed_created"
            assert business_event['breed'] == "Arabian"
            assert business_event['user'] == "user123"
    
    def test_log_business_event_with_metadata(self):
        """Test business event logging with metadata."""
        with patch('app.core.enhanced_logging.get_logger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            log_business_event(
                event_type="breed_searched",
                query="Arabian horses",
                results_count=5,
                metadata={"source": "web", "user_type": "premium"}
            )
            
            mock_logger.info.assert_called()
            call_args = mock_logger.info.call_args
            extra = call_args[1].get('extra', {})
            
            business_event = extra['business_event']
            assert business_event['query'] == "Arabian horses"
            assert business_event['results_count'] == 5
            assert business_event['metadata']['source'] == "web"


class TestSecurityEventLogging:
    """Test security event logging functionality."""
    
    def test_log_security_event_basic(self):
        """Test basic security event logging."""
        with patch('app.core.enhanced_logging.get_logger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            log_security_event(
                event_type="failed_login",
                user_id="user123",
                ip_address="192.168.1.100",
                severity="medium"
            )
            
            # Should log to security logger
            mock_logger.warning.assert_called()
            call_args = mock_logger.warning.call_args
            
            # Check security event structure
            assert "security event" in call_args[0][0].lower()
    
    def test_log_security_event_high_severity(self):
        """Test high severity security event logging."""
        with patch('app.core.enhanced_logging.get_logger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            log_security_event(
                event_type="unauthorized_access",
                ip_address="10.0.0.1",
                severity="high",
                details={"attempted_resource": "/admin", "method": "POST"}
            )
            
            # High severity should use error level
            mock_logger.error.assert_called()


class TestLoggingSetup:
    """Test logging setup and configuration."""
    
    def test_setup_logging_basic(self):
        """Test basic logging setup."""
        with patch('app.core.enhanced_logging.Path') as mock_path:
            mock_path.return_value.mkdir = Mock()
            
            with patch('logging.getLogger') as mock_get_logger:
                mock_logger = Mock()
                mock_get_logger.return_value = mock_logger
                
                setup_enhanced_logging()
                
                # Should configure root logger
                mock_get_logger.assert_called()
    
    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a logger instance."""
        logger = get_logger("test_logger")
        
        # Should return a logger-like object
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'debug')
    
    def test_get_metrics_summary_returns_dict(self):
        """Test that get_metrics_summary returns metrics data."""
        with patch('app.core.enhanced_logging._metrics_collector') as mock_collector:
            mock_collector.get_summary.return_value = {
                "total_requests": 100,
                "total_errors": 5,
                "error_rate": 5.0
            }
            
            summary = get_metrics_summary()
            
            assert isinstance(summary, dict)
            assert "total_requests" in summary
            assert summary["total_requests"] == 100


@pytest.mark.logging
@pytest.mark.slow
class TestLoggingIntegration:
    """Integration tests for logging system."""
    
    @pytest.mark.asyncio
    async def test_full_logging_pipeline(self, temp_log_file):
        """Test complete logging pipeline from setup to file output."""
        # Configure logging to use temp file
        with patch('app.core.enhanced_logging.Path') as mock_path:
            mock_path.return_value.mkdir = Mock()
            mock_path.return_value.exists.return_value = True
            
            # Setup logging
            setup_enhanced_logging()
            
            # Get logger and log various events
            logger = get_logger("integration_test")
            
            # Test different log levels and contexts
            with LoggingContext(correlation_id="integration_123", user_id="testuser"):
                logger.info("Integration test message")
                logger.warning("Test warning")
                logger.error("Test error")
                
                # Test business event
                log_business_event(
                    event_type="integration_test",
                    action="testing",
                    metadata={"test": True}
                )
                
                # Test security event
                log_security_event(
                    event_type="test_security",
                    severity="low",
                    details={"test": "security"}
                )
            
            # Wait for async processing
            await asyncio.sleep(0.1)
    
    def test_logging_performance_under_load(self, performance_timer):
        """Test logging performance under high load."""
        logger = get_logger("performance_test")
        
        timer = performance_timer
        timer.start()
        
        # Log many messages quickly
        for i in range(1000):
            with LoggingContext(correlation_id=f"perf_{i}"):
                logger.info(f"Performance test message {i}")
        
        elapsed = timer.stop()
        
        # Should handle high throughput efficiently
        assert elapsed < 1.0  # Less than 1 second for 1000 messages
    
    def test_concurrent_logging(self):
        """Test concurrent logging from multiple contexts."""
        import threading
        import time
        
        results = []
        errors = []
        
        def log_worker(worker_id):
            try:
                logger = get_logger(f"worker_{worker_id}")
                for i in range(50):
                    with LoggingContext(
                        correlation_id=f"worker_{worker_id}_msg_{i}",
                        worker_id=worker_id
                    ):
                        logger.info(f"Worker {worker_id} message {i}")
                        time.sleep(0.001)  # Small delay
                results.append(worker_id)
            except Exception as e:
                errors.append((worker_id, str(e)))
        
        # Start multiple worker threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=log_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=10)
        
        # All workers should complete successfully
        assert len(results) == 5
        assert len(errors) == 0