---
applyTo: "app/core/**/*logging*.py,app/core/**/middleware.py,**/monitoring*.py"
---

# Logging & Monitoring Instructions

## Enhanced Logging System

This service uses structured JSON logging with correlation IDs and automatic PII filtering.

## Required Patterns

**Logger Initialization**: Always get logger with component name:
```python
from app.core.enhanced_logging import get_logger
self.logger = get_logger("service.component_name")
```

**Performance Monitoring**: Use `@log_performance` decorator for operations that may be slow:
```python
@log_performance("operation_name", threshold_ms=500.0, include_args=True)
def slow_operation(self, param1, param2):
    # Implementation
```

**Business Event Logging**: Log important business operations:
```python
from app.core.enhanced_logging import log_business_event

log_business_event(
    self.logger,
    "resource_created",
    {
        "resource_id": resource.id,
        "resource_type": "horse_breed",
        "user_id": user_id
    }
)
```

**Context Logging**: Use LoggingContext for operation tracking:
```python
from app.core.enhanced_logging import LoggingContext

with LoggingContext("database_query", self.logger, query_type="select", table="breeds"):
    results = self.db.query(HorseBreed).all()
```

## Security & PII Protection

**Automatic PII Filtering**: The logging system automatically filters:
- Passwords, tokens, API keys
- Email addresses, SSNs, credit card numbers
- Sensitive HTTP headers (Authorization, etc.)

**Never log sensitive data directly** - the system will filter it, but be mindful.

## Monitoring Endpoints

**Health Check Patterns**: Implement comprehensive health checks:
- `/health` - Basic service health
- `/monitoring/health` - Detailed health with dependencies
- `/monitoring/metrics` - Performance metrics
- `/monitoring/logs` - Recent filtered logs

**Performance Metrics**: Track and expose key metrics:
- Request duration
- Database connection status
- Memory and CPU usage
- Business operation counts