"""
Advanced health monitoring system for Building Energy Optimizer.
"""
import os
import sys
import time
import psutil
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import sqlite3
import subprocess

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import sqlalchemy
    from sqlalchemy import text
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False

logger = logging.getLogger(__name__)

@dataclass
class HealthStatus:
    """Health check status."""
    component: str
    status: str  # healthy, warning, critical, unknown
    message: str
    details: Dict[str, Any]
    last_check: datetime
    response_time_ms: Optional[float] = None

@dataclass
class SystemMetrics:
    """System performance metrics."""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    load_average: Optional[List[float]]
    process_count: int
    uptime_seconds: float
    
class HealthChecker:
    """Comprehensive health checking system."""
    
    def __init__(self):
        self.checks = {}
        self.last_full_check = None
        self.metrics_history = []
        
    def register_check(self, name: str, check_function, critical: bool = False):
        """Register a health check function."""
        self.checks[name] = {
            'function': check_function,
            'critical': critical,
            'last_result': None
        }
    
    def run_check(self, check_name: str) -> HealthStatus:
        """Run a specific health check."""
        if check_name not in self.checks:
            return HealthStatus(
                component=check_name,
                status="unknown",
                message="Check not found",
                details={},
                last_check=datetime.now()
            )
        
        check_info = self.checks[check_name]
        start_time = time.time()
        
        try:
            result = check_info['function']()
            response_time = (time.time() - start_time) * 1000
            
            if isinstance(result, HealthStatus):
                result.response_time_ms = response_time
                check_info['last_result'] = result
                return result
            else:
                # Legacy support for simple bool/dict returns
                status = "healthy" if result else "critical"
                return HealthStatus(
                    component=check_name,
                    status=status,
                    message="Check completed",
                    details=result if isinstance(result, dict) else {},
                    last_check=datetime.now(),
                    response_time_ms=response_time
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            error_status = HealthStatus(
                component=check_name,
                status="critical",
                message=f"Check failed: {str(e)}",
                details={"error": str(e), "type": type(e).__name__},
                last_check=datetime.now(),
                response_time_ms=response_time
            )
            check_info['last_result'] = error_status
            return error_status
    
    def run_all_checks(self) -> Dict[str, HealthStatus]:
        """Run all registered health checks."""
        results = {}
        
        for check_name in self.checks:
            results[check_name] = self.run_check(check_name)
        
        self.last_full_check = datetime.now()
        return results
    
    def get_overall_status(self) -> Dict[str, Any]:
        """Get overall system health status."""
        results = self.run_all_checks()
        
        # Count statuses
        status_counts = {"healthy": 0, "warning": 0, "critical": 0, "unknown": 0}
        critical_issues = []
        
        for check_name, result in results.items():
            status_counts[result.status] += 1
            
            if result.status == "critical":
                critical_issues.append({
                    'component': check_name,
                    'message': result.message,
                    'is_critical': self.checks[check_name]['critical']
                })
        
        # Determine overall status
        if status_counts["critical"] > 0:
            overall_status = "critical"
        elif status_counts["warning"] > 0:
            overall_status = "warning" 
        elif status_counts["unknown"] > 0:
            overall_status = "warning"
        else:
            overall_status = "healthy"
        
        return {
            'overall_status': overall_status,
            'status_counts': status_counts,
            'critical_issues': critical_issues,
            'total_checks': len(results),
            'last_check': self.last_full_check.isoformat() if self.last_full_check else None,
            'checks': {name: asdict(status) for name, status in results.items()}
        }
    
    def get_system_metrics(self) -> SystemMetrics:
        """Get current system performance metrics."""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        
        # Load average (Unix only)
        try:
            load_avg = os.getloadavg()
        except (AttributeError, OSError):
            load_avg = None
        
        # Process count
        process_count = len(psutil.pids())
        
        # System uptime
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        
        metrics = SystemMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_percent=disk_percent,
            load_average=list(load_avg) if load_avg else None,
            process_count=process_count,
            uptime_seconds=uptime_seconds
        )
        
        # Store in history (keep last 100 entries)
        self.metrics_history.append({
            'timestamp': datetime.now(),
            'metrics': metrics
        })
        
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-100:]
        
        return metrics

