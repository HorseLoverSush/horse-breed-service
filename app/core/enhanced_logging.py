"""
Enhanced logging configuration for the Horse Breed Service.

This module provides enterprise-grade logging with:
- Structured JSON logging with correlation IDs
- Performance monitoring and metrics
- Security event logging
- Async logging for high performance
- Log sampling and filtering
- Multiple output destinations
- Custom log processors and enrichers
"""
import asyncio
import json
import logging
import logging.config
import logging.handlers
import os
import platform
import psutil
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from contextvars import ContextVar
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable
from urllib.parse import urlparse

try:
    import aiofiles
    AIOFILES_AVAILABLE = True
except ImportError:
    AIOFILES_AVAILABLE = False

from app.core.config import settings

# Context variables for request correlation
request_id_context: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_context: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
session_id_context: ContextVar[Optional[str]] = ContextVar('session_id', default=None)

# Global metrics collector
_metrics_collector = None


class MetricsCollector:
    """Collects and aggregates logging metrics."""
    
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.warning_count = 0
        self.performance_metrics = []
        self.response_times = []
        self.status_codes = {}
        self.endpoints = {}
        self.start_time = time.time()
        
    def record_request(self, endpoint: str, method: str, status_code: int, response_time: float):
        """Record a request metric."""
        self.request_count += 1
        self.response_times.append(response_time)
        
        # Track status codes
        self.status_codes[status_code] = self.status_codes.get(status_code, 0) + 1
        
        # Track endpoints
        endpoint_key = f"{method} {endpoint}"
        if endpoint_key not in self.endpoints:
            self.endpoints[endpoint_key] = {
                'count': 0,
                'total_time': 0,
                'min_time': float('inf'),
                'max_time': 0,
                'errors': 0
            }
        
        endpoint_data = self.endpoints[endpoint_key]
        endpoint_data['count'] += 1
        endpoint_data['total_time'] += response_time
        endpoint_data['min_time'] = min(endpoint_data['min_time'], response_time)
        endpoint_data['max_time'] = max(endpoint_data['max_time'], response_time)
        
        if status_code >= 400:
            endpoint_data['errors'] += 1
            if status_code >= 500:
                self.error_count += 1
            elif status_code >= 400:
                self.warning_count += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        uptime = time.time() - self.start_time
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        return {
            'uptime_seconds': round(uptime, 2),
            'total_requests': self.request_count,
            'total_errors': self.error_count,
            'total_warnings': self.warning_count,
            'average_response_time': round(avg_response_time, 4),
            'requests_per_second': round(self.request_count / uptime if uptime > 0 else 0, 2),
            'error_rate': round(self.error_count / self.request_count * 100 if self.request_count > 0 else 0, 2),
            'status_codes': self.status_codes,
            'top_endpoints': dict(sorted(
                self.endpoints.items(), 
                key=lambda x: x[1]['count'], 
                reverse=True
            )[:10])
        }


