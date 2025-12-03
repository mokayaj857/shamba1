"""
Monitoring and metrics collection for the API
"""

import time
import threading
from collections import defaultdict, deque
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass, field
import json

# Try to import Prometheus client
try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logging.warning("Prometheus client not available. Metrics will be limited to internal collection.")

logger = logging.getLogger(__name__)

@dataclass
class PredictionMetrics:
    """Metrics for prediction requests"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_processing_time: float = 0.0
    average_processing_time: float = 0.0
    min_processing_time: float = float('inf')
    max_processing_time: float = 0.0
    
    def update(self, processing_time: float, success: bool = True):
        """Update metrics with new request data"""
        self.total_requests += 1
        self.total_processing_time += processing_time
        
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        # Update processing time statistics
        if processing_time < self.min_processing_time:
            self.min_processing_time = processing_time
        if processing_time > self.max_processing_time:
            self.max_processing_time = processing_time
        
        self.average_processing_time = self.total_processing_time / self.total_requests

@dataclass
class FeatureMetrics:
    """Metrics for feature distributions"""
    rainfall_stats: Dict[str, float] = field(default_factory=dict)
    soil_ph_stats: Dict[str, float] = field(default_factory=dict)
    organic_carbon_stats: Dict[str, float] = field(default_factory=dict)
    county_distribution: Dict[str, int] = field(default_factory=dict)
    
    def update(self, rainfall: float, soil_ph: float, organic_carbon: float, county: str):
        """Update feature metrics"""
        # Update county distribution
        self.county_distribution[county] = self.county_distribution.get(county, 0) + 1
        
        # Update numerical feature statistics (simplified rolling stats)
        self._update_numerical_stats('rainfall', rainfall)
        self._update_numerical_stats('soil_ph', soil_ph)
        self._update_numerical_stats('organic_carbon', organic_carbon)
    
    def _update_numerical_stats(self, feature_name: str, value: float):
        """Update numerical feature statistics"""
        stats = getattr(self, f"{feature_name}_stats")
        
        if not stats:
            stats.update({
                'count': 0,
                'sum': 0.0,
                'min': float('inf'),
                'max': float('-inf'),
                'mean': 0.0
            })
        
        stats['count'] += 1
        stats['sum'] += value
        stats['min'] = min(stats['min'], value)
        stats['max'] = max(stats['max'], value)
        stats['mean'] = stats['sum'] / stats['count']

class MetricsCollector:
    """
    Comprehensive metrics collector for the API
    """
    
    def __init__(self, max_history_size: int = 10000):
        self.max_history_size = max_history_size
        self.lock = threading.Lock()
        
        # Initialize metrics
        self.prediction_metrics = PredictionMetrics()
        self.feature_metrics = FeatureMetrics()
        self.response_times = deque(maxlen=max_history_size)
        self.error_counts = defaultdict(int)
        self.endpoint_usage = defaultdict(int)
        
        # Initialize Prometheus metrics if available
        if PROMETHEUS_AVAILABLE:
            self._init_prometheus_metrics()
        
        # Performance tracking
        self.start_time = datetime.now(timezone.utc)
        self.last_reset = self.start_time
        
        logger.info("Metrics collector initialized")
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        try:
            # Counters
            self.prediction_requests_total = Counter(
                'prediction_requests_total',
                'Total number of prediction requests',
                ['status', 'endpoint']
            )
            
            self.prediction_processing_duration = Histogram(
                'prediction_processing_duration_seconds',
                'Prediction processing duration in seconds',
                ['endpoint'],
                buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
            )
            
            # Gauges
            self.active_connections = Gauge(
                'active_connections',
                'Number of active connections'
            )
            
            self.model_health = Gauge(
                'model_health',
                'Model health status (1=healthy, 0=unhealthy)'
            )
            
            logger.info("Prometheus metrics initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Prometheus metrics: {e}")
            PROMETHEUS_AVAILABLE = False
    
    def record_prediction(self, rainfall: float, soil_ph: float, organic_carbon: float, 
                         resilience_score: float, processing_time: float = 0.0, 
                         success: bool = True, endpoint: str = "/api/predict"):
        """Record prediction metrics"""
        with self.lock:
            # Update internal metrics
            self.prediction_metrics.update(processing_time, success)
            self.feature_metrics.update(rainfall, soil_ph, organic_carbon, "Unknown")
            self.response_times.append(processing_time)
            self.endpoint_usage[endpoint] += 1
            
            if not success:
                self.error_counts[endpoint] += 1
            
            # Update Prometheus metrics if available
            if PROMETHEUS_AVAILABLE:
                try:
                    status = "success" if success else "failure"
                    self.prediction_requests_total.labels(status=status, endpoint=endpoint).inc()
                    
                    if processing_time > 0:
                        self.prediction_processing_duration.labels(endpoint=endpoint).observe(processing_time)
                        
                except Exception as e:
                    logger.error(f"Failed to update Prometheus metrics: {e}")
    
    def record_request(self, endpoint: str, method: str, status_code: int, 
                      processing_time: float, user_agent: str = None, ip_address: str = None):
        """Record general request metrics"""
        with self.lock:
            self.endpoint_usage[f"{method} {endpoint}"] += 1
            
            if status_code >= 400:
                self.error_counts[f"{method} {endpoint}"] += 1
            
            self.response_times.append(processing_time)
    
    def record_error(self, endpoint: str, error_type: str, error_message: str):
        """Record error metrics"""
        with self.lock:
            error_key = f"{endpoint}:{error_type}"
            self.error_counts[error_key] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        with self.lock:
            current_time = datetime.now(timezone.utc)
            uptime = (current_time - self.start_time).total_seconds()
            
            # Calculate rates
            requests_per_hour = (self.prediction_metrics.total_requests / max(uptime / 3600, 1))
            error_rate = (self.prediction_metrics.failed_requests / max(self.prediction_metrics.total_requests, 1)) * 100
            
            # Response time percentiles
            sorted_times = sorted(self.response_times)
            if sorted_times:
                p50 = sorted_times[len(sorted_times) // 2]
                p95 = sorted_times[int(len(sorted_times) * 0.95)]
                p99 = sorted_times[int(len(sorted_times) * 0.99)]
            else:
                p50 = p95 = p99 = 0.0
            
            metrics = {
                "timestamp": current_time.isoformat(),
                "uptime_seconds": uptime,
                "prediction_metrics": {
                    "total_requests": self.prediction_metrics.total_requests,
                    "successful_requests": self.prediction_metrics.successful_requests,
                    "failed_requests": self.prediction_metrics.failed_requests,
                    "success_rate_percent": 100 - error_rate,
                    "error_rate_percent": error_rate,
                    "requests_per_hour": round(requests_per_hour, 2),
                    "processing_time": {
                        "average_seconds": round(self.prediction_metrics.average_processing_time, 4),
                        "min_seconds": round(self.prediction_metrics.min_processing_time, 4),
                        "max_seconds": round(self.prediction_metrics.max_processing_time, 4),
                        "p50_seconds": round(p50, 4),
                        "p95_seconds": round(p95, 4),
                        "p99_seconds": round(p99, 4)
                    }
                },
                "feature_metrics": {
                    "rainfall": self.feature_metrics.rainfall_stats,
                    "soil_ph": self.feature_metrics.soil_ph_stats,
                    "organic_carbon": self.feature_metrics.organic_carbon_stats,
                    "county_distribution": dict(self.feature_metrics.county_distribution)
                },
                "endpoint_usage": dict(self.endpoint_usage),
                "error_counts": dict(self.error_counts),
                "system_health": {
                    "status": "healthy",
                    "last_reset": self.last_reset.isoformat(),
                    "memory_usage_mb": self._get_memory_usage()
                }
            }
            
            return metrics
    
    def get_prometheus_metrics(self) -> str:
        """Get Prometheus-formatted metrics"""
        if not PROMETHEUS_AVAILABLE:
            return "# Prometheus metrics not available\n"
        
        try:
            return generate_latest().decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to generate Prometheus metrics: {e}")
            return f"# Error generating metrics: {e}\n"
    
    def reset_metrics(self):
        """Reset all metrics (useful for testing)"""
        with self.lock:
            self.prediction_metrics = PredictionMetrics()
            self.feature_metrics = FeatureMetrics()
            self.response_times.clear()
            self.error_counts.clear()
            self.endpoint_usage.clear()
            self.last_reset = datetime.now(timezone.utc)
            
            logger.info("Metrics reset successfully")
    
    def _get_memory_usage(self) -> float:
        """Get approximate memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            return round(memory_info.rss / (1024 * 1024), 2)
        except ImportError:
            return 0.0
    
    def export_metrics_to_file(self, filepath: str):
        """Export metrics to JSON file"""
        try:
            metrics = self.get_metrics()
            with open(filepath, 'w') as f:
                json.dump(metrics, f, indent=2, default=str)
            logger.info(f"Metrics exported to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for monitoring"""
        metrics = self.get_metrics()
        
        # Determine overall health
        health_status = "healthy"
        issues = []
        
        # Check error rate
        if metrics["prediction_metrics"]["error_rate_percent"] > 5:
            health_status = "degraded"
            issues.append("High error rate")
        
        # Check response time
        if metrics["prediction_metrics"]["processing_time"]["p95_seconds"] > 2.0:
            health_status = "degraded"
            issues.append("Slow response times")
        
        # Check uptime
        if metrics["uptime_seconds"] < 60:
            health_status = "starting"
            issues.append("Service recently started")
        
        return {
            "status": health_status,
            "timestamp": metrics["timestamp"],
            "uptime_seconds": metrics["uptime_seconds"],
            "issues": issues,
            "metrics_summary": {
                "total_requests": metrics["prediction_metrics"]["total_requests"],
                "success_rate": metrics["prediction_metrics"]["success_rate_percent"],
                "avg_response_time": metrics["prediction_metrics"]["processing_time"]["average_seconds"]
            }
        }

# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None

def get_metrics_collector() -> MetricsCollector:
    """Get or create global metrics collector"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector

# Performance monitoring decorator
def monitor_performance(endpoint: str = None):
    """Decorator to monitor endpoint performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                processing_time = time.time() - start_time
                endpoint_name = endpoint or func.__name__
                
                # Record metrics
                collector = get_metrics_collector()
                collector.record_request(
                    endpoint=endpoint_name,
                    method="POST" if "predict" in endpoint_name else "GET",
                    status_code=200 if success else 500,
                    processing_time=processing_time
                )
        
        return wrapper
    return decorator

# Health check function
def check_system_health() -> Dict[str, Any]:
    """Check overall system health"""
    try:
        collector = get_metrics_collector()
        health = collector.get_health_status()
        
        # Add additional health checks
        health["components"] = {
            "metrics_collector": "healthy",
            "database": "healthy",  # Add actual DB health check
            "model": "healthy"      # Add actual model health check
        }
        
        return health
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "components": {
                "metrics_collector": "unhealthy",
                "database": "unknown",
                "model": "unknown"
            }
        }

if __name__ == "__main__":
    # Test the metrics collector
    collector = MetricsCollector()
    
    # Simulate some metrics
    for i in range(10):
        collector.record_prediction(
            rainfall=800 + i * 10,
            soil_ph=6.0 + i * 0.1,
            organic_carbon=2.0 + i * 0.1,
            resilience_score=75 + i,
            processing_time=0.1 + i * 0.01
        )
    
    # Print metrics
    metrics = collector.get_metrics()
    print(json.dumps(metrics, indent=2, default=str))