# Health check implementations
def check_database_health() -> HealthStatus:
    """Check database connectivity and performance."""
    start_time = time.time()
    
    try:
        if HAS_SQLALCHEMY:
            from ..utils.database import DatabaseManager
            from ..config.settings import get_config
            
            config = get_config()
            db_manager = DatabaseManager(config.database.url)
            
            # Test connection
            with db_manager.get_session() as session:
                result = session.execute(text("SELECT 1")).fetchone()
                if result[0] != 1:
                    raise Exception("Database query test failed")
            
            # Check table existence
            tables = ['buildings', 'energy_records', 'optimization_results']
            with db_manager.get_session() as session:
                for table in tables:
                    count_result = session.execute(text(f"SELECT COUNT(*) FROM {table}")).fetchone()
                    if count_result is None:
                        raise Exception(f"Table {table} not accessible")
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthStatus(
                component="database",
                status="healthy",
                message="Database connection and tables OK",
                details={
                    "url": config.database.url.split('@')[-1] if '@' in config.database.url else "local",
                    "tables_checked": tables,
                    "connection_pool": "active"
                },
                last_check=datetime.now(),
                response_time_ms=response_time
            )
        else:
            # Fallback for SQLite
            if os.path.exists("building_energy.db"):
                conn = sqlite3.connect("building_energy.db")
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                conn.close()
                
                response_time = (time.time() - start_time) * 1000
                
                return HealthStatus(
                    component="database",
                    status="healthy",
                    message=f"SQLite database OK with {table_count} tables",
                    details={"database_type": "sqlite", "table_count": table_count},
                    last_check=datetime.now(),
                    response_time_ms=response_time
                )
            else:
                return HealthStatus(
                    component="database",
                    status="warning",
                    message="Database file not found",
                    details={"database_type": "sqlite", "file_path": "building_energy.db"},
                    last_check=datetime.now()
                )
    
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        return HealthStatus(
            component="database",
            status="critical",
            message=f"Database check failed: {str(e)}",
            details={"error": str(e)},
            last_check=datetime.now(),
            response_time_ms=response_time
        )

def check_ml_models_health() -> HealthStatus:
    """Check ML models and dependencies."""
    start_time = time.time()
    
    try:
        # Check ML dependencies
        dependencies = ['numpy', 'pandas', 'scikit-learn']
        missing_deps = []
        
        for dep in dependencies:
            try:
                __import__(dep)
            except ImportError:
                missing_deps.append(dep)
        
        if missing_deps:
            return HealthStatus(
                component="ml_models",
                status="critical",
                message=f"Missing ML dependencies: {missing_deps}",
                details={"missing_dependencies": missing_deps},
                last_check=datetime.now()
            )
        
        # Check for trained models
        model_files = list(Path(".").glob("*.joblib"))
        
        # Test model loading capability
        from ..optimizer import BuildingEnergyOptimizer
        optimizer = BuildingEnergyOptimizer()
        
        response_time = (time.time() - start_time) * 1000
        
        return HealthStatus(
            component="ml_models",
            status="healthy",
            message="ML system operational",
            details={
                "available_algorithms": ["xgboost", "lightgbm", "random_forest"],
                "trained_models": len(model_files),
                "model_files": [f.name for f in model_files]
            },
            last_check=datetime.now(),
            response_time_ms=response_time
        )
        
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        return HealthStatus(
            component="ml_models",
            status="critical",
            message=f"ML system check failed: {str(e)}",
            details={"error": str(e)},
            last_check=datetime.now(),
            response_time_ms=response_time
        )

def check_weather_service_health() -> HealthStatus:
    """Check weather service connectivity."""
    start_time = time.time()
    
    try:
        from ..utils.weather import OpenWeatherMapProvider
        
        provider = OpenWeatherMapProvider()
        
        # Test weather data retrieval (will use synthetic if no API key)
        weather = provider.get_current_weather(41.9028, 12.4964)  # Rome
        
        response_time = (time.time() - start_time) * 1000
        
        has_api_key = provider.api_key is not None
        
        return HealthStatus(
            component="weather_service",
            status="healthy" if has_api_key else "warning",
            message="Weather service operational" if has_api_key else "Using synthetic weather data",
            details={
                "api_key_configured": has_api_key,
                "data_source": "OpenWeatherMap" if has_api_key else "Synthetic",
                "last_temperature": weather.temperature,
                "last_humidity": weather.humidity
            },
            last_check=datetime.now(),
            response_time_ms=response_time
        )
        
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        return HealthStatus(
            component="weather_service",
            status="warning",
            message=f"Weather service check failed: {str(e)}",
            details={"error": str(e)},
            last_check=datetime.now(),
            response_time_ms=response_time
        )

