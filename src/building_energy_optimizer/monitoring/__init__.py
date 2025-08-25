"""
Monitoring and observability system for Building Energy Optimizer.
"""
from datetime import datetime
from .health import (
    HealthChecker,
    HealthStatus,
    SystemMetrics,
    SystemMonitor,
    get_system_monitor,
    quick_health_check,
    detailed_health_check
)

from .backup import (
    BackupManager,
    backup_manager,
    create_backup,
    restore_backup,
    list_available_backups,
    cleanup_old_backups
)

from .metrics import (
    MetricsCollector,
    MetricsAnalyzer,
    MetricPoint,
    get_metrics_collector,
    get_metrics_analyzer,
    record_optimization_metrics,
    record_prediction_metrics,
    record_api_metrics,
    get_performance_summary,
    generate_performance_report
)

# Initialize monitoring system
def initialize_monitoring(config: dict = None) -> dict:
    """Initialize complete monitoring system."""
    if config is None:
        config = {}
    
    results = {
        'health_monitoring': False,
        'metrics_collection': False,
        'backup_system': False,
        'prometheus_server': False
    }
    
    try:
        # Initialize health monitoring
        monitor = get_system_monitor()
        if config.get('monitoring', {}).get('enabled', True):
            monitor.start_monitoring(
                interval_seconds=config.get('monitoring', {}).get('interval', 60)
            )
            results['health_monitoring'] = True
        
        # Initialize metrics collection
        collector = get_metrics_collector()
        if config.get('metrics', {}).get('enabled', True):
            collector.start_monitoring()
            results['metrics_collection'] = True
            
            # Start Prometheus server if configured
            prometheus_port = config.get('metrics', {}).get('prometheus_port', 8090)
            if prometheus_port and collector.prometheus_enabled:
                if collector.start_prometheus_server(prometheus_port):
                    results['prometheus_server'] = True
        
        # Configure backup system
        backup_config = config.get('backup', {})
        if backup_config.get('enabled', False):
            from .backup import backup_manager
            
            # Configure S3 if provided
            s3_config = backup_config.get('s3')
            if s3_config:
                backup_manager.configure_s3(
                    bucket_name=s3_config['bucket'],
                    aws_access_key=s3_config.get('access_key'),
                    aws_secret_key=s3_config.get('secret_key'),
                    region=s3_config.get('region', 'us-east-1')
                )
            
            # Schedule automatic backups
            if backup_config.get('automatic', False):
                backup_manager.schedule_automatic_backups(
                    backup_type=backup_config.get('type', 'full'),
                    interval_hours=backup_config.get('interval_hours', 24)
                )
            
            results['backup_system'] = True
        
        print("🔍 Monitoring system initialized successfully")
        return results
        
    except Exception as e:
        print(f"❌ Failed to initialize monitoring system: {e}")
        return results

def get_complete_system_status() -> dict:
    """Get complete system status including health, metrics, and backups."""
    status = {
        'timestamp': datetime.now().isoformat(),
        'overall_status': 'healthy'
    }
    
    try:
        # Health status
        health_status = detailed_health_check()
        status['health'] = health_status
        
        # Performance metrics
        performance_summary = get_performance_summary()
        status['performance'] = performance_summary
        
        # Backup status
        backup_list = list_available_backups()
        status['backups'] = {
            'total_backups': len(backup_list),
            'latest_backup': backup_list[0] if backup_list else None,
            'backup_sizes_mb': [
                round(backup['size_bytes'] / (1024**2), 2) 
                for backup in backup_list[:5]  # Last 5 backups
            ]
        }
        
        # Determine overall status
        if health_status['overall_status'] == 'critical':
            status['overall_status'] = 'critical'
        elif health_status['overall_status'] == 'warning':
            status['overall_status'] = 'warning'
        elif performance_summary['system_health']['error_rate_24h'] > 10:
            status['overall_status'] = 'warning'
        
    except Exception as e:
        status['error'] = str(e)
        status['overall_status'] = 'unknown'
    
    return status

__all__ = [
    # Health monitoring
    'HealthChecker',
    'HealthStatus', 
    'SystemMetrics',
    'SystemMonitor',
    'get_system_monitor',
    'quick_health_check',
    'detailed_health_check',
    
    # Backup system
    'BackupManager',
    'backup_manager',
    'create_backup',
    'restore_backup',
    'list_available_backups',
    'cleanup_old_backups',
    
    # Metrics collection
    'MetricsCollector',
    'MetricsAnalyzer',
    'MetricPoint',
    'get_metrics_collector',
    'get_metrics_analyzer',
    'record_optimization_metrics',
    'record_prediction_metrics',
    'record_api_metrics',
    'get_performance_summary',
    'generate_performance_report',
    
    # System initialization
    'initialize_monitoring',
    'get_complete_system_status'
]
