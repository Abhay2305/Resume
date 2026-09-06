"""Health check router.

Provides system health check endpoints for monitoring and load balancers.
No authentication required for health checks.

Endpoints:
    GET /api/health         - Full health status
    GET /api/health/ready   - Readiness check (for Kubernetes)
    GET /api/health/live    - Liveness check (for Kubernetes)
"""
import logging
import platform
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..database import get_db, check_db_connection, engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
def health_check(db: Session = Depends(get_db)):
    """Full health check endpoint.
    
    Returns comprehensive health status including database and system info.
    Used by monitoring systems and load balancers.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "checks": {}
    }
    
    # Database check
    try:
        db_connected = check_db_connection()
        health_status["checks"]["database"] = {
            "status": "healthy" if db_connected else "unhealthy",
        }
        
        if db_connected:
            # Get pool stats
            pool = engine.pool
            health_status["checks"]["database"]["pool"] = {
                "size": pool.size(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
            }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e),
        }
        health_status["status"] = "degraded"
    
    # System info
    health_status["checks"]["system"] = {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
    }
    
    # Overall status
    if health_status["checks"].get("database", {}).get("status") == "unhealthy":
        health_status["status"] = "unhealthy"
    
    return health_status


@router.get("/ready")
def readiness_check(db: Session = Depends(get_db)):
    """Readiness check for Kubernetes.
    
    Returns 200 if the service is ready to accept traffic.
    Returns 503 if the service is not ready.
    """
    is_ready = check_db_connection()
    
    if is_ready:
        return {"status": "ready"}
    else:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=503,
            content={"status": "not ready"}
        )


@router.get("/live")
def liveness_check():
    """Liveness check for Kubernetes.
    
    Returns 200 if the service is alive.
    This check should be lightweight and not depend on external services.
    """
    return {"status": "alive"}