def check_api_health() -> HealthStatus:
    """Check API server health."""
    start_time = time.time()
    
    try:
        if HAS_REQUESTS:
            # Test API endpoint
            try:
                response = requests.get("http://localhost:8000/", timeout=5)
                if response.status_code == 200:
                    response_time = (time.time() - start_time) * 1000
                    
                    return HealthStatus(
                        component="api_server",
                        status="healthy",
                        message="API server responding",
                        details={
                            "status_code": response.status_code,
                            "endpoint": "http://localhost:8000/",
                            "server_info": response.json() if response.headers.get('content-type', '').startswith('application/json') else None
                        },
                        last_check=datetime.now(),
                        response_time_ms=response_time
                    )
                else:
                    return HealthStatus(
                        component="api_server",
                        status="warning",
                        message=f"API server returned status {response.status_code}",
                        details={"status_code": response.status_code},
                        last_check=datetime.now()
                    )
            
            except requests.ConnectionError:
                return HealthStatus(
                    component="api_server",
                    status="warning",
                    message="API server not running",
                    details={"endpoint": "http://localhost:8000/", "error": "Connection refused"},
                    last_check=datetime.now()
                )
        else:
            return HealthStatus(
                component="api_server",
                status="unknown",
                message="Cannot check API - requests library not available",
                details={},
                last_check=datetime.now()
            )
    
    except Exception as e:
        return HealthStatus(
            component="api_server",
            status="critical",
            message=f"API health check failed: {str(e)}",
            details={"error": str(e)},
            last_check=datetime.now()
        )

def check_file_system_health() -> HealthStatus:
    """Check file system and directory permissions."""
    start_time = time.time()
    
    try:
        required_dirs = ['logs', 'models', 'data']
        missing_dirs = []
        permission_errors = []
        
        for dir_name in required_dirs:
            dir_path = Path(dir_name)
            
            if not dir_path.exists():
                missing_dirs.append(dir_name)
                continue
            
            # Test write permissions
            test_file = dir_path / f"health_check_{int(time.time())}.tmp"
            try:
                test_file.write_text("health check")
                test_file.unlink()  # Delete test file
            except PermissionError:
                permission_errors.append(dir_name)
        
        # Check disk space
        disk_usage = psutil.disk_usage('.')
        free_gb = disk_usage.free / (1024**3)
        
        response_time = (time.time() - start_time) * 1000
        
        if missing_dirs or permission_errors:
            status = "warning"
            message = f"File system issues detected"
        elif free_gb < 1:  # Less than 1GB free
            status = "warning"
            message = "Low disk space"
        else:
            status = "healthy"
            message = "File system OK"
        
        return HealthStatus(
            component="file_system",
            status=status,
            message=message,
            details={
                "missing_directories": missing_dirs,
                "permission_errors": permission_errors,
                "free_space_gb": round(free_gb, 2),
                "total_space_gb": round(disk_usage.total / (1024**3), 2)
            },
            last_check=datetime.now(),
            response_time_ms=response_time
        )
        
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        return HealthStatus(
            component="file_system",
            status="critical",
            message=f"File system check failed: {str(e)}",
            details={"error": str(e)},
            last_check=datetime.now(),
            response_time_ms=response_time
        )

def check_plugin_health() -> HealthStatus:
    """Check plugin system health."""
    start_time = time.time()
    
    try:
        from ..plugins import get_plugin_manager
        
        manager = get_plugin_manager()
        status_summary = manager.get_status_summary()
        
        response_time = (time.time() - start_time) * 1000
        
        total_plugins = status_summary['total_plugins']
        loaded_plugins = status_summary['loaded_plugins']
        
        if total_plugins == 0:
            status = "warning"
            message = "No plugins discovered"
        elif loaded_plugins == 0:
            status = "warning"
            message = "No plugins loaded"
        elif loaded_plugins < total_plugins:
            status = "warning"
            message = f"Only {loaded_plugins}/{total_plugins} plugins loaded"
        else:
            status = "healthy"
            message = f"All {total_plugins} plugins loaded successfully"
        
        return HealthStatus(
            component="plugin_system",
            status=status,
            message=message,
            details=status_summary,
            last_check=datetime.now(),
            response_time_ms=response_time
        )
        
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        return HealthStatus(
            component="plugin_system",
            status="critical",
            message=f"Plugin system check failed: {str(e)}",
            details={"error": str(e)},
            last_check=datetime.now(),
            response_time_ms=response_time
        )

