"""
Performance monitoring and metrics collection for Lumen storage system.

This module provides comprehensive monitoring of storage performance,
caching effectiveness, and system health metrics.
"""

import asyncio
import logging
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
import json
import psutil

from ..storage.interfaces import ICacheService, IStorageService

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Individual performance metric data point"""
    timestamp: datetime
    metric_name: str
    value: float
    unit: str
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class SystemSnapshot:
    """System resource snapshot"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_sent_mb: float
    network_recv_mb: float
    active_connections: int


class PerformanceMonitor:
    """
    Comprehensive performance monitoring system.
    
    Tracks storage operations, caching effectiveness, system resources,
    and provides real-time metrics and historical analysis.
    """
    
    def __init__(self, 
                 storage_service: IStorageService,
                 cache_service: ICacheService,
                 max_history_points: int = 1000,
                 collection_interval: int = 30):
        """
        Initialize performance monitor.
        
        Args:
            storage_service: Storage service to monitor
            cache_service: Cache service to monitor
            max_history_points: Maximum historical data points to keep
            collection_interval: Seconds between automatic collections
        """
        self.storage_service = storage_service
        self.cache_service = cache_service
        self.max_history_points = max_history_points
        self.collection_interval = collection_interval
        
        # Metrics storage
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history_points))
        self.system_snapshots = deque(maxlen=max_history_points)
        
        # Operation tracking
        self.operation_stats = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'error_count': 0,
            'last_operation': None
        })
        
        # Request tracking (for rate limiting and analytics)
        self.request_log = deque(maxlen=10000)  # Last 10k requests
        
        # Cache effectiveness tracking
        self.cache_stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'cache_errors': 0,
            'hit_rate_history': deque(maxlen=100)
        }
        
        # System baseline (for alerting)
        self.baseline_metrics = {}
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_usage_percent': 90.0,
            'response_time_ms': 1000.0,
            'error_rate_percent': 5.0
        }
        
        # Monitoring state
        self._monitoring_active = False
        self._collection_task = None
        
        logger.info("PerformanceMonitor initialized")
    
    async def start_monitoring(self):
        """Start automatic performance data collection"""
        if self._monitoring_active:
            logger.warning("Performance monitoring already active")
            return
        
        self._monitoring_active = True
        self._collection_task = asyncio.create_task(self._collection_loop())
        logger.info(f"Performance monitoring started (interval: {self.collection_interval}s)")
    
    async def stop_monitoring(self):
        """Stop automatic performance data collection"""
        self._monitoring_active = False
        if self._collection_task:
            self._collection_task.cancel()
            try:
                await self._collection_task
            except asyncio.CancelledError:
                pass
        logger.info("Performance monitoring stopped")
    
    @asynccontextmanager
    async def track_operation(self, operation_name: str, **tags):
        """
        Context manager to track operation performance.
        
        Usage:
            async with monitor.track_operation('image_upload', user_id=user_id):
                # perform operation
        """
        start_time = time.time()
        error_occurred = False
        
        try:
            yield
        except Exception as e:
            error_occurred = True
            self.operation_stats[operation_name]['error_count'] += 1
            logger.error(f"Operation {operation_name} failed: {e}")
            raise
        finally:
            duration = time.time() - start_time
            
            # Update operation statistics
            stats = self.operation_stats[operation_name]
            stats['count'] += 1
            stats['total_time'] += duration
            stats['last_operation'] = datetime.utcnow()
            
            # Record metric
            await self._record_metric(
                f"{operation_name}_duration",
                duration * 1000,  # Convert to milliseconds
                "ms",
                tags
            )
            
            # Log slow operations
            if duration > 2.0:  # More than 2 seconds
                logger.warning(f"Slow operation: {operation_name} took {duration:.2f}s")

    async def track_request(self, method: str, endpoint: str, status_code: int, response_time_ms: float):
        """Track HTTP request metrics"""
        
        request_data = {
            'timestamp': datetime.utcnow(),
            'method': method,
            'endpoint': endpoint,
            'status_code': status_code,
            'response_time_ms': response_time_ms
        }
        
        self.request_log.append(request_data)
        
        # Record metrics
        await self._record_metric("response_time", response_time_ms, "ms", {
            'method': method,
            'endpoint': endpoint,
            'status': str(status_code)
        })
        
        # Track error rates
        if status_code >= 400:
            await self._record_metric("request_error", 1, "count", {
                'method': method,
                'endpoint': endpoint,
                'status': str(status_code)
            })

    async def track_cache_operation(self, operation: str, hit: bool, error: bool = False):
        """Track cache operation effectiveness"""
        
        self.cache_stats['total_requests'] += 1
        
        if error:
            self.cache_stats['cache_errors'] += 1
        elif hit:
            self.cache_stats['cache_hits'] += 1
        else:
            self.cache_stats['cache_misses'] += 1
        
        # Calculate current hit rate
        total_ops = self.cache_stats['cache_hits'] + self.cache_stats['cache_misses']
        if total_ops > 0:
            hit_rate = (self.cache_stats['cache_hits'] / total_ops) * 100
            self.cache_stats['hit_rate_history'].append({
                'timestamp': datetime.utcnow(),
                'hit_rate': hit_rate
            })

    async def get_performance_summary(self) -> Dict[str, Union[float, int, str]]:
        """Get current performance summary"""
        
        # System metrics
        system_snapshot = await self._collect_system_metrics()
        
        # Storage health
        storage_health = await self.storage_service.health_check()
        storage_metrics = self.storage_service.get_metrics()
        
        # Cache statistics
        cache_stats = await self.cache_service.get_cache_stats()
        
        # Calculate operation averages
        operation_averages = {}
        for op_name, stats in self.operation_stats.items():
            if stats['count'] > 0:
                avg_time = (stats['total_time'] / stats['count']) * 1000  # ms
                error_rate = (stats['error_count'] / stats['count']) * 100
                operation_averages[op_name] = {
                    'avg_response_time_ms': round(avg_time, 2),
                    'error_rate_percent': round(error_rate, 2),
                    'total_operations': stats['count']
                }
        
        # Recent request metrics
        recent_requests = self._get_recent_request_stats(minutes=5)
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'system': {
                'cpu_percent': system_snapshot.cpu_percent,
                'memory_percent': system_snapshot.memory_percent,
                'disk_usage_percent': system_snapshot.disk_usage_percent,
                'active_connections': system_snapshot.active_connections
            },
            'storage': {
                'healthy': storage_health.get('healthy', False),
                'disk_usage_percent': storage_health.get('disk_usage_percent', 0),
                'avg_upload_time_ms': storage_metrics.upload_time * 1000,
                'avg_processing_time_ms': storage_metrics.processing_time * 1000
            },
            'cache': {
                'hit_rate_percent': cache_stats.get('hit_rate_percent', 0),
                'total_hits': cache_stats.get('total_hits', 0),
                'total_misses': cache_stats.get('total_misses', 0),
                'memory_usage_mb': cache_stats.get('memory_usage_bytes', 0) / 1024 / 1024
            },
            'operations': operation_averages,
            'requests': {
                'requests_per_minute': recent_requests['requests_per_minute'],
                'avg_response_time_ms': recent_requests['avg_response_time_ms'],
                'error_rate_percent': recent_requests['error_rate_percent']
            }
        }

    async def get_detailed_metrics(self, metric_name: str, hours: int = 1) -> List[Dict]:
        """Get detailed historical metrics"""
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        if metric_name not in self.metrics_history:
            return []
        
        filtered_metrics = []
        for metric in self.metrics_history[metric_name]:
            if metric.timestamp >= cutoff_time:
                filtered_metrics.append({
                    'timestamp': metric.timestamp.isoformat(),
                    'value': metric.value,
                    'unit': metric.unit,
                    'tags': metric.tags
                })
        
        return filtered_metrics

    async def check_alert_conditions(self) -> List[Dict[str, str]]:
        """Check for alert conditions and return list of active alerts"""
        
        alerts = []
        
        # Get latest system snapshot
        if self.system_snapshots:
            latest = self.system_snapshots[-1]
            
            # CPU usage alert
            if latest.cpu_percent > self.alert_thresholds['cpu_percent']:
                alerts.append({
                    'type': 'high_cpu',
                    'severity': 'warning',
                    'message': f"High CPU usage: {latest.cpu_percent:.1f}%",
                    'threshold': self.alert_thresholds['cpu_percent']
                })
            
            # Memory usage alert
            if latest.memory_percent > self.alert_thresholds['memory_percent']:
                alerts.append({
                    'type': 'high_memory',
                    'severity': 'warning',
                    'message': f"High memory usage: {latest.memory_percent:.1f}%",
                    'threshold': self.alert_thresholds['memory_percent']
                })
            
            # Disk usage alert
            if latest.disk_usage_percent > self.alert_thresholds['disk_usage_percent']:
                alerts.append({
                    'type': 'high_disk_usage',
                    'severity': 'critical',
                    'message': f"High disk usage: {latest.disk_usage_percent:.1f}%",
                    'threshold': self.alert_thresholds['disk_usage_percent']
                })
        
        # Check operation error rates
        for op_name, stats in self.operation_stats.items():
            if stats['count'] > 10:  # Only alert if we have enough samples
                error_rate = (stats['error_count'] / stats['count']) * 100
                if error_rate > self.alert_thresholds['error_rate_percent']:
                    alerts.append({
                        'type': 'high_error_rate',
                        'severity': 'warning',
                        'message': f"High error rate for {op_name}: {error_rate:.1f}%",
                        'threshold': self.alert_thresholds['error_rate_percent']
                    })
        
        return alerts

    async def export_metrics(self, format: str = 'json') -> str:
        """Export metrics data in various formats"""
        
        summary = await self.get_performance_summary()
        
        if format.lower() == 'json':
            return json.dumps(summary, indent=2, default=str)
        elif format.lower() == 'prometheus':
            return self._format_prometheus_metrics(summary)
        else:
            raise ValueError(f"Unsupported format: {format}")

    async def _collection_loop(self):
        """Background loop for collecting performance data"""
        
        while self._monitoring_active:
            try:
                # Collect system metrics
                system_snapshot = await self._collect_system_metrics()
                self.system_snapshots.append(system_snapshot)
                
                # Record system metrics as individual metrics
                await self._record_metric("cpu_percent", system_snapshot.cpu_percent, "percent")
                await self._record_metric("memory_percent", system_snapshot.memory_percent, "percent")
                await self._record_metric("disk_usage_percent", system_snapshot.disk_usage_percent, "percent")
                
                # Update cache effectiveness
                if self.cache_stats['hit_rate_history']:
                    latest_hit_rate = self.cache_stats['hit_rate_history'][-1]['hit_rate']
                    await self._record_metric("cache_hit_rate", latest_hit_rate, "percent")
                
                logger.debug("Performance metrics collected")
                
            except Exception as e:
                logger.error(f"Error collecting performance metrics: {e}")
            
            await asyncio.sleep(self.collection_interval)

    async def _collect_system_metrics(self) -> SystemSnapshot:
        """Collect current system resource metrics"""
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_usage_percent = (disk.used / disk.total) * 100
        
        # Disk I/O
        disk_io = psutil.disk_io_counters()
        disk_io_read_mb = disk_io.read_bytes / 1024 / 1024
        disk_io_write_mb = disk_io.write_bytes / 1024 / 1024
        
        # Network I/O
        network_io = psutil.net_io_counters()
        network_sent_mb = network_io.bytes_sent / 1024 / 1024
        network_recv_mb = network_io.bytes_recv / 1024 / 1024
        
        # Connection count (approximate)
        active_connections = len(psutil.net_connections())
        
        return SystemSnapshot(
            timestamp=datetime.utcnow(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_usage_percent=disk_usage_percent,
            disk_io_read_mb=disk_io_read_mb,
            disk_io_write_mb=disk_io_write_mb,
            network_sent_mb=network_sent_mb,
            network_recv_mb=network_recv_mb,
            active_connections=active_connections
        )

    async def _record_metric(self, metric_name: str, value: float, unit: str, tags: Dict[str, str] = None):
        """Record a performance metric"""
        
        metric = PerformanceMetric(
            timestamp=datetime.utcnow(),
            metric_name=metric_name,
            value=value,
            unit=unit,
            tags=tags or {}
        )
        
        self.metrics_history[metric_name].append(metric)

    def _get_recent_request_stats(self, minutes: int = 5) -> Dict[str, float]:
        """Get statistics for recent requests"""
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        recent_requests = [r for r in self.request_log if r['timestamp'] >= cutoff_time]
        
        if not recent_requests:
            return {
                'requests_per_minute': 0.0,
                'avg_response_time_ms': 0.0,
                'error_rate_percent': 0.0
            }
        
        # Requests per minute
        requests_per_minute = len(recent_requests) / minutes
        
        # Average response time
        total_response_time = sum(r['response_time_ms'] for r in recent_requests)
        avg_response_time_ms = total_response_time / len(recent_requests)
        
        # Error rate
        error_requests = [r for r in recent_requests if r['status_code'] >= 400]
        error_rate_percent = (len(error_requests) / len(recent_requests)) * 100
        
        return {
            'requests_per_minute': round(requests_per_minute, 2),
            'avg_response_time_ms': round(avg_response_time_ms, 2),
            'error_rate_percent': round(error_rate_percent, 2)
        }

    def _format_prometheus_metrics(self, summary: Dict) -> str:
        """Format metrics in Prometheus format"""
        
        metrics_lines = []
        
        # System metrics
        metrics_lines.append(f"lumen_cpu_percent {summary['system']['cpu_percent']}")
        metrics_lines.append(f"lumen_memory_percent {summary['system']['memory_percent']}")
        metrics_lines.append(f"lumen_disk_usage_percent {summary['system']['disk_usage_percent']}")
        
        # Storage metrics
        metrics_lines.append(f"lumen_storage_healthy {1 if summary['storage']['healthy'] else 0}")
        metrics_lines.append(f"lumen_upload_time_ms {summary['storage']['avg_upload_time_ms']}")
        
        # Cache metrics
        metrics_lines.append(f"lumen_cache_hit_rate_percent {summary['cache']['hit_rate_percent']}")
        metrics_lines.append(f"lumen_cache_hits_total {summary['cache']['total_hits']}")
        
        # Request metrics
        metrics_lines.append(f"lumen_requests_per_minute {summary['requests']['requests_per_minute']}")
        metrics_lines.append(f"lumen_response_time_ms {summary['requests']['avg_response_time_ms']}")
        
        return '\n'.join(metrics_lines) + '\n'


# Global performance monitor instance
_global_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> Optional[PerformanceMonitor]:
    """Get the global performance monitor instance"""
    return _global_monitor


def initialize_performance_monitor(storage_service: IStorageService, 
                                 cache_service: ICacheService) -> PerformanceMonitor:
    """Initialize the global performance monitor"""
    global _global_monitor
    
    _global_monitor = PerformanceMonitor(storage_service, cache_service)
    return _global_monitor