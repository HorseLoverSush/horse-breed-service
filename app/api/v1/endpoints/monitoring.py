"""
Monitoring endpoints for the Horse Breed Service.

Provides real-time metrics, health checks, and logging information
for monitoring and observability.
"""
import platform
import psutil
import time
from datetime import datetime, timezone
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel

from app.core.enhanced_logging import get_logger, get_metrics_summary


# Pydantic models for response schemas
class HealthStatus(BaseModel):
    status: str
    timestamp: str
    version: str
    uptime_seconds: float


class SystemMetrics(BaseModel):
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    disk_usage_percent: float
    open_files: int
    network_connections: int


class ServiceMetrics(BaseModel):
    total_requests: int
    total_errors: int
    average_response_time: float
    requests_per_second: float
    error_rate: float


class DetailedHealthCheck(BaseModel):
    status: str
    timestamp: str
    version: str
    uptime_seconds: float
    system: SystemMetrics
    service: ServiceMetrics
    components: Dict[str, str]


class LogMetrics(BaseModel):
    total_log_entries: int
    log_levels: Dict[str, int]
    recent_errors: List[Dict[str, Any]]
    log_files: List[Dict[str, Any]]


# Create router for monitoring endpoints
router = APIRouter()
logger = get_logger("monitoring")

# Track service start time
SERVICE_START_TIME = time.time()


def get_system_metrics() -> SystemMetrics:
    """Get current system metrics."""
    try:
        process = psutil.Process()
        disk_usage = psutil.disk_usage('/')
        
        return SystemMetrics(
            cpu_percent=round(process.cpu_percent(), 2),
            memory_percent=round(process.memory_percent(), 2),
            memory_mb=round(process.memory_info().rss / 1024 / 1024, 2),
            disk_usage_percent=round(disk_usage.percent, 2),
            open_files=len(process.open_files()),
            network_connections=len(process.connections())
        )
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        return SystemMetrics(
            cpu_percent=0.0,
            memory_percent=0.0,
            memory_mb=0.0,
            disk_usage_percent=0.0,
            open_files=0,
            network_connections=0
        )


def get_service_metrics() -> ServiceMetrics:
    """Get service-level metrics."""
    try:
        metrics = get_metrics_summary()
        return ServiceMetrics(
            total_requests=metrics.get('total_requests', 0),
            total_errors=metrics.get('total_errors', 0),
            average_response_time=metrics.get('average_response_time', 0.0),
            requests_per_second=metrics.get('requests_per_second', 0.0),
            error_rate=metrics.get('error_rate', 0.0)
        )
    except Exception as e:
        logger.error(f"Failed to get service metrics: {e}")
        return ServiceMetrics(
            total_requests=0,
            total_errors=0,
            average_response_time=0.0,
            requests_per_second=0.0,
            error_rate=0.0
        )


def check_component_health() -> Dict[str, str]:
    """Check health of various system components."""
    components = {}
    
    # Database connectivity check
    try:
        from app.db.database import engine
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        components["database"] = "healthy"
    except Exception as e:
        components["database"] = f"unhealthy: {str(e)[:100]}"
        logger.error(f"Database health check failed: {e}")
    
    # File system check
    try:
        import tempfile
        with tempfile.NamedTemporaryFile(delete=True) as tmp:
            tmp.write(b"health check")
            tmp.flush()
        components["filesystem"] = "healthy"
    except Exception as e:
        components["filesystem"] = f"unhealthy: {str(e)[:100]}"
        logger.error(f"Filesystem health check failed: {e}")
    
    # Memory check
    try:
        memory = psutil.virtual_memory()
        if memory.percent > 90:
            components["memory"] = "warning: high usage"
        else:
            components["memory"] = "healthy"
    except Exception as e:
        components["memory"] = f"unknown: {str(e)[:100]}"
    
    return components


@router.get("/health", response_model=HealthStatus)
async def basic_health_check(response: Response):
    """
    Basic health check endpoint.
    Returns minimal health information for load balancers.
    Optimized for frequent polling by load balancers and monitoring systems.
    """
    # Add cache headers to prevent unnecessary load
    response.headers["Cache-Control"] = "no-cache, max-age=0"
    response.headers["X-Health-Check"] = "basic"
    
    uptime = time.time() - SERVICE_START_TIME
    
    return HealthStatus(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="1.0.0",  # This could come from settings
        uptime_seconds=round(uptime, 2)
    )


@router.get("/health/detailed", response_model=DetailedHealthCheck)
async def detailed_health_check():
    """
    Detailed health check with system and service metrics.
    """
    uptime = time.time() - SERVICE_START_TIME
    system_metrics = get_system_metrics()
    service_metrics = get_service_metrics()
    components = check_component_health()
    
    # Determine overall health status
    overall_status = "healthy"
    if any("unhealthy" in status for status in components.values()):
        overall_status = "unhealthy"
    elif any("warning" in status for status in components.values()):
        overall_status = "degraded"
    
    return DetailedHealthCheck(
        status=overall_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="1.0.0",
        uptime_seconds=round(uptime, 2),
        system=system_metrics,
        service=service_metrics,
        components=components
    )