def check_dependencies_health() -> HealthStatus:
    """Check critical dependencies."""
    start_time = time.time()
    
    try:
        critical_deps = {
            'numpy': 'Required for numerical computations',
            'pandas': 'Required for data processing',
            'scikit-learn': 'Required for ML algorithms'
        }
        
        optional_deps = {
            'xgboost': 'XGBoost algorithm support',
            'lightgbm': 'LightGBM algorithm support',
            'fastapi': 'REST API support',
            'streamlit': 'Dashboard support'
        }
        
        missing_critical = []
        missing_optional = []
        versions = {}
        
        # Check critical dependencies
        for dep, description in critical_deps.items():
            try:
                module = __import__(dep.replace('-', '_'))
                if hasattr(module, '__version__'):
                    versions[dep] = module.__version__
                else:
                    versions[dep] = 'unknown'
            except ImportError:
                missing_critical.append(dep)
        
        # Check optional dependencies
        for dep, description in optional_deps.items():
            try:
                module = __import__(dep.replace('-', '_'))
                if hasattr(module, '__version__'):
                    versions[dep] = module.__version__
                else:
                    versions[dep] = 'unknown'
            except ImportError:
                missing_optional.append(dep)
        
        response_time = (time.time() - start_time) * 1000
        
        if missing_critical:
            status = "critical"
            message = f"Missing critical dependencies: {missing_critical}"
        elif len(missing_optional) > len(optional_deps) / 2:
            status = "warning"
            message = f"Many optional dependencies missing: {missing_optional}"
        else:
            status = "healthy"
            message = "All critical dependencies available"
        
        return HealthStatus(
            component="dependencies",
            status=status,
            message=message,
            details={
                "missing_critical": missing_critical,
                "missing_optional": missing_optional,
                "versions": versions,
                "python_version": sys.version
            },
            last_check=datetime.now(),
            response_time_ms=response_time
        )
        
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        return HealthStatus(
            component="dependencies",
            status="critical",
            message=f"Dependency check failed: {str(e)}",
            details={"error": str(e)},
            last_check=datetime.now(),
            response_time_ms=response_time
        )

