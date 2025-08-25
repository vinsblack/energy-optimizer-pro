"""
Advanced metrics collection and monitoring system.
"""
import time
import json
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
import sqlite3
from pathlib import Path

try:
    import prometheus_client
    from prometheus_client import Counter, Histogram, Gauge, start_http_server
    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False

logger = logging.getLogger(__name__)

@dataclass
class MetricPoint:
    """Single metric data point."""
    timestamp: datetime
    name: str
    value: float
    labels: Dict[str, str]
    unit: str = ""

class MetricsCollector:
    """Comprehensive metrics collection system."""
    
    def __init__(self, enable_prometheus: bool = True):
        self.metrics_data = defaultdict(lambda: deque(maxlen=1000))
        self.prometheus_enabled = enable_prometheus and HAS_PROMETHEUS
        
        # Performance metrics
        self.counters = {}
        self.histograms = {}
        self.gauges = {}
        
        # Custom metrics
        self.custom_metrics = {}
        
        # Monitoring
        self.monitoring_active = False
        self.collection_interval = 30  # seconds
        
        self._initialize_prometheus()
        self._initialize_core_metrics()
    
    def _initialize_prometheus(self):
        """Initialize Prometheus metrics if available."""
        if not self.prometheus_enabled:
            return
        
        try:
            # Business metrics
            self.counters['optimizations_total'] = Counter(
                'building_energy_optimizations_total',
                'Total number of energy optimizations performed',
                ['algorithm', 'building_type', 'status']
            )
            
            self.counters['predictions_total'] = Counter(
                'building_energy_predictions_total', 
                'Total number of energy predictions',
                ['algorithm', 'building_type']
            )
            
            self.counters['api_requests_total'] = Counter(
                'api_requests_total',
                'Total API requests',
                ['method', 'endpoint', 'status_code']
            )
            
            # Performance metrics
            self.histograms['optimization_duration'] = Histogram(
                'building_energy_optimization_duration_seconds',
                'Time spent on energy optimization',
                ['algorithm', 'building_type']
            )
            
            self.histograms['prediction_duration'] = Histogram(
                'building_energy_prediction_duration_seconds',
                'Time spent on energy prediction',
                ['algorithm']
            )
            
            self.histograms['api_request_duration'] = Histogram(
                'api_request_duration_seconds',
                'Time spent on API requests',
                ['method', 'endpoint']
            )
            
            # System metrics
            self.gauges['active_optimizations'] = Gauge(
                'building_energy_active_optimizations',
                'Number of currently running optimizations'
            )
            
            self.gauges['model_accuracy'] = Gauge(
                'building_energy_model_accuracy',
                'Current model accuracy (R² score)',
                ['algorithm', 'building_type']
            )
            
            self.gauges['energy_savings_percent'] = Gauge(
                'building_energy_savings_percent',
                'Average energy savings percentage',
                ['building_type']
            )
            
            logger.info("Prometheus metrics initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Prometheus metrics: {e}")
            self.prometheus_enabled = False
    
    def _initialize_core_metrics(self):
        """Initialize core metrics tracking."""
        self.custom_metrics = {
            'optimizations_count': 0,
            'predictions_count': 0,
            'total_energy_analyzed_kwh': 0.0,
            'total_savings_identified_kwh': 0.0,
            'average_model_accuracy': 0.0,
            'buildings_analyzed': set(),
            'algorithms_used': defaultdict(int),
            'errors_count': defaultdict(int)
        }
    
    def record_optimization(self, algorithm: str, building_type: str, 
                          duration_seconds: float, accuracy: float,
                          energy_analyzed_kwh: float, savings_kwh: float,
                          success: bool = True):
        """Record optimization metrics."""
        # Prometheus metrics
        if self.prometheus_enabled:
            status = 'success' if success else 'error'
            self.counters['optimizations_total'].labels(
                algorithm=algorithm, 
                building_type=building_type, 
                status=status
            ).inc()
            
            self.histograms['optimization_duration'].labels(
                algorithm=algorithm,
                building_type=building_type
            ).observe(duration_seconds)
            
            self.gauges['model_accuracy'].labels(
                algorithm=algorithm,
                building_type=building_type
            ).set(accuracy)
        
        # Custom metrics
        self.custom_metrics['optimizations_count'] += 1
        self.custom_metrics['total_energy_analyzed_kwh'] += energy_analyzed_kwh
        self.custom_metrics['total_savings_identified_kwh'] += savings_kwh
        self.custom_metrics['algorithms_used'][algorithm] += 1
        
        # Update average accuracy
        total_count = self.custom_metrics['optimizations_count']
        current_avg = self.custom_metrics['average_model_accuracy']
        self.custom_metrics['average_model_accuracy'] = (
            (current_avg * (total_count - 1) + accuracy) / total_count
        )
        
        # Store detailed metric
        metric = MetricPoint(
            timestamp=datetime.now(),
            name="optimization_completed",
            value=duration_seconds,
            labels={
                'algorithm': algorithm,
                'building_type': building_type,
                'status': 'success' if success else 'error'
            },
            unit="seconds"
        )
        
        self.metrics_data['optimizations'].append(metric)
        logger.info(f"Recorded optimization: {algorithm} for {building_type} in {duration_seconds:.2f}s")
    
    def record_prediction(self, algorithm: str, duration_seconds: float, building_type: str = "unknown"):
        """Record prediction metrics."""
        if self.prometheus_enabled:
            self.counters['predictions_total'].labels(
                algorithm=algorithm,
                building_type=building_type
            ).inc()
            
            self.histograms['prediction_duration'].labels(
                algorithm=algorithm
            ).observe(duration_seconds)
        
        self.custom_metrics['predictions_count'] += 1
        
        metric = MetricPoint(
            timestamp=datetime.now(),
            name="prediction_completed",
            value=duration_seconds,
            labels={'algorithm': algorithm, 'building_type': building_type},
            unit="seconds"
        )
        
        self.metrics_data['predictions'].append(metric)
    
    def record_api_request(self, method: str, endpoint: str, status_code: int, duration_seconds: float):
        """Record API request metrics."""
        if self.prometheus_enabled:
            self.counters['api_requests_total'].labels(
                method=method,
                endpoint=endpoint,
                status_code=str(status_code)
            ).inc()
            
            self.histograms['api_request_duration'].labels(
                method=method,
                endpoint=endpoint
            ).observe(duration_seconds)
        
        metric = MetricPoint(
            timestamp=datetime.now(),
            name="api_request",
            value=duration_seconds,
            labels={
                'method': method,
                'endpoint': endpoint,
                'status_code': str(status_code)
            },
            unit="seconds"
        )
        
        self.metrics_data['api_requests'].append(metric)
    
    def record_error(self, error_type: str, component: str, message: str):
        """Record error occurrence."""
        self.custom_metrics['errors_count'][error_type] += 1
        
        metric = MetricPoint(
            timestamp=datetime.now(),
            name="error_occurred",
            value=1,
            labels={
                'error_type': error_type,
                'component': component,
                'message': message[:100]  # Truncate long messages
            },
            unit="count"
        )
        
        self.metrics_data['errors'].append(metric)
        logger.error(f"Recorded error: {error_type} in {component}: {message}")
    
    def get_summary_metrics(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        # Calculate time windows
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(days=1)
        
        summary = {
            'collection_info': {
                'total_metric_points': sum(len(deque_data) for deque_data in self.metrics_data.values()),
                'metric_categories': list(self.metrics_data.keys()),
                'collection_active': self.monitoring_active,
                'last_update': now.isoformat()
            },
            'business_metrics': {
                'total_optimizations': self.custom_metrics['optimizations_count'],
                'total_predictions': self.custom_metrics['predictions_count'],
                'total_energy_analyzed_kwh': round(self.custom_metrics['total_energy_analyzed_kwh'], 2),
                'total_savings_identified_kwh': round(self.custom_metrics['total_savings_identified_kwh'], 2),
                'average_model_accuracy': round(self.custom_metrics['average_model_accuracy'], 3),
                'unique_buildings_analyzed': len(self.custom_metrics['buildings_analyzed']),
                'algorithms_usage': dict(self.custom_metrics['algorithms_used'])
            },
            'performance_metrics': {
                'avg_optimization_time_last_hour': self._calculate_avg_duration('optimizations', hour_ago),
                'avg_prediction_time_last_hour': self._calculate_avg_duration('predictions', hour_ago),
                'api_requests_last_hour': self._count_metrics('api_requests', hour_ago),
                'errors_last_24h': self._count_metrics('errors', day_ago)
            },
            'system_health': {
                'error_rate_24h': self._calculate_error_rate(day_ago),
                'uptime_hours': (now - self._get_system_start_time()).total_seconds() / 3600,
                'prometheus_enabled': self.prometheus_enabled
            }
        }
        
        return summary
    
    def _calculate_avg_duration(self, metric_category: str, since: datetime) -> float:
        """Calculate average duration for metrics since timestamp."""
        if metric_category not in self.metrics_data:
            return 0.0
        
        recent_metrics = [
            m for m in self.metrics_data[metric_category] 
            if m.timestamp >= since
        ]
        
        if not recent_metrics:
            return 0.0
        
        return sum(m.value for m in recent_metrics) / len(recent_metrics)
    
    def _count_metrics(self, metric_category: str, since: datetime) -> int:
        """Count metrics since timestamp."""
        if metric_category not in self.metrics_data:
            return 0
        
        return len([
            m for m in self.metrics_data[metric_category]
            if m.timestamp >= since
        ])
    
    def _calculate_error_rate(self, since: datetime) -> float:
        """Calculate error rate since timestamp."""
        total_requests = self._count_metrics('api_requests', since)
        error_requests = len([
            m for m in self.metrics_data.get('api_requests', [])
            if m.timestamp >= since and 
               int(m.labels.get('status_code', '200')) >= 400
        ])
        
        if total_requests == 0:
            return 0.0
        
        return (error_requests / total_requests) * 100
    
    def _get_system_start_time(self) -> datetime:
        """Get approximate system start time."""
        if self.metrics_data:
            oldest_metric = min(
                (min(deque_data, key=lambda m: m.timestamp) for deque_data in self.metrics_data.values() if deque_data),
                key=lambda m: m.timestamp,
                default=None
            )
            if oldest_metric:
                return oldest_metric.timestamp
        
        return datetime.now()  # Fallback
    
    def export_metrics(self, format: str = 'json', time_window_hours: int = 24) -> str:
        """Export metrics in specified format."""
        since = datetime.now() - timedelta(hours=time_window_hours)
        
        exported_data = {
            'export_info': {
                'format': format,
                'time_window_hours': time_window_hours,
                'exported_at': datetime.now().isoformat(),
                'total_metrics': 0
            },
            'metrics': {}
        }
        
        # Export metrics by category
        for category, metrics_deque in self.metrics_data.items():
            category_metrics = [
                asdict(m) for m in metrics_deque 
                if m.timestamp >= since
            ]
            
            # Convert datetime to string for JSON serialization
            for metric in category_metrics:
                metric['timestamp'] = metric['timestamp'].isoformat()
            
            exported_data['metrics'][category] = category_metrics
            exported_data['export_info']['total_metrics'] += len(category_metrics)
        
        # Add summary
        exported_data['summary'] = self.get_summary_metrics()
        
        if format == 'json':
            return json.dumps(exported_data, indent=2)
        elif format == 'csv':
            # Convert to CSV format
            import pandas as pd
            all_metrics = []
            
            for category, metrics in exported_data['metrics'].items():
                for metric in metrics:
                    flat_metric = {
                        'category': category,
                        'timestamp': metric['timestamp'],
                        'name': metric['name'],
                        'value': metric['value'],
                        'unit': metric['unit']
                    }
                    # Flatten labels
                    for key, value in metric['labels'].items():
                        flat_metric[f'label_{key}'] = value
                    
                    all_metrics.append(flat_metric)
            
            if all_metrics:
                df = pd.DataFrame(all_metrics)
                return df.to_csv(index=False)
            else:
                return "No metrics found for the specified time window"
        
        return str(exported_data)
    
    def start_prometheus_server(self, port: int = 8090):
        """Start Prometheus metrics server."""
        if not self.prometheus_enabled:
            logger.warning("Prometheus not available - metrics server not started")
            return False
        
        try:
            start_http_server(port)
            logger.info(f"Prometheus metrics server started on port {port}")
            return True
        except Exception as e:
            logger.error(f"Failed to start Prometheus server: {e}")
            return False
    
    def start_monitoring(self):
        """Start automatic metrics collection."""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return
        
        self.monitoring_active = True
        
        def monitoring_loop():
            """Background monitoring loop."""
            while self.monitoring_active:
                try:
                    self._collect_system_metrics()
                    time.sleep(self.collection_interval)
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    time.sleep(self.collection_interval)
        
        monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitoring_thread.start()
        
        logger.info("Metrics monitoring started")
    
    def stop_monitoring(self):
        """Stop automatic metrics collection."""
        self.monitoring_active = False
        logger.info("Metrics monitoring stopped")
    
    def _collect_system_metrics(self):
        """Collect system performance metrics."""
        try:
            import psutil
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent()
            self.metrics_data['system'].append(MetricPoint(
                timestamp=datetime.now(),
                name="cpu_usage_percent",
                value=cpu_percent,
                labels={'component': 'system'},
                unit="percent"
            ))
            
            # Memory metrics
            memory = psutil.virtual_memory()
            self.metrics_data['system'].append(MetricPoint(
                timestamp=datetime.now(),
                name="memory_usage_percent",
                value=memory.percent,
                labels={'component': 'system'},
                unit="percent"
            ))
            
            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            self.metrics_data['system'].append(MetricPoint(
                timestamp=datetime.now(),
                name="process_memory_mb",
                value=process_memory,
                labels={'component': 'building_energy_optimizer'},
                unit="MB"
            ))
            
            # Update Prometheus gauges if available
            if self.prometheus_enabled:
                # Create gauges for system metrics if they don't exist
                if 'system_cpu_percent' not in self.gauges:
                    self.gauges['system_cpu_percent'] = Gauge(
                        'system_cpu_usage_percent',
                        'System CPU usage percentage'
                    )
                
                if 'system_memory_percent' not in self.gauges:
                    self.gauges['system_memory_percent'] = Gauge(
                        'system_memory_usage_percent',
                        'System memory usage percentage'
                    )
                
                self.gauges['system_cpu_percent'].set(cpu_percent)
                self.gauges['system_memory_percent'].set(memory.percent)
        
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")

class MetricsAnalyzer:
    """Analysis tools for collected metrics."""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
    
    def analyze_performance_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze performance trends over time."""
        since = datetime.now() - timedelta(hours=hours)
        
        analysis = {
            'time_window_hours': hours,
            'analysis_timestamp': datetime.now().isoformat(),
            'trends': {}
        }
        
        # Analyze optimization duration trends
        opt_durations = [
            m.value for m in self.collector.metrics_data.get('optimizations', [])
            if m.timestamp >= since and m.name == 'optimization_completed'
        ]
        
        if opt_durations:
            analysis['trends']['optimization_duration'] = {
                'average_seconds': sum(opt_durations) / len(opt_durations),
                'min_seconds': min(opt_durations),
                'max_seconds': max(opt_durations),
                'total_optimizations': len(opt_durations),
                'trend': self._calculate_trend(opt_durations)
            }
        
        # Analyze CPU usage trends
        cpu_metrics = [
            m.value for m in self.collector.metrics_data.get('system', [])
            if m.timestamp >= since and m.name == 'cpu_usage_percent'
        ]
        
        if cpu_metrics:
            analysis['trends']['cpu_usage'] = {
                'average_percent': sum(cpu_metrics) / len(cpu_metrics),
                'peak_percent': max(cpu_metrics),
                'samples': len(cpu_metrics),
                'trend': self._calculate_trend(cpu_metrics)
            }
        
        # Analyze memory usage trends
        memory_metrics = [
            m.value for m in self.collector.metrics_data.get('system', [])
            if m.timestamp >= since and m.name == 'memory_usage_percent'
        ]
        
        if memory_metrics:
            analysis['trends']['memory_usage'] = {
                'average_percent': sum(memory_metrics) / len(memory_metrics),
                'peak_percent': max(memory_metrics),
                'samples': len(memory_metrics),
                'trend': self._calculate_trend(memory_metrics)
            }
        
        return analysis
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction."""
        if len(values) < 2:
            return "insufficient_data"
        
        # Simple trend calculation - compare first and second half
        mid_point = len(values) // 2
        first_half_avg = sum(values[:mid_point]) / mid_point
        second_half_avg = sum(values[mid_point:]) / (len(values) - mid_point)
        
        diff_percent = ((second_half_avg - first_half_avg) / first_half_avg) * 100
        
        if abs(diff_percent) < 5:
            return "stable"
        elif diff_percent > 0:
            return "increasing"
        else:
            return "decreasing"
    
    def generate_performance_report(self) -> str:
        """Generate human-readable performance report."""
        summary = self.collector.get_summary_metrics()
        trends = self.analyze_performance_trends(24)
        
        report = []
        report.append("📊 BUILDING ENERGY OPTIMIZER PERFORMANCE REPORT")
        report.append("=" * 55)
        report.append(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Business metrics
        business = summary['business_metrics']
        report.append("🏢 BUSINESS METRICS")
        report.append("-" * 20)
        report.append(f"🤖 Total Optimizations: {business['total_optimizations']:,}")
        report.append(f"🔮 Total Predictions: {business['total_predictions']:,}")
        report.append(f"⚡ Energy Analyzed: {business['total_energy_analyzed_kwh']:,.0f} kWh")
        report.append(f"💰 Savings Identified: {business['total_savings_identified_kwh']:,.0f} kWh")
        report.append(f"🎯 Average Model Accuracy: {business['average_model_accuracy']:.1%}")
        report.append(f"🏘️ Buildings Analyzed: {business['unique_buildings_analyzed']}")
        report.append("")
        
        # Performance metrics
        performance = summary['performance_metrics']
        report.append("⚡ PERFORMANCE METRICS (Last 24h)")
        report.append("-" * 35)
        report.append(f"⏱️ Avg Optimization Time: {performance['avg_optimization_time_last_hour']:.2f}s")
        report.append(f"⚡ Avg Prediction Time: {performance['avg_prediction_time_last_hour']:.2f}s")
        report.append(f"📡 API Requests: {performance['api_requests_last_hour']:,}")
        report.append(f"❌ Errors: {performance['errors_last_24h']}")
        report.append("")
        
        # System health
        health = summary['system_health']
        report.append("🏥 SYSTEM HEALTH")
        report.append("-" * 15)
        report.append(f"📈 Error Rate: {health['error_rate_24h']:.2f}%")
        report.append(f"⏰ Uptime: {health['uptime_hours']:.1f} hours")
        report.append(f"📊 Monitoring: {'Active' if self.collector.monitoring_active else 'Inactive'}")
        report.append("")
        
        # Trends
        if trends['trends']:
            report.append("📈 PERFORMANCE TRENDS (Last 24h)")
            report.append("-" * 35)
            
            for metric_name, trend_data in trends['trends'].items():
                trend_emoji = {"increasing": "📈", "decreasing": "📉", "stable": "➡️"}.get(trend_data['trend'], "❓")
                report.append(f"{trend_emoji} {metric_name.replace('_', ' ').title()}: {trend_data['trend']}")
        
        report.append("")
        report.append("✅ Performance report complete")
        
        return "\n".join(report)
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get performance alerts based on thresholds."""
        alerts = []
        summary = self.collector.get_summary_metrics()
        
        # High error rate alert
        error_rate = summary['system_health']['error_rate_24h']
        if error_rate > 5:  # 5% error rate threshold
            alerts.append({
                'type': 'high_error_rate',
                'level': 'critical' if error_rate > 10 else 'warning',
                'message': f'High error rate detected: {error_rate:.1f}%',
                'threshold': 5,
                'current_value': error_rate
            })
        
        # Slow optimization alert
        avg_opt_time = summary['performance_metrics']['avg_optimization_time_last_hour']
        if avg_opt_time > 120:  # 2 minutes threshold
            alerts.append({
                'type': 'slow_optimization',
                'level': 'warning',
                'message': f'Slow optimization times: {avg_opt_time:.1f}s average',
                'threshold': 120,
                'current_value': avg_opt_time
            })
        
        # Low accuracy alert
        avg_accuracy = summary['business_metrics']['average_model_accuracy']
        if avg_accuracy < 0.7:  # 70% accuracy threshold
            alerts.append({
                'type': 'low_model_accuracy',
                'level': 'warning',
                'message': f'Low model accuracy: {avg_accuracy:.1%}',
                'threshold': 0.7,
                'current_value': avg_accuracy
            })
        
        return alerts

# Global metrics collector
metrics_collector = MetricsCollector()
metrics_analyzer = MetricsAnalyzer(metrics_collector)

def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector instance."""
    return metrics_collector

def get_metrics_analyzer() -> MetricsAnalyzer:
    """Get global metrics analyzer instance."""
    return metrics_analyzer

# Convenience functions
def record_optimization_metrics(algorithm: str, building_type: str, duration: float, 
                              accuracy: float, energy_kwh: float, savings_kwh: float, success: bool = True):
    """Record optimization metrics (convenience function)."""
    metrics_collector.record_optimization(algorithm, building_type, duration, accuracy, energy_kwh, savings_kwh, success)

def record_prediction_metrics(algorithm: str, duration: float, building_type: str = "unknown"):
    """Record prediction metrics (convenience function)."""
    metrics_collector.record_prediction(algorithm, duration, building_type)

def record_api_metrics(method: str, endpoint: str, status_code: int, duration: float):
    """Record API metrics (convenience function)."""
    metrics_collector.record_api_request(method, endpoint, status_code, duration)

def get_performance_summary() -> Dict[str, Any]:
    """Get performance summary (convenience function)."""
    return metrics_collector.get_summary_metrics()

def generate_performance_report() -> str:
    """Generate performance report (convenience function)."""
    return metrics_analyzer.generate_performance_report()

if __name__ == "__main__":
    # Test metrics system
    print("📊 Testing metrics system...")
    
    # Start monitoring
    metrics_collector.start_monitoring()
    
    # Simulate some metrics
    for i in range(5):
        metrics_collector.record_optimization(
            algorithm='xgboost',
            building_type='commercial',
            duration_seconds=45.2 + i * 5,
            accuracy=0.85 + i * 0.02,
            energy_analyzed_kwh=2500.0,
            savings_kwh=375.0,
            success=True
        )
        
        metrics_collector.record_prediction(
            algorithm='xgboost',
            duration_seconds=0.05 + i * 0.01
        )
        
        time.sleep(1)
    
    # Generate report
    print("\n📋 Performance Report:")
    print(generate_performance_report())
    
    # Show summary
    summary = get_performance_summary()
    print(f"\n🎯 Quick Summary:")
    print(f"   Optimizations: {summary['business_metrics']['total_optimizations']}")
    print(f"   Predictions: {summary['business_metrics']['total_predictions']}")
    print(f"   Average Accuracy: {summary['business_metrics']['average_model_accuracy']:.1%}")
    
    # Export metrics
    print("\n💾 Exporting metrics...")
    json_export = metrics_collector.export_metrics('json', 1)
    with open('metrics_export.json', 'w') as f:
        f.write(json_export)
    print("✅ Metrics exported to metrics_export.json")
    
    # Check alerts
    alerts = metrics_analyzer.get_alerts()
    if alerts:
        print(f"\n🚨 {len(alerts)} alert(s) detected:")
        for alert in alerts:
            print(f"   {alert['level'].upper()}: {alert['message']}")
    else:
        print("\n✅ No alerts - system performing well")
    
    metrics_collector.stop_monitoring()
    print("📊 Metrics system test complete!")