class EnhancedJSONFormatter(logging.Formatter):
    """
    Enhanced JSON formatter with correlation IDs, performance metrics,
    and system information. Includes PII filtering for security.
    """
    
    # Sensitive fields that should be filtered from logs
    SENSITIVE_FIELDS = {
        'password', 'passwd', 'pwd', 'secret', 'token', 'key', 'auth',
        'authorization', 'cookie', 'session', 'csrf', 'api_key',
        'access_token', 'refresh_token', 'bearer', 'signature',
        'email', 'phone', 'ssn', 'credit_card', 'cc_number',
        'address', 'personal_info', 'pii', 'private'
    }
    
    # Sensitive header names to filter
    SENSITIVE_HEADERS = {
        'authorization', 'cookie', 'x-api-key', 'x-auth-token',
        'x-csrf-token', 'x-session-id', 'x-user-token'
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hostname = platform.node()
        self.service_name = settings.PROJECT_NAME
        self.service_version = settings.PROJECT_VERSION
    
    def _filter_sensitive_data(self, data: Any, field_name: str = "") -> Any:
        """Filter sensitive data from logs."""
        if isinstance(data, dict):
            filtered = {}
            for key, value in data.items():
                key_lower = key.lower()
                if any(sensitive in key_lower for sensitive in self.SENSITIVE_FIELDS):
                    filtered[key] = "[FILTERED]"
                else:
                    filtered[key] = self._filter_sensitive_data(value, key)
            return filtered
        elif isinstance(data, (list, tuple)):
            return [self._filter_sensitive_data(item) for item in data]
        elif isinstance(data, str) and len(data) > 100:
            # Truncate very long strings that might contain sensitive data
            return data[:100] + "...[TRUNCATED]"
        else:
            # Check if the field name itself is sensitive
            field_lower = field_name.lower()
            if any(sensitive in field_lower for sensitive in self.SENSITIVE_FIELDS):
                return "[FILTERED]"
        return data
    
    def _filter_headers(self, headers: Dict[str, Any]) -> Dict[str, Any]:
        """Filter sensitive headers."""
        filtered_headers = {}
        for key, value in headers.items():
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in self.SENSITIVE_HEADERS):
                filtered_headers[key] = "[FILTERED]"
            else:
                filtered_headers[key] = value
        return filtered_headers
        
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as enhanced JSON."""
        now = datetime.fromtimestamp(record.created, tz=timezone.utc)
        
        # Base log entry structure
        log_entry = {
            "@timestamp": now.isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": {
                "name": self.service_name,
                "version": self.service_version,
                "hostname": self.hostname,
                "environment": "development" if settings.DEBUG else "production"
            },
            "source": {
                "file": record.filename,
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
                "path": record.pathname
            },
            "process": {
                "id": record.process,
                "name": record.processName,
                "thread_id": record.thread,
                "thread_name": record.threadName
            }
        }
        
        # Add correlation IDs from context
        correlation = {}
        if request_id := request_id_context.get():
            correlation["request_id"] = request_id
        if user_id := user_id_context.get():
            correlation["user_id"] = user_id
        if session_id := session_id_context.get():
            correlation["session_id"] = session_id
        
        if correlation:
            log_entry["correlation"] = correlation
        
        # Add system metrics for ERROR and CRITICAL logs
        if record.levelno >= logging.ERROR:
            try:
                process = psutil.Process()
                log_entry["system"] = {
                    "cpu_percent": process.cpu_percent(),
                    "memory_percent": process.memory_percent(),
                    "memory_mb": round(process.memory_info().rss / 1024 / 1024, 2),
                    "open_files": len(process.open_files()),
                    "connections": len(process.connections())
                }
            except (psutil.Error, OSError):
                # Ignore system metrics if unavailable
                pass
        
        # Add extra fields from log record (with PII filtering)
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in [
                "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
                "module", "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "getMessage", 
                "exc_info", "exc_text", "stack_info"
            ]:
                # Apply PII filtering to the field
                filtered_value = self._filter_sensitive_data(value, key)
                
                # Handle complex objects
                if isinstance(filtered_value, (dict, list, tuple)):
                    extra_fields[key] = filtered_value
                elif hasattr(filtered_value, '__dict__'):
                    extra_fields[key] = str(filtered_value)
                else:
                    extra_fields[key] = filtered_value
        
        if extra_fields:
            log_entry["extra"] = extra_fields
        
        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info) if record.exc_info else None,
            }
        
        # Add stack trace if present
        if hasattr(record, 'stack_info') and record.stack_info:
            log_entry["stack_trace"] = record.stack_info
        
        # Add tags for log categorization
        tags = []
        if "request" in record.name or hasattr(record, 'request_id'):
            tags.append("request")
        if "database" in record.name or "db" in record.name:
            tags.append("database")
        if "security" in record.name or record.levelno >= logging.ERROR:
            tags.append("security")
        if hasattr(record, 'performance') or "performance" in str(record.msg).lower():
            tags.append("performance")
        if hasattr(record, 'business_event'):
            tags.append("business")
        
        if tags:
            log_entry["tags"] = tags
        
        return json.dumps(log_entry, default=str, ensure_ascii=False)


class AsyncFileHandler(logging.Handler):
    """
    Asynchronous file handler for high-performance logging.
    """
    
    def __init__(self, filename: str, maxBytes: int = 10*1024*1024, backupCount: int = 5):
        super().__init__()
        self.filename = Path(filename)
        self.maxBytes = maxBytes
        self.backupCount = backupCount
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="AsyncFileHandler")
        self._ensure_directory()
        
    def _ensure_directory(self):
        """Ensure the log directory exists."""
        self.filename.parent.mkdir(parents=True, exist_ok=True)
    
    def emit(self, record):
        """Emit a record asynchronously."""
        try:
            msg = self.format(record)
            # Submit to thread pool for async processing
            self.executor.submit(self._write_log, msg)
        except Exception:
            self.handleError(record)
    
    def _write_log(self, message: str):
        """Write log message to file with rotation."""
        try:
            # Check if rotation is needed
            if self.filename.exists() and self.filename.stat().st_size > self.maxBytes:
                self._rotate_logs()
            
            # Write the message
            with open(self.filename, 'a', encoding='utf-8') as f:
                f.write(message + '\n')
                f.flush()
        except Exception as e:
            # Fallback to stderr
            print(f"Error writing to log file: {e}", file=sys.stderr)
    
    def _rotate_logs(self):
        """Rotate log files."""
        try:
            # Remove oldest backup
            oldest_backup = self.filename.with_suffix(f".{self.backupCount}")
            if oldest_backup.exists():
                oldest_backup.unlink()
            
            # Rotate existing backups
            for i in range(self.backupCount - 1, 0, -1):
                old_backup = self.filename.with_suffix(f".{i}")
                new_backup = self.filename.with_suffix(f".{i + 1}")
                if old_backup.exists():
                    old_backup.rename(new_backup)
            
            # Move current file to .1
            if self.filename.exists():
                backup_name = self.filename.with_suffix(".1")
                self.filename.rename(backup_name)
        except Exception as e:
            print(f"Error rotating log files: {e}", file=sys.stderr)
    
    def close(self):
        """Close the handler and clean up."""
        super().close()
        self.executor.shutdown(wait=True)


class SamplingFilter(logging.Filter):
    """
    Filter to sample logs based on level and rate.
    Useful for high-traffic scenarios to reduce log volume.
    """
    
    def __init__(self, sample_rate: float = 1.0, level_rates: Optional[Dict[str, float]] = None):
        super().__init__()
        self.sample_rate = sample_rate
        self.level_rates = level_rates or {}
        self.counters = {}
    
    def filter(self, record) -> bool:
        """Filter records based on sampling rate."""
        level_name = record.levelname
        
        # Always allow ERROR and CRITICAL
        if record.levelno >= logging.ERROR:
            return True
        
        # Get sampling rate for this level
        rate = self.level_rates.get(level_name, self.sample_rate)
        
        # Initialize counter for this level
        if level_name not in self.counters:
            self.counters[level_name] = 0
        
        self.counters[level_name] += 1
        
        # Sample based on rate (1.0 = all, 0.1 = 10%)
        return (self.counters[level_name] % max(1, int(1 / rate))) == 0


class SecurityLogFilter(logging.Filter):
    """
    Filter to identify and enrich security-related log events.
    """
    
    SECURITY_KEYWORDS = [
        'authentication', 'authorization', 'login', 'logout', 'failed',
        'unauthorized', 'forbidden', 'blocked', 'suspicious', 'attack',
        'injection', 'xss', 'csrf', 'rate limit', 'brute force'
    ]
    
    def filter(self, record) -> bool:
        """Identify security events and add security context."""
        message = record.getMessage().lower()
        
        # Check if this is a security-related log
        is_security_event = any(keyword in message for keyword in self.SECURITY_KEYWORDS)
        
        if is_security_event:
            # Add security tag
            if not hasattr(record, 'tags'):
                record.tags = []
            if 'security' not in record.tags:
                record.tags.append('security')
            
            # Mark as security event for enhanced processing
            record.security_event = True
            
            # Increase log level for security events (optional)
            if record.levelno < logging.WARNING:
                record.levelno = logging.WARNING
                record.levelname = 'WARNING'
        
        return True


def setup_enhanced_logging() -> None:
    """
    Set up enhanced logging configuration for the application.
    
    This function configures:
    - Enhanced JSON logging with correlation IDs
    - Async file handlers for performance
    - Multiple log destinations (console, files, metrics)
    - Log sampling for high-traffic scenarios
    - Security event detection and enrichment
    - Performance monitoring integration
    """
    global _metrics_collector
    _metrics_collector = MetricsCollector()
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Determine log level based on environment
    log_level = "DEBUG" if settings.DEBUG else "INFO"
    
    # Configure logging
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "enhanced_json": {
                "()": EnhancedJSONFormatter,
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - [%(correlation)s] - %(module)s:%(funcName)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "simple": {
                "format": "%(levelname)s - %(name)s - %(message)s",
            },
            "performance": {
                "format": "PERF - %(asctime)s - %(message)s - %(extra)s",
                "datefmt": "%Y-%m-%d %H:%M:%S.%f",
            },
        },
        "filters": {
            "sampling": {
                "()": SamplingFilter,
                "sample_rate": 1.0 if settings.DEBUG else 0.1,  # Sample 10% in production
                "level_rates": {
                    "DEBUG": 0.01,  # Sample 1% of DEBUG logs
                    "INFO": 0.1,    # Sample 10% of INFO logs
                    "WARNING": 1.0, # Keep all WARNING logs
                }
            },
            "security": {
                "()": SecurityLogFilter,
            },
        },
        "handlers": {
            "console": {
                "level": log_level,
                "class": "logging.StreamHandler",
                "formatter": "simple" if settings.DEBUG else "enhanced_json",
                "filters": ["security"],
                "stream": sys.stdout,
            },
            "main_file": {
                "()": AsyncFileHandler,
                "level": "INFO",
                "formatter": "enhanced_json",
                "filters": ["sampling", "security"],
                "filename": log_dir / "horse_breed_service.log",
                "maxBytes": 50 * 1024 * 1024,  # 50MB
                "backupCount": 10,
            },
            "error_file": {
                "()": AsyncFileHandler,
                "level": "ERROR",
                "formatter": "enhanced_json",
                "filters": ["security"],
                "filename": log_dir / "horse_breed_service_errors.log",
                "maxBytes": 25 * 1024 * 1024,  # 25MB
                "backupCount": 15,
            },
            "security_file": {
                "()": AsyncFileHandler,
                "level": "WARNING",
                "formatter": "enhanced_json",
                "filename": log_dir / "horse_breed_service_security.log",
                "maxBytes": 10 * 1024 * 1024,  # 10MB
                "backupCount": 20,
            },
            "performance_file": {
                "()": AsyncFileHandler,
                "level": "INFO",
                "formatter": "enhanced_json",
                "filename": log_dir / "horse_breed_service_performance.log",
                "maxBytes": 25 * 1024 * 1024,  # 25MB
                "backupCount": 5,
            },
            "access_file": {
                "()": AsyncFileHandler,
                "level": "INFO",
                "formatter": "enhanced_json",
                "filename": log_dir / "horse_breed_service_access.log",
                "maxBytes": 100 * 1024 * 1024,  # 100MB
                "backupCount": 7,
            },
        },
        "loggers": {
            # Application loggers
            "app": {
                "level": log_level,
                "handlers": ["console", "main_file", "error_file"],
                "propagate": False,
            },
            # Security-specific logger
            "app.security": {
                "level": "WARNING",
                "handlers": ["console", "security_file", "error_file"],
                "propagate": False,
            },
            # Performance logger
            "app.performance": {
                "level": "INFO",
                "handlers": ["performance_file"],
                "propagate": False,
            },
            # Access logger
            "app.access": {
                "level": "INFO",
                "handlers": ["access_file"],
                "propagate": False,
            },
            # FastAPI access logs
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["access_file"],
                "propagate": False,
            },
            # Uvicorn error logs
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["console", "main_file", "error_file"],
                "propagate": False,
            },
            # SQLAlchemy logs
            "sqlalchemy.engine": {
                "level": "INFO" if settings.DEBUG else "WARNING",
                "handlers": ["main_file"],
                "propagate": False,
            },
            "sqlalchemy.pool": {
                "level": "INFO" if settings.DEBUG else "WARNING",
                "handlers": ["main_file"],
                "propagate": False,
            },
        },
        "root": {
            "level": "INFO",
            "handlers": ["console", "main_file", "error_file"],
        },
    }
    
    # Apply logging configuration
    logging.config.dictConfig(logging_config)
    
    # Log application startup
    logger = logging.getLogger("app.startup")
    logger.info(
        "Enhanced logging system initialized",
        extra={
            "log_level": log_level,
            "debug_mode": settings.DEBUG,
            "log_directory": str(log_dir.absolute()),
            "handlers": list(logging_config["handlers"].keys()),
            "async_logging": True,
            "sampling_enabled": not settings.DEBUG,
            "security_filtering": True,
        }
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: The name for the logger (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(f"app.{name}")


def set_correlation_id(request_id: Optional[str] = None, user_id: Optional[str] = None, 
                      session_id: Optional[str] = None) -> str:
    """
    Set correlation IDs for the current context.
    
    Args:
        request_id: Unique request identifier
        user_id: User identifier
        session_id: Session identifier
        
    Returns:
        The request ID (generated if not provided)
    """
    if request_id is None:
        request_id = str(uuid.uuid4())
    
    request_id_context.set(request_id)
    if user_id:
        user_id_context.set(user_id)
    if session_id:
        session_id_context.set(session_id)
    
    return request_id


def get_correlation_context() -> Dict[str, Optional[str]]:
    """Get current correlation context."""
    return {
        "request_id": request_id_context.get(),
        "user_id": user_id_context.get(),
        "session_id": session_id_context.get(),
    }


def log_business_event(logger: logging.Logger, event_name: str, 
                      details: Optional[Dict[str, Any]] = None, **kwargs) -> None:
    """
    Log a business event with structured data.
    
    Args:
        logger: Logger instance
        event_name: Name of the business event
        details: Event details
        **kwargs: Additional context
    """
    logger.info(
        f"Business event: {event_name}",
        extra={
            "business_event": True,
            "event_name": event_name,
            "event_details": details or {},
            "tags": ["business"],
            **kwargs
        }
    )


def log_security_event(event_type: str, details: Optional[Dict[str, Any]] = None, 
                      level: str = "warning", **kwargs) -> None:
    """
    Log a security event.
    
    Args:
        event_type: Type of security event
        details: Event details
        level: Log level (warning, error, critical)
        **kwargs: Additional context
    """
    logger = logging.getLogger("app.security")
    log_method = getattr(logger, level.lower())
    
    log_method(
        f"Security event: {event_type}",
        extra={
            "security_event": True,
            "event_type": event_type,
            "event_details": details or {},
            "tags": ["security"],
            **kwargs
        }
    )


def log_performance_metric(logger: logging.Logger, metric_name: str, value: float, 
                          unit: str = "ms", **kwargs) -> None:
    """
    Log a performance metric.
    
    Args:
        logger: Logger instance
        metric_name: Name of the metric
        value: Metric value
        unit: Unit of measurement
        **kwargs: Additional context
    """
    perf_logger = logging.getLogger("app.performance")
    perf_logger.info(
        f"Performance metric: {metric_name}",
        extra={
            "performance": True,
            "metric_name": metric_name,
            "metric_value": value,
            "metric_unit": unit,
            "tags": ["performance"],
            **kwargs
        }
    )


def record_request_metrics(endpoint: str, method: str, status_code: int, response_time: float):
    """Record request metrics for monitoring."""
    if _metrics_collector:
        _metrics_collector.record_request(endpoint, method, status_code, response_time)


def get_metrics_summary() -> Dict[str, Any]:
    """Get current metrics summary."""
    return _metrics_collector.get_summary() if _metrics_collector else {}


class LoggingMiddleware:
    """
    Middleware to enhance request/response logging with correlation IDs.
    """
    
    def __init__(self, app):
        self.app = app
        self.logger = get_logger("middleware.logging")
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        
        # Generate correlation ID
        request_id = set_correlation_id()
        
        # Log request start (with sensitive data filtering)
        start_time = time.time()
        
        # Filter sensitive query parameters
        query_string = scope.get("query_string", b"").decode()
        filtered_query = self._filter_query_string(query_string)
        
        # Filter sensitive headers
        raw_headers = dict(scope.get("headers", []))
        filtered_headers = self._filter_headers_for_logging(raw_headers)
        
        # Get client info safely
        client_info = scope.get("client")
        safe_client = {"host": client_info[0], "port": client_info[1]} if client_info else None
        
        self.logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": scope["method"],
                "path": scope["path"],
                "query_string": filtered_query,
                "client": safe_client,
                "headers": filtered_headers,
            }
        )
        
        # Wrap send to capture response
        response_data = {}
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                response_data["status_code"] = message["status"]
                response_data["headers"] = dict(message.get("headers", []))
            elif message["type"] == "http.response.body":
                # Calculate response time
                response_time = time.time() - start_time
                
                # Record metrics
                record_request_metrics(
                    scope["path"], 
                    scope["method"], 
                    response_data["status_code"], 
                    response_time
                )
                
                # Log response
                self.logger.info(
                    "Request completed",
                    extra={
                        "request_id": request_id,
                        "method": scope["method"],
                        "path": scope["path"],
                        "status_code": response_data["status_code"],
                        "response_time": round(response_time, 4),
                        "response_size": len(message.get("body", b"")),
                    }
                )
            
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            response_time = time.time() - start_time
            self.logger.error(
                "Request failed with exception",
                extra={
                    "request_id": request_id,
                    "method": scope["method"],
                    "path": scope["path"],
                    "response_time": round(response_time, 4),
                    "error": str(e),
                    "error_type": e.__class__.__name__,
                },
                exc_info=True
            )
            raise
    
    def _filter_query_string(self, query_string: str) -> str:
        """Filter sensitive data from query parameters."""
        if not query_string:
            return query_string
        
        # Parse and filter query parameters
        from urllib.parse import parse_qs, urlencode
        try:
            params = parse_qs(query_string, keep_blank_values=True)
            filtered_params = {}
            
            for key, values in params.items():
                key_lower = key.lower()
                if any(sensitive in key_lower for sensitive in EnhancedJSONFormatter.SENSITIVE_FIELDS):
                    filtered_params[key] = ["[FILTERED]" for _ in values]
                else:
                    filtered_params[key] = values
            
            return urlencode(filtered_params, doseq=True)
        except Exception:
            # If parsing fails, return sanitized version
            return "[QUERY_PARSE_ERROR]"
    
    def _filter_headers_for_logging(self, headers: Dict[bytes, bytes]) -> Dict[str, str]:
        """Filter sensitive headers for logging."""
        filtered = {}
        for key_bytes, value_bytes in headers.items():
            try:
                key = key_bytes.decode('utf-8').lower()
                value = value_bytes.decode('utf-8')
                
                if any(sensitive in key for sensitive in EnhancedJSONFormatter.SENSITIVE_HEADERS):
                    filtered[key] = "[FILTERED]"
                elif key == 'user-agent' and len(value) > 200:
                    # Truncate very long user agents
                    filtered[key] = value[:200] + "...[TRUNCATED]"
                else:
                    filtered[key] = value
            except UnicodeDecodeError:
                filtered[f"header_{len(filtered)}"] = "[BINARY_HEADER]"
        
        return filtered


# Enhanced performance decorator
def log_performance(operation: str, logger: Optional[logging.Logger] = None, 
                   threshold_ms: float = 1000.0, include_args: bool = False):
    """
    Enhanced decorator to log performance metrics for functions.
    
    Args:
        operation: Name of the operation being logged
        logger: Logger instance to use (auto-detected if None)
        threshold_ms: Log as warning if execution time exceeds this threshold
        include_args: Whether to include function arguments in the log
    """
    def decorator(func: Callable) -> Callable:
        nonlocal logger
        if logger is None:
            logger = get_logger(func.__module__)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            correlation = get_correlation_context()
            
            # Prepare argument info if requested
            arg_info = {}
            if include_args:
                try:
                    # Be careful with sensitive data
                    arg_info = {
                        "args_count": len(args),
                        "kwargs_keys": list(kwargs.keys()),
                    }
                except Exception:
                    arg_info = {"args_info": "unavailable"}
            
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                execution_time = (time.time() - start_time) * 1000  # Convert to ms
                
                # Choose log level based on execution time
                if execution_time > threshold_ms:
                    log_level = "warning"
                    message = f"Slow operation: {operation}"
                else:
                    log_level = "info"
                    message = f"Operation completed: {operation}"
                
                # Log performance metric
                log_method = getattr(logger, log_level)
                log_method(
                    message,
                    extra={
                        "operation": operation,
                        "execution_time_ms": round(execution_time, 2),
                        "status": "success",
                        "function": func.__name__,
                        "source_module": func.__module__,
                        **correlation,
                        **arg_info,
                    }
                )
                
                # Also log to performance logger
                log_performance_metric(
                    logger, 
                    f"{operation}_duration", 
                    execution_time, 
                    "ms",
                    function=func.__name__,
                    status="success"
                )
                
                return result
                
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                
                logger.error(
                    f"Operation failed: {operation}",
                    extra={
                        "operation": operation,
                        "execution_time_ms": round(execution_time, 2),
                        "status": "error",
                        "function": func.__name__,
                        "source_module": func.__module__,
                        "error": str(e),
                        "error_type": e.__class__.__name__,
                        **correlation,
                        **arg_info,
                    },
                    exc_info=True
                )
                
                # Log performance metric for failed operations
                log_performance_metric(
                    logger, 
                    f"{operation}_duration", 
                    execution_time, 
                    "ms",
                    function=func.__name__,
                    status="error",
                    error_type=e.__class__.__name__
                )
                
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Use the same logic but without async/await
            start_time = time.time()
            correlation = get_correlation_context()
            
            arg_info = {}
            if include_args:
                try:
                    arg_info = {
                        "args_count": len(args),
                        "kwargs_keys": list(kwargs.keys()),
                    }
                except Exception:
                    arg_info = {"args_info": "unavailable"}
            
            try:
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                
                if execution_time > threshold_ms:
                    log_level = "warning"
                    message = f"Slow operation: {operation}"
                else:
                    log_level = "info"
                    message = f"Operation completed: {operation}"
                
                log_method = getattr(logger, log_level)
                log_method(
                    message,
                    extra={
                        "operation": operation,
                        "execution_time_ms": round(execution_time, 2),
                        "status": "success",
                        "function": func.__name__,
                        "source_module": func.__module__,
                        **correlation,
                        **arg_info,
                    }
                )
                
                log_performance_metric(
                    logger, 
                    f"{operation}_duration", 
                    execution_time, 
                    "ms",
                    function=func.__name__,
                    status="success"
                )
                
                return result
                
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                
                logger.error(
                    f"Operation failed: {operation}",
                    extra={
                        "operation": operation,
                        "execution_time_ms": round(execution_time, 2),
                        "status": "error",
                        "function": func.__name__,
                        "source_module": func.__module__,
                        "error": str(e),
                        "error_type": e.__class__.__name__,
                        **correlation,
                        **arg_info,
                    },
                    exc_info=True
                )
                
                log_performance_metric(
                    logger, 
                    f"{operation}_duration", 
                    execution_time, 
                    "ms",
                    function=func.__name__,
                    status="error",
                    error_type=e.__class__.__name__
                )
                
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


# Context manager for logging operations
class LoggingContext:
    """Context manager for logging operations with automatic cleanup."""
    
    def __init__(self, operation: str, logger: Optional[logging.Logger] = None, **context):
        self.operation = operation
        self.logger = logger or get_logger("context")
        self.context = context
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(
            f"Starting operation: {self.operation}",
            extra={
                "operation": self.operation,
                "phase": "start",
                **self.context
            }
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time = (time.time() - self.start_time) * 1000
        
        if exc_type is None:
            self.logger.info(
                f"Completed operation: {self.operation}",
                extra={
                    "operation": self.operation,
                    "phase": "complete",
                    "execution_time_ms": round(execution_time, 2),
                    "status": "success",
                    **self.context
                }
            )
        else:
            self.logger.error(
                f"Failed operation: {self.operation}",
                extra={
                    "operation": self.operation,
                    "phase": "error",
                    "execution_time_ms": round(execution_time, 2),
                    "status": "error",
                    "error_type": exc_type.__name__ if exc_type else None,
                    "error_message": str(exc_val) if exc_val else None,
                    **self.context
                },
                exc_info=True
            )
        
        return False  # Don't suppress exceptions