class SystemMonitor:
    """Continuous system monitoring."""
    
    def __init__(self):
        self.health_checker = HealthChecker()
        self.monitoring_enabled = False
        self.alert_thresholds = {
            'cpu_percent': 80,
            'memory_percent': 85,
            'disk_percent': 90,
            'response_time_ms': 5000
        }
        
        # Register health checks
        self._register_default_checks()
    
    def _register_default_checks(self):
        """Register default health checks."""
        self.health_checker.register_check("database", check_database_health, critical=True)
        self.health_checker.register_check("ml_models", check_ml_models_health, critical=True)
        self.health_checker.register_check("weather_service", check_weather_service_health, critical=False)
        self.health_checker.register_check("api_server", check_api_health, critical=False)
        self.health_checker.register_check("file_system", check_file_system_health, critical=True)
        self.health_checker.register_check("plugin_system", check_plugin_health, critical=False)
        self.health_checker.register_check("dependencies", check_dependencies_health, critical=True)
    
    def start_monitoring(self, interval_seconds: int = 60):
        """Start continuous monitoring."""
        self.monitoring_enabled = True
        logger.info("System monitoring started")
        
        # This would run in a separate thread in production
        # For demo, just return the current status
        return self.get_current_status()
    
    def stop_monitoring(self):
        """Stop continuous monitoring."""
        self.monitoring_enabled = False
        logger.info("System monitoring stopped")
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current system status."""
        # Health checks
        health_status = self.health_checker.get_overall_status()
        
        # System metrics
        metrics = self.health_checker.get_system_metrics()
        
        # Check for alerts
        alerts = self._check_alerts(metrics, health_status)
        
        return {
            'system_health': health_status,
            'system_metrics': asdict(metrics),
            'alerts': alerts,
            'monitoring_enabled': self.monitoring_enabled,
            'timestamp': datetime.now().isoformat()
        }
    
    def _check_alerts(self, metrics: SystemMetrics, health_status: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for system alerts."""
        alerts = []
        
        # CPU alert
        if metrics.cpu_percent > self.alert_thresholds['cpu_percent']:
            alerts.append({
                'type': 'high_cpu',
                'level': 'warning',
                'message': f'High CPU usage: {metrics.cpu_percent:.1f}%',
                'threshold': self.alert_thresholds['cpu_percent'],
                'current_value': metrics.cpu_percent
            })
        
        # Memory alert
        if metrics.memory_percent > self.alert_thresholds['memory_percent']:
            alerts.append({
                'type': 'high_memory',
                'level': 'warning',
                'message': f'High memory usage: {metrics.memory_percent:.1f}%',
                'threshold': self.alert_thresholds['memory_percent'],
                'current_value': metrics.memory_percent
            })
        
        # Disk space alert
        if metrics.disk_percent > self.alert_thresholds['disk_percent']:
            alerts.append({
                'type': 'low_disk_space',
                'level': 'critical',
                'message': f'Low disk space: {metrics.disk_percent:.1f}% used',
                'threshold': self.alert_thresholds['disk_percent'],
                'current_value': metrics.disk_percent
            })
        
        # Critical component failures
        for check_name, check_result in health_status['checks'].items():
            if check_result['status'] == 'critical':
                alerts.append({
                    'type': 'component_failure',
                    'level': 'critical',
                    'message': f'Component {check_name} is critical: {check_result["message"]}',
                    'component': check_name,
                    'details': check_result['details']
                })
        
        return alerts
    
    def get_health_report(self) -> str:
        """Generate human-readable health report."""
        status = self.get_current_status()
        
        report = []
        report.append("🏥 BUILDING ENERGY OPTIMIZER HEALTH REPORT")
        report.append("=" * 55)
        report.append(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"🎯 Overall Status: {status['system_health']['overall_status'].upper()}")
        report.append("")
        
        # System metrics
        metrics = status['system_metrics']
        report.append("📊 SYSTEM METRICS")
        report.append("-" * 20)
        report.append(f"🖥️  CPU Usage: {metrics['cpu_percent']:.1f}%")
        report.append(f"💾 Memory Usage: {metrics['memory_percent']:.1f}%")
        report.append(f"💿 Disk Usage: {metrics['disk_percent']:.1f}%")
        report.append(f"⏰ Uptime: {metrics['uptime_seconds'] / 3600:.1f} hours")
        report.append(f"🔢 Processes: {metrics['process_count']}")
        report.append("")
        
        # Component health
        report.append("🔍 COMPONENT HEALTH")
        report.append("-" * 20)
        for check_name, check_result in status['system_health']['checks'].items():
            status_emoji = {
                'healthy': '✅',
                'warning': '⚠️',
                'critical': '❌',
                'unknown': '❓'
            }
            
            emoji = status_emoji.get(check_result['status'], '❓')
            response_time = check_result.get('response_time_ms', 0)
            
            report.append(f"{emoji} {check_name}: {check_result['message']} ({response_time:.1f}ms)")
        
        # Alerts
        if status['alerts']:
            report.append("")
            report.append("🚨 ACTIVE ALERTS")
            report.append("-" * 15)
            for alert in status['alerts']:
                level_emoji = {'warning': '⚠️', 'critical': '🚨'}
                emoji = level_emoji.get(alert['level'], '❓')
                report.append(f"{emoji} {alert['message']}")
        
        report.append("")
        report.append("✅ Health check complete")
        
        return "\n".join(report)

# Global monitor instance
system_monitor = SystemMonitor()

def get_system_monitor() -> SystemMonitor:
    """Get global system monitor instance."""
    return system_monitor

def quick_health_check() -> bool:
    """Quick health check returning simple boolean."""
    status = system_monitor.get_current_status()
    return status['system_health']['overall_status'] in ['healthy', 'warning']

def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check returning full status."""
    return system_monitor.get_current_status()

if __name__ == "__main__":
    # Run health check
    print("🏥 Running health check...")
    
    monitor = SystemMonitor()
    report = monitor.get_health_report()
    
    print(report)
    
    # Show JSON status for debugging
    status = monitor.get_current_status()
    print("\n🔍 Detailed JSON status:")
    import json
    print(json.dumps(status, indent=2, default=str))
