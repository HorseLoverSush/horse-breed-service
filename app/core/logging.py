"""
Logging configuration for the Horse Breed Service.

This module provides comprehensive logging configuration with structured JSON output,
file rotation, and different log levels for development and production environments.
"""
import json
import logging
import logging.config
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    
    This formatter creates JSON log entries with consistent structure
    and includes contextual information like request IDs when available.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        # Base log entry structure
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add process and thread information
        log_entry["process"] = {
            "id": record.process,
            "name": record.processName,
        }
        log_entry["thread"] = {
            "id": record.thread,
            "name": record.threadName,
        }
        
        # Add extra fields from log record
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in [
                "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
                "module", "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "getMessage", 
                "exc_info", "exc_text", "stack_info"
            ]:
                extra_fields[key] = value
        
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
        
        return json.dumps(log_entry, default=str, ensure_ascii=False)


def setup_logging() -> None:
    """
    Set up logging configuration for the application.
    
    This function configures:
    - Console logging with appropriate formatter
    - File logging with rotation (in production)
    - Different log levels based on environment
    - Structured JSON logging for better parsing
    """
    
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
            "json": {
                "()": JSONFormatter,
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "simple": {
                "format": "%(levelname)s - %(name)s - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "level": log_level,
                "class": "logging.StreamHandler",
                "formatter": "simple" if settings.DEBUG else "json",
                "stream": sys.stdout,
            },
            "file": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "json",
                "filename": log_dir / "horse_breed_service.log",
                "maxBytes": 10 * 1024 * 1024,  # 10MB
                "backupCount": 5,
                "encoding": "utf-8",
            },
            "error_file": {
                "level": "ERROR",
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "json",
                "filename": log_dir / "horse_breed_service_errors.log",
                "maxBytes": 10 * 1024 * 1024,  # 10MB
                "backupCount": 10,
                "encoding": "utf-8",
            },
        },
        "loggers": {
            # Application loggers
            "app": {
                "level": log_level,
                "handlers": ["console", "file", "error_file"],
                "propagate": False,
            },
            # FastAPI access logs
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            # Uvicorn error logs
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["console", "file", "error_file"],
                "propagate": False,
            },
            # SQLAlchemy logs (only in debug mode)
            "sqlalchemy.engine": {
                "level": "INFO" if settings.DEBUG else "WARNING",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "sqlalchemy.pool": {
                "level": "INFO" if settings.DEBUG else "WARNING",
                "handlers": ["console", "file"],
                "propagate": False,
            },
        },
        "root": {
            "level": "INFO",
            "handlers": ["console", "file", "error_file"],
        },
    }
    
    # Apply logging configuration
    logging.config.dictConfig(logging_config)
    
    # Log application startup
    logger = logging.getLogger("app.startup")
    logger.info(
        "Logging system initialized",
        extra={
            "log_level": log_level,
            "debug_mode": settings.DEBUG,
            "log_directory": str(log_dir.absolute()),
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


# Convenience function for getting correlation ID from log context
def log_with_context(logger: logging.Logger, level: str, message: str, **kwargs) -> None:
    """
    Log a message with additional context.
    
    Args:
        logger: The logger instance to use
        level: Log level (debug, info, warning, error, critical)
        message: The log message
        **kwargs: Additional context to include in the log
    """
    log_method = getattr(logger, level.lower())
    log_method(message, extra=kwargs)


# Performance logging decorator
def log_performance(logger: logging.Logger, operation: str):
    """
    Decorator to log performance metrics for functions.
    
    Args:
        logger: Logger instance to use
        operation: Name of the operation being logged
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                logger.info(
                    f"Operation completed: {operation}",
                    extra={
                        "operation": operation,
                        "execution_time": round(execution_time, 4),
                        "status": "success",
                        "function": func.__name__,
                    }
                )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                logger.error(
                    f"Operation failed: {operation}",
                    extra={
                        "operation": operation,
                        "execution_time": round(execution_time, 4),
                        "status": "error",
                        "function": func.__name__,
                        "error": str(e),
                        "error_type": e.__class__.__name__,
                    },
                    exc_info=True
                )
                
                raise
                
        return wrapper
    return decorator