@router.get("/metrics")
async def get_application_metrics(response: Response):
    """
    Get comprehensive application metrics.
    
    Note: In production, consider restricting access to this endpoint
    to internal networks or authenticated monitoring systems only.
    """
    # Add Prometheus-compatible headers
    response.headers["Content-Type"] = "application/json"
    response.headers["X-Metrics-Version"] = "1.0"
    
    try:
        # Get service metrics
        service_metrics = get_metrics_summary()
        
        # Get system information
        system_info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
            "cpu_count": psutil.cpu_count(),
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
        }
        
        # Get current system metrics
        system_metrics = get_system_metrics()
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": service_metrics,
            "system": system_metrics.dict(),
            "system_info": system_info,
            "uptime_seconds": round(time.time() - SERVICE_START_TIME, 2)
        }
    except Exception as e:
        logger.error(f"Failed to get application metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")


@router.get("/metrics/performance")
async def get_performance_metrics():
    """
    Get performance-specific metrics.
    """
    try:
        metrics = get_metrics_summary()
        
        # Extract performance-related metrics
        performance_data = {
            "request_metrics": {
                "total_requests": metrics.get("total_requests", 0),
                "requests_per_second": metrics.get("requests_per_second", 0.0),
                "average_response_time": metrics.get("average_response_time", 0.0)
            },
            "error_metrics": {
                "total_errors": metrics.get("total_errors", 0),
                "error_rate": metrics.get("error_rate", 0.0),
                "status_codes": metrics.get("status_codes", {})
            },
            "endpoint_metrics": metrics.get("top_endpoints", {}),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return performance_data
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve performance metrics")


@router.get("/logs/metrics")
async def get_log_metrics():
    """
    Get logging-related metrics and recent log entries.
    """
    try:
        from pathlib import Path
        import json
        
        log_dir = Path("logs")
        log_files_info = []
        recent_errors = []
        log_levels = {"DEBUG": 0, "INFO": 0, "WARNING": 0, "ERROR": 0, "CRITICAL": 0}
        total_entries = 0
        
        if log_dir.exists():
            for log_file in log_dir.glob("*.log"):
                try:
                    size_mb = log_file.stat().st_size / (1024 * 1024)
                    modified_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                    
                    log_files_info.append({
                        "name": log_file.name,
                        "size_mb": round(size_mb, 2),
                        "modified": modified_time.isoformat(),
                        "path": str(log_file)
                    })
                    
                    # Try to read recent entries from error log
                    if "error" in log_file.name.lower():
                        try:
                            with open(log_file, 'r', encoding='utf-8') as f:
                                lines = f.readlines()[-10:]  # Last 10 lines
                                for line in lines:
                                    try:
                                        log_entry = json.loads(line.strip())
                                        if log_entry.get("level") in ["ERROR", "CRITICAL"]:
                                            recent_errors.append({
                                                "timestamp": log_entry.get("@timestamp"),
                                                "level": log_entry.get("level"),
                                                "message": log_entry.get("message"),
                                                "logger": log_entry.get("logger")
                                            })
                                            total_entries += 1
                                            log_levels[log_entry.get("level", "INFO")] += 1
                                    except (json.JSONDecodeError, KeyError):
                                        continue
                        except Exception:
                            continue
                            
                except Exception as e:
                    logger.warning(f"Could not process log file {log_file}: {e}")
        
        return LogMetrics(
            total_log_entries=total_entries,
            log_levels=log_levels,
            recent_errors=recent_errors[-5:],  # Last 5 errors
            log_files=log_files_info
        )
        
    except Exception as e:
        logger.error(f"Failed to get log metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve log metrics")


@router.get("/status")
async def get_service_status():
    """
    Get overall service status summary.
    """
    try:
        uptime = time.time() - SERVICE_START_TIME
        components = check_component_health()
        metrics = get_service_metrics()
        
        # Determine status based on components and metrics
        status = "healthy"
        if any("unhealthy" in str(comp_status) for comp_status in components.values()):
            status = "unhealthy"
        elif metrics.error_rate > 10.0:  # More than 10% error rate
            status = "degraded"
        elif any("warning" in str(comp_status) for comp_status in components.values()):
            status = "degraded"
        
        return {
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": round(uptime, 2),
            "uptime_human": f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m {int(uptime % 60)}s",
            "version": "1.0.0",
            "environment": "development",  # This could come from settings
            "components": components,
            "quick_metrics": {
                "total_requests": metrics.total_requests,
                "error_rate": f"{metrics.error_rate}%",
                "avg_response_time": f"{metrics.average_response_time}ms"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get service status: {e}")
        return {
            "status": "unknown",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }