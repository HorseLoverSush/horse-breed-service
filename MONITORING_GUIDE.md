# 🐎 Horse Breed Service - Monitoring & Error Handling Guide

## Overview

The Horse Breed Service now features enterprise-grade error handling, enhanced logging, and comprehensive monitoring capabilities designed for production environments. This guide covers all monitoring features, error handling mechanisms, and observability tools.

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Install dependencies (including monitoring tools)
pip install -r requirements.txt

# Run the setup script
python setup_monitoring.py
```

### 2. Start the Service
```bash
# Start with monitoring enabled
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Access Monitoring
- **API Documentation**: http://localhost:8000/docs
- **Monitoring Dashboard**: Open `monitoring_dashboard.html` in your browser
- **Health Check**: http://localhost:8000/api/v1/monitoring/health

## 📊 Monitoring Endpoints

### Health Checks
| Endpoint | Description | Response Time |
|----------|-------------|---------------|
| `/api/v1/monitoring/health` | Basic health status | < 50ms |
| `/api/v1/monitoring/health/detailed` | Comprehensive health with metrics | < 200ms |
| `/api/v1/monitoring/status` | Overall service status summary | < 100ms |

### Metrics & Performance
| Endpoint | Description | Use Case |
|----------|-------------|----------|
| `/api/v1/monitoring/metrics` | Application metrics | Dashboard data |
| `/api/v1/monitoring/metrics/performance` | Performance-specific metrics | Performance analysis |
| `/api/v1/monitoring/logs/metrics` | Logging statistics | Log analysis |

## 🔧 Error Handling System

### Custom Exception Classes

The service uses specialized exception classes for different error scenarios:

```python
# Database-related errors
DatabaseError(message="Connection failed", details={...})

# Resource not found
NotFoundError(resource="breed", identifier="arabian", details={...})

# Data validation errors
ValidationError(field="name", value="", message="Name is required")

# Business logic conflicts
ConflictError(message="Breed already exists", existing_data={...})

# External service errors
ExternalServiceError(service="breed-registry", status_code=503)

# Authentication errors
AuthenticationError(message="Invalid credentials")

# Authorization errors
AuthorizationError(resource="admin", action="delete")

# Rate limiting
RateLimitError(limit=100, window="1 hour", retry_after=3600)
```

### Global Exception Handlers

All exceptions are handled consistently with structured responses:

```json
{
  "error": true,
  "error_type": "NotFoundError",
  "message": "Horse breed not found",
  "details": {
    "resource": "breed",
    "identifier": "nonexistent"
  },
  "correlation_id": "req_1234567890abcdef",
  "timestamp": "2024-01-15T10:30:00Z",
  "path": "/api/v1/breeds/nonexistent"
}
```

## 📝 Enhanced Logging System

### Features

- **Structured JSON Logging**: Machine-readable log format
- **Correlation IDs**: Track requests across services
- **Performance Monitoring**: Automatic timing of operations
- **Business Event Logging**: Track important business events
- **Security Event Detection**: Monitor security-related events
- **Async File Handlers**: Non-blocking log writes
- **Log Sampling**: Efficient logging for high-traffic scenarios
- **Multiple Destinations**: Console, files, error logs, security logs

### Log Structure

```json
{
  "@timestamp": "2024-01-15T10:30:00.123Z",
  "level": "INFO",
  "logger": "horse_breed_service",
  "message": "Breed retrieved successfully",
  "correlation_id": "req_1234567890abcdef",
  "user_id": "user123",
  "request_id": "req_1234567890abcdef",
  "method": "GET",
  "path": "/api/v1/breeds/arabian",
  "status_code": 200,
  "response_time": 45.67,
  "business_event": {
    "type": "breed_accessed",
    "breed": "arabian",
    "user": "user123"
  },
  "performance": {
    "db_query_time": 12.34,
    "total_time": 45.67
  },
  "system": {
    "hostname": "server01",
    "process_id": 1234,
    "memory_mb": 156.7,
    "cpu_percent": 2.3
  }
}
```

### Log Files

| File | Purpose | Rotation |
|------|---------|----------|
| `horse_breed_service.log` | General application logs | Daily |
| `horse_breed_service_errors.log` | Error and warning logs | Daily |
| `security_events.log` | Security-related events | Daily |
| `performance.log` | Performance metrics | Daily |
| `access.log` | HTTP access logs | Daily |

## 🛡️ Middleware Stack

### Request Tracking Middleware
- Generates unique correlation IDs for each request
- Tracks request timing and response codes
- Adds security headers to responses

### Security Middleware
- Content Security Policy headers
- HSTS (HTTP Strict Transport Security)
- Frame options protection
- Content type sniffing protection

### Rate Limiting Middleware
- Configurable rate limits per endpoint
- IP-based limiting with whitelist support
- Graceful degradation under load

## 📈 Performance Monitoring

### Automatic Performance Tracking

Use the `@log_performance` decorator to monitor function execution:

```python
from app.core.enhanced_logging import log_performance

@log_performance
async def get_breed(breed_name: str):
    # Function execution time is automatically logged
    return await horse_breed_service.get_breed(breed_name)
```

### Metrics Collection

The system automatically collects:
- Request count and rate
- Response times (avg, min, max, percentiles)
- Error rates by status code
- System resource usage
- Database query performance
- Cache hit/miss rates

## 🎯 Business Event Logging

Track important business events with structured logging:

```python
from app.core.enhanced_logging import log_business_event

# Log breed creation
log_business_event(
    event_type="breed_created",
    breed=breed_data.name,
    user=current_user.id,
    metadata={"source": "api", "validation_passed": True}
)

# Log search operations
log_business_event(
    event_type="breed_searched",
    query=search_term,
    results_count=len(results)
)
```

## 🔒 Security Event Detection

Automatic detection and logging of security events:

- Failed authentication attempts
- Suspicious request patterns
- Rate limit violations
- Invalid input attempts
- Privilege escalation attempts

## 📊 Monitoring Dashboard

The HTML dashboard provides real-time monitoring with:

### System Overview
- Service health status
- Uptime and version information
- Component health (database, filesystem, memory)

### Performance Metrics
- Request throughput and response times
- Error rates and status code distribution
- System resource utilization (CPU, memory, disk)

### Error Analysis
- Recent error logs with filtering
- Error distribution by type and endpoint
- Correlation ID tracking for debugging

### Interactive Charts
- Performance trends over time
- Error distribution visualization
- Resource usage graphs

## 🧪 Testing

### Run Comprehensive Tests
```bash
# Test all monitoring features
python test_monitoring.py

# Test with custom URL
python test_monitoring.py --url http://your-service:8000

# Test with startup delay
python test_monitoring.py --wait 10
```

### Test Coverage
- Health check endpoints
- Metrics collection accuracy
- Error handling consistency
- Log file creation and rotation
- Concurrent request handling
- API documentation accessibility

## 🔧 Configuration

### Environment Variables

```bash
# Logging configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_SAMPLING_RATE=1.0

# Monitoring settings
METRICS_ENABLED=true
PERFORMANCE_MONITORING=true
SECURITY_EVENTS=true

# Rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
```

### Advanced Configuration

Customize logging in `app/core/enhanced_logging.py`:

```python
# Adjust log sampling for high traffic
LOG_SAMPLING_RATE = 0.1  # Log 10% of requests

# Configure async handler buffer size
ASYNC_HANDLER_CAPACITY = 10000

# Set custom log rotation
file_handler = TimedRotatingFileHandler(
    filename="logs/app.log",
    when="midnight",
    interval=1,
    backupCount=30
)
```

## 🚨 Alerting Integration

### Prometheus Metrics
Export metrics for Prometheus scraping:

```python
from prometheus_client import Counter, Histogram, Gauge

request_count = Counter('http_requests_total', 'Total HTTP requests')
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')
active_connections = Gauge('active_connections', 'Active connections')
```

### Webhook Notifications
Configure webhook alerts for critical events:

```python
from app.core.enhanced_logging import configure_webhook_alerts

configure_webhook_alerts(
    webhook_url="https://your-webhook-endpoint.com/alerts",
    events=["critical_error", "service_down", "high_error_rate"]
)
```

## 📋 Troubleshooting

### Common Issues

1. **Missing psutil dependency**
   ```bash
   pip install psutil==6.0.0
   ```

2. **Log files not created**
   - Check directory permissions for `logs/` folder
   - Ensure service has write access

3. **Monitoring endpoints return 500**
   - Check database connectivity
   - Verify all dependencies are installed

4. **Dashboard not loading data**
   - Ensure service is running on correct port
   - Check browser console for CORS issues

### Debug Mode

Enable debug logging for troubleshooting:

```python
import logging
logging.getLogger('app').setLevel(logging.DEBUG)
```

## 🏗️ Production Deployment

### Docker Configuration

```dockerfile
FROM python:3.12-slim

# Install system dependencies for monitoring
RUN apt-get update && apt-get install -y \
    procps \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /app
WORKDIR /app

# Create logs directory
RUN mkdir -p logs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/monitoring/health || exit 1

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: horse-breed-service
spec:
  template:
    spec:
      containers:
      - name: horse-breed-service
        image: horse-breed-service:latest
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /api/v1/monitoring/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/monitoring/health/detailed
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

## 📚 Additional Resources

### Log Analysis Tools
- **ELK Stack**: Elasticsearch, Logstash, Kibana for log analysis
- **Grafana**: Dashboard visualization for metrics
- **Jaeger**: Distributed tracing with correlation IDs

### Monitoring Integrations
- **DataDog**: APM and infrastructure monitoring
- **New Relic**: Application performance monitoring
- **Sentry**: Error tracking and performance monitoring

### Best Practices
1. **Correlation IDs**: Always include in external service calls
2. **Structured Logging**: Use consistent JSON format
3. **Performance Budgets**: Set alerts for response time thresholds
4. **Error Rate Monitoring**: Alert on error rates > 1%
5. **Health Check Design**: Keep health checks lightweight

## 🤝 Contributing

When adding new monitoring features:

1. Update this documentation
2. Add tests to `test_monitoring.py`
3. Include performance considerations
4. Follow structured logging patterns
5. Update the monitoring dashboard if needed

## 📄 License

This monitoring system is part of the Horse Breed Service and follows the same license terms.

---

For support or questions about the monitoring system, please refer to the main project documentation or create an issue in the project repository.