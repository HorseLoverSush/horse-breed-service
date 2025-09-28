"""
Production monitoring best practices and security considerations.

This module provides guidance on securing and optimizing monitoring endpoints
for production deployments.
"""

# 🏭 PRODUCTION MONITORING BEST PRACTICES

## 1. SECURITY CONSIDERATIONS

### Access Control
```python
# Option 1: IP Whitelist for monitoring endpoints
ALLOWED_MONITORING_IPS = [
    "10.0.0.0/8",      # Internal network
    "172.16.0.0/12",   # Private network
    "192.168.0.0/16",  # Local network
    "127.0.0.1/32",    # Localhost
]

# Option 2: Authentication for sensitive metrics
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_monitoring_token(token: str = Depends(security)):
    if token.credentials != "your-monitoring-secret":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid monitoring token"
        )
```

### Endpoint Protection
```python
# Apply to sensitive endpoints only
@router.get("/metrics/detailed")
async def detailed_metrics(token: str = Depends(verify_monitoring_token)):
    # Sensitive system information
    pass

# Keep basic health check public for load balancers
@router.get("/health")
async def health_check():
    # Minimal public information
    pass
```

## 2. PERFORMANCE OPTIMIZATION

### Caching Strategy
```python
from functools import lru_cache
import time

@lru_cache(maxsize=1)
def get_cached_system_metrics(cache_time: int):
    """Cache system metrics for 30 seconds to reduce overhead."""
    return get_system_metrics()

@router.get("/metrics")
async def metrics():
    # Cache for 30 seconds
    cache_key = int(time.time() // 30)
    return get_cached_system_metrics(cache_key)
```

### Async Optimization
```python
import asyncio

async def get_all_metrics_async():
    """Gather all metrics concurrently for better performance."""
    tasks = [
        asyncio.create_task(get_system_metrics_async()),
        asyncio.create_task(get_service_metrics_async()),
        asyncio.create_task(check_component_health_async()),
    ]
    return await asyncio.gather(*tasks)
```

## 3. STANDARDIZATION

### Industry Standard Endpoints
Your current implementation already follows these standards:

✅ `/health` - Kubernetes liveness probe
✅ `/health/detailed` - Readiness probe with dependencies
✅ `/metrics` - Prometheus scraping endpoint
✅ `/status` - Overall service status

### Additional Standards to Consider:
```python
@router.get("/ready")  # Alternative readiness check
@router.get("/live")   # Alternative liveness check
@router.get("/info")   # Service information (version, build, etc.)
```

## 4. MONITORING INTEGRATION

### Prometheus Metrics Export
```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Add to your existing endpoints
@router.get("/metrics/prometheus")
async def prometheus_metrics():
    """Export metrics in Prometheus format."""
    return Response(
        content=generate_latest(),
        media_type="text/plain; version=0.0.4; charset=utf-8"
    )
```

### OpenTelemetry Integration
```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Add tracing to monitoring endpoints
tracer = trace.get_tracer(__name__)

@router.get("/health")
async def health_check():
    with tracer.start_as_current_span("health_check") as span:
        span.set_attribute("health.status", "healthy")
        # ... your health check logic
```

## 5. ERROR HANDLING & RELIABILITY

### Circuit Breaker Pattern
```python
import asyncio
from typing import Optional

class HealthCheckCircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    async def call_with_circuit_breaker(self, func):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise HTTPException(503, "Service temporarily unavailable")
        
        try:
            result = await func()
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
            raise
```

## 6. LOGGING & AUDIT

### Monitoring Access Logs
```python
@router.get("/metrics")
async def metrics(request: Request):
    # Log monitoring access for security audit
    logger.info(
        "Metrics accessed",
        extra={
            "client_ip": request.client.host,
            "user_agent": request.headers.get("user-agent"),
            "monitoring_endpoint": "/metrics",
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    # ... return metrics
```

## 7. DEPLOYMENT CONSIDERATIONS

### Kubernetes Configuration
```yaml
# Health check probes configuration
livenessProbe:
  httpGet:
    path: /api/v1/monitoring/health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /api/v1/monitoring/health/detailed
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 10
  failureThreshold: 3

# Service monitor for Prometheus
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: horse-breed-service
spec:
  selector:
    matchLabels:
      app: horse-breed-service
  endpoints:
  - port: http
    path: /api/v1/monitoring/metrics
    interval: 30s
```

### Load Balancer Health Checks
```nginx
# Nginx upstream health check
upstream horse_breed_service {
    server app1:8000 max_fails=3 fail_timeout=30s;
    server app2:8000 max_fails=3 fail_timeout=30s;
}

location /health {
    access_log off;  # Don't log health checks
    proxy_pass http://horse_breed_service/api/v1/monitoring/health;
    proxy_connect_timeout 1s;
    proxy_read_timeout 1s;
}
```

## 8. MONITORING BEST PRACTICES SUMMARY

### ✅ What You're Already Doing Right:
- Lightweight health checks for load balancers
- Detailed health checks with dependency verification
- Comprehensive metrics collection
- Structured response models
- Proper error handling
- System resource monitoring
- Business metrics tracking

### 🔧 Additional Recommendations:
1. **Security**: Add IP whitelisting or authentication for sensitive endpoints
2. **Performance**: Implement caching for expensive operations
3. **Standards**: Consider Prometheus metrics export format
4. **Reliability**: Add circuit breakers for external dependencies
5. **Observability**: Integrate with OpenTelemetry for distributed tracing
6. **Documentation**: Your monitoring guide is excellent!

### 🎯 Priority Implementation Order:
1. **High Priority**: IP whitelisting for production security
2. **Medium Priority**: Prometheus metrics export
3. **Low Priority**: OpenTelemetry integration (for complex systems)

Your current monitoring implementation is **production-ready** and follows industry best practices. The suggestions above are enhancements for specific use cases or enterprise requirements.