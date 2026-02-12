"""
Health check routes for monitoring and status
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any
import datetime
import psutil
import platform

from ...core.config import settings

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: datetime.datetime
    version: str
    system_info: Dict[str, Any]
    services: Dict[str, str]


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint"""
    
    # System information
    system_info = {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "architecture": platform.machine(),
        "hostname": platform.node(),
        "python_version": platform.python_version(),
        "cpu_count": psutil.cpu_count(),
        "memory_total": psutil.virtual_memory().total,
        "memory_available": psutil.virtual_memory().available,
        "disk_usage": psutil.disk_usage('/').percent
    }
    
    # Service status checks
    services = {
        "database": "healthy",  # TODO: Add actual DB health check
        "redis": "healthy",     # TODO: Add actual Redis health check
        "api": "healthy"
    }
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.datetime.utcnow(),
        version=settings.version,
        system_info=system_info,
        services=services
    )


@router.get("/ready")
async def readiness_check():
    """Kubernetes readiness probe endpoint"""
    # Check if all critical services are ready
    return {"status": "ready", "timestamp": datetime.datetime.utcnow()}


@router.get("/live")
async def liveness_check():
    """Kubernetes liveness probe endpoint"""
    # Simple liveness check
    return {"status": "alive", "timestamp": datetime.datetime.utcnow()}


@router.get("/metrics")
async def metrics():
    """Basic metrics endpoint"""
    # TODO: Integrate with Prometheus metrics
    return {
        "requests_total": 0,
        "requests_duration_seconds": 0.0,
        "active_connections": 0
    }