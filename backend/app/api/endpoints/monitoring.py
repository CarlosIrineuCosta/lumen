"""
API endpoints for monitoring and performance metrics.

Provides endpoints to access storage performance, system health,
and operational metrics for the Lumen application.
"""

from datetime import datetime
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import PlainTextResponse

from ...monitoring.performance_monitor import get_performance_monitor
from ...auth_middleware import get_current_user, AuthUser

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/health")
async def get_health_status():
    """
    Get overall system health status.
    
    Returns basic health information without requiring authentication.
    """
    monitor = get_performance_monitor()
    
    if not monitor:
        return {
            "status": "unknown",
            "message": "Performance monitoring not initialized",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    try:
        # Get basic health metrics
        summary = await monitor.get_performance_summary()
        alerts = await monitor.check_alert_conditions()
        
        # Determine overall health status
        critical_alerts = [a for a in alerts if a.get('severity') == 'critical']
        warning_alerts = [a for a in alerts if a.get('severity') == 'warning']
        
        if critical_alerts:
            status = "critical"
            message = f"{len(critical_alerts)} critical issues detected"
        elif warning_alerts:
            status = "warning"
            message = f"{len(warning_alerts)} warnings detected"
        else:
            status = "healthy"
            message = "All systems operational"
        
        return {
            "status": status,
            "message": message,
            "timestamp": summary["timestamp"],
            "system": {
                "cpu_percent": summary["system"]["cpu_percent"],
                "memory_percent": summary["system"]["memory_percent"],
                "disk_usage_percent": summary["system"]["disk_usage_percent"]
            },
            "storage_healthy": summary["storage"]["healthy"],
            "cache_hit_rate": summary["cache"]["hit_rate_percent"],
            "active_alerts": len(alerts)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Health check failed: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/metrics")
async def get_performance_metrics(
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Get comprehensive performance metrics.
    
    Requires authentication to access detailed metrics.
    """
    monitor = get_performance_monitor()
    
    if not monitor:
        raise HTTPException(
            status_code=503,
            detail="Performance monitoring not available"
        )
    
    try:
        summary = await monitor.get_performance_summary()
        alerts = await monitor.check_alert_conditions()
        
        return {
            "performance": summary,
            "alerts": alerts,
            "monitoring_info": {
                "collection_interval_seconds": monitor.collection_interval,
                "max_history_points": monitor.max_history_points,
                "monitoring_active": monitor._monitoring_active
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get performance metrics: {str(e)}"
        )


@router.get("/metrics/prometheus")
async def get_prometheus_metrics(
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Get metrics in Prometheus format for scraping.
    
    Returns metrics formatted for Prometheus monitoring system.
    """
    monitor = get_performance_monitor()
    
    if not monitor:
        raise HTTPException(
            status_code=503,
            detail="Performance monitoring not available"
        )
    
    try:
        prometheus_metrics = await monitor.export_metrics(format='prometheus')
        return PlainTextResponse(
            content=prometheus_metrics,
            media_type="text/plain"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export Prometheus metrics: {str(e)}"
        )


@router.get("/metrics/detailed/{metric_name}")
async def get_detailed_metrics(
    metric_name: str,
    hours: int = Query(default=1, ge=1, le=24),
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Get detailed historical data for a specific metric.
    
    Args:
        metric_name: Name of the metric to retrieve
        hours: Number of hours of history to return (1-24)
    """
    monitor = get_performance_monitor()
    
    if not monitor:
        raise HTTPException(
            status_code=503,
            detail="Performance monitoring not available"
        )
    
    try:
        metrics_data = await monitor.get_detailed_metrics(metric_name, hours)
        
        return {
            "metric_name": metric_name,
            "hours_requested": hours,
            "data_points": len(metrics_data),
            "data": metrics_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get detailed metrics: {str(e)}"
        )


@router.get("/alerts")
async def get_active_alerts(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get currently active alerts and their details."""
    
    monitor = get_performance_monitor()
    
    if not monitor:
        raise HTTPException(
            status_code=503,
            detail="Performance monitoring not available"
        )
    
    try:
        alerts = await monitor.check_alert_conditions()
        
        # Group alerts by severity
        critical_alerts = [a for a in alerts if a.get('severity') == 'critical']
        warning_alerts = [a for a in alerts if a.get('severity') == 'warning']
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_alerts": len(alerts),
            "critical_count": len(critical_alerts),
            "warning_count": len(warning_alerts),
            "alerts": {
                "critical": critical_alerts,
                "warning": warning_alerts
            },
            "alert_summary": {
                alert['type']: alert['message'] 
                for alert in alerts
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get alerts: {str(e)}"
        )


@router.get("/storage/stats")
async def get_storage_statistics(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get detailed storage service statistics."""
    
    monitor = get_performance_monitor()
    
    if not monitor:
        raise HTTPException(
            status_code=503,
            detail="Performance monitoring not available"
        )
    
    try:
        # Get storage health and metrics
        storage_health = await monitor.storage_service.health_check()
        storage_metrics = monitor.storage_service.get_metrics()
        
        # Get operation statistics
        operation_stats = {}
        for op_name, stats in monitor.operation_stats.items():
            if 'upload' in op_name or 'storage' in op_name:
                operation_stats[op_name] = {
                    'total_operations': stats['count'],
                    'error_count': stats['error_count'],
                    'avg_time_ms': (stats['total_time'] / stats['count'] * 1000) if stats['count'] > 0 else 0,
                    'error_rate_percent': (stats['error_count'] / stats['count'] * 100) if stats['count'] > 0 else 0,
                    'last_operation': stats['last_operation'].isoformat() if stats['last_operation'] else None
                }
        
        return {
            "storage_health": storage_health,
            "performance_metrics": {
                "avg_upload_time_ms": storage_metrics.upload_time * 1000,
                "avg_processing_time_ms": storage_metrics.processing_time * 1000,
                "cache_hit_rate": storage_metrics.cache_hit_rate,
                "storage_used_bytes": storage_metrics.storage_used,
                "bandwidth_used_bytes": storage_metrics.bandwidth_used
            },
            "operation_statistics": operation_stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get storage statistics: {str(e)}"
        )


@router.get("/cache/stats")
async def get_cache_statistics(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get detailed cache service statistics."""
    
    monitor = get_performance_monitor()
    
    if not monitor:
        raise HTTPException(
            status_code=503,
            detail="Performance monitoring not available"
        )
    
    try:
        # Get cache statistics
        cache_stats = await monitor.cache_service.get_cache_stats()
        
        # Get recent hit rate history
        recent_hit_rates = list(monitor.cache_stats['hit_rate_history'])[-20:]  # Last 20 data points
        
        return {
            "cache_stats": cache_stats,
            "effectiveness": {
                "current_hit_rate_percent": cache_stats.get('hit_rate_percent', 0),
                "total_requests": monitor.cache_stats['total_requests'],
                "hits": monitor.cache_stats['cache_hits'],
                "misses": monitor.cache_stats['cache_misses'],
                "errors": monitor.cache_stats['cache_errors']
            },
            "hit_rate_history": [
                {
                    "timestamp": entry['timestamp'].isoformat(),
                    "hit_rate": entry['hit_rate']
                }
                for entry in recent_hit_rates
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get cache statistics: {str(e)}"
        )


@router.post("/monitoring/start")
async def start_monitoring(
    current_user: AuthUser = Depends(get_current_user)
):
    """Start performance monitoring if not already active."""
    
    monitor = get_performance_monitor()
    
    if not monitor:
        raise HTTPException(
            status_code=503,
            detail="Performance monitoring not available"
        )
    
    try:
        if monitor._monitoring_active:
            return {
                "message": "Performance monitoring already active",
                "status": "active"
            }
        
        await monitor.start_monitoring()
        
        return {
            "message": "Performance monitoring started",
            "status": "started",
            "collection_interval": monitor.collection_interval
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start monitoring: {str(e)}"
        )


@router.post("/monitoring/stop")
async def stop_monitoring(
    current_user: AuthUser = Depends(get_current_user)
):
    """Stop performance monitoring."""
    
    monitor = get_performance_monitor()
    
    if not monitor:
        raise HTTPException(
            status_code=503,
            detail="Performance monitoring not available"
        )
    
    try:
        if not monitor._monitoring_active:
            return {
                "message": "Performance monitoring already inactive",
                "status": "inactive"
            }
        
        await monitor.stop_monitoring()
        
        return {
            "message": "Performance monitoring stopped",
            "status": "stopped"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to stop monitoring: {str(e)}"
        )