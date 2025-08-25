#!/usr/bin/env python3
"""
Complete system deployment and management script.
"""
import os
import sys
import subprocess
import argparse
import time
import json
from pathlib import Path
from datetime import datetime

def run_command(command, capture_output=False, check=True):
    """Run shell command with proper error handling."""
    print(f"🔧 Running: {command}")
    
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
            return result.stdout.strip()
        else:
            result = subprocess.run(command, shell=True, check=check)
            return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {command}")
        print(f"❌ Error: {e}")
        if capture_output and e.stderr:
            print(f"❌ Stderr: {e.stderr}")
        return False

def check_requirements():
    """Check system requirements."""
    print("🔍 Checking system requirements...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        print(f"❌ Python 3.8+ required, found {python_version.major}.{python_version.minor}")
        return False
    else:
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check Docker
    docker_available = run_command("docker --version", capture_output=True)
    if docker_available:
        print(f"✅ Docker: {docker_available}")
    else:
        print("⚠️ Docker not available (optional for local development)")
    
    # Check Docker Compose
    compose_available = run_command("docker-compose --version", capture_output=True)
    if compose_available:
        print(f"✅ Docker Compose: {compose_available}")
    else:
        print("⚠️ Docker Compose not available (optional)")
    
    # Check Git
    git_available = run_command("git --version", capture_output=True)
    if git_available:
        print(f"✅ Git: {git_available}")
    else:
        print("⚠️ Git not available (recommended)")
    
    return True

def setup_environment():
    """Setup development environment."""
    print("🔧 Setting up development environment...")
    
    # Create virtual environment if it doesn't exist
    if not Path("venv").exists():
        print("📦 Creating virtual environment...")
        if not run_command(f"{sys.executable} -m venv venv"):
            return False
    
    # Determine activation script
    if os.name == 'nt':  # Windows
        activate_script = "venv\\Scripts\\activate"
        pip_command = "venv\\Scripts\\pip"
    else:  # Unix/Linux/MacOS
        activate_script = "source venv/bin/activate"
        pip_command = "venv/bin/pip"
    
    # Install requirements
    print("📚 Installing dependencies...")
    if not run_command(f"{pip_command} install -r requirements.txt"):
        return False
    
    # Install package in development mode
    print("🔧 Installing package in development mode...")
    if not run_command(f"{pip_command} install -e .[all]"):
        return False
    
    return True

def setup_configuration():
    """Setup configuration files."""
    print("⚙️ Setting up configuration...")
    
    # Copy .env.example to .env if it doesn't exist
    if not Path(".env").exists():
        if Path(".env.example").exists():
            print("📋 Creating .env from template...")
            import shutil
            shutil.copy(".env.example", ".env")
            print("✅ .env created - please edit with your settings")
        else:
            print("⚠️ .env.example not found - creating basic .env")
            env_content = """# Building Energy Optimizer Configuration

# Environment
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production

# Database
DATABASE_URL=sqlite:///building_energy.db

# Weather API (get free key from openweathermap.org)
OPENWEATHERMAP_API_KEY=your_openweathermap_api_key_here

# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# Dashboard Settings
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=8501

# Logging
LOG_LEVEL=INFO
LOG_FILE_ENABLED=true

# Monitoring
MONITORING_ENABLED=true
METRICS_ENABLED=true
PROMETHEUS_PORT=8090

# Backup
BACKUP_ENABLED=true
BACKUP_RETENTION_DAYS=30
"""
            with open(".env", "w") as f:
                f.write(env_content)
            print("✅ Basic .env created")
    else:
        print("✅ .env already exists")
    
    # Create necessary directories
    directories = ["logs", "models", "data", "backups"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Directory ready: {directory}")
    
    return True

def initialize_database():
    """Initialize database."""
    print("🗄️ Initializing database...")
    
    try:
        # Import after package installation
        from building_energy_optimizer.utils.database import init_database
        init_database()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def run_health_check():
    """Run comprehensive health check."""
    print("🏥 Running health check...")
    
    try:
        from building_energy_optimizer.monitoring import detailed_health_check, generate_performance_report
        
        # Health check
        health_status = detailed_health_check()
        overall_status = health_status['overall_status']
        
        print(f"🎯 Overall Status: {overall_status.upper()}")
        
        if overall_status == 'healthy':
            print("✅ All systems operational")
        elif overall_status == 'warning':
            print("⚠️ Some warnings detected")
            # Show warnings
            for check_name, check_result in health_status['checks'].items():
                if check_result['status'] == 'warning':
                    print(f"   ⚠️ {check_name}: {check_result['message']}")
        else:
            print("❌ Critical issues detected")
            # Show critical issues
            for issue in health_status.get('critical_issues', []):
                print(f"   ❌ {issue['component']}: {issue['message']}")
        
        # Performance report
        print("\n📊 Performance Summary:")
        try:
            report = generate_performance_report()
            # Show just the summary part
            lines = report.split('\n')
            for line in lines:
                if line.startswith(('🤖', '🔮', '⚡', '💰', '🎯')):
                    print(f"   {line}")
        except Exception as e:
            print(f"   ⚠️ Could not generate performance report: {e}")
        
        return overall_status in ['healthy', 'warning']
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def start_services(mode="development"):
    """Start all services."""
    print(f"🚀 Starting services in {mode} mode...")
    
    if mode == "docker":
        # Docker deployment
        if not Path("docker-compose.yml").exists():
            print("❌ docker-compose.yml not found")
            return False
        
        print("🐳 Starting Docker services...")
        if run_command("docker-compose up -d"):
            print("✅ Docker services started")
            print("🌐 Dashboard: http://localhost:8501")
            print("📡 API: http://localhost:8000/docs")
            return True
        else:
            print("❌ Failed to start Docker services")
            return False
    
    else:
        # Local development
        print("💻 Starting local development services...")
        
        # Start API server in background
        print("📡 Starting API server...")
        api_process = subprocess.Popen([
            sys.executable, "scripts/start_api.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for API to start
        time.sleep(3)
        
        # Check if API is running
        api_check = run_command("curl -s http://localhost:8000/ > /dev/null", check=False)
        if api_check:
            print("✅ API server started on http://localhost:8000")
        else:
            print("⚠️ API server may not have started properly")
        
        # Start dashboard
        print("📊 Starting dashboard...")
        dashboard_process = subprocess.Popen([
            sys.executable, "scripts/start_dashboard.py"
        ])
        
        print("✅ Services starting...")
        print("🌐 Dashboard: http://localhost:8501")
        print("📡 API: http://localhost:8000/docs")
        print("📊 Metrics: http://localhost:8090/metrics (if enabled)")
        
        return True

def run_demo():
    """Run complete system demo."""
    print("🎬 Running Building Energy Optimizer demo...")
    
    try:
        from building_energy_optimizer import (
            quick_optimize, 
            create_enhanced_example_data,
            get_version_info
        )
        
        # Show version info
        version_info = get_version_info()
        print(f"📦 Building Energy Optimizer v{version_info['version']}")
        print(f"🤖 Available algorithms: {', '.join(version_info['supported_algorithms'])}")
        print()
        
        # Generate sample data
        print("📊 Generating sample data...")
        data = create_enhanced_example_data('2024-01-01', '2024-01-07')
        print(f"✅ Generated {len(data)} data points")
        
        # Run optimization with different algorithms
        algorithms = ['xgboost', 'lightgbm', 'random_forest']
        results = {}
        
        for algorithm in algorithms:
            print(f"🤖 Testing {algorithm.upper()} algorithm...")
            start_time = time.time()
            
            try:
                result = quick_optimize(data, algorithm=algorithm)
                duration = time.time() - start_time
                
                summary = result['report']['summary']
                results[algorithm] = {
                    'duration': duration,
                    'accuracy': result.get('training_metrics', {}).get('val_r2', 0),
                    'savings_percent': summary['potential_savings_percent'],
                    'cost_savings': summary['cost_savings_estimate_eur'],
                    'suggestions_count': len(result['suggestions'])
                }
                
                print(f"   ✅ Completed in {duration:.1f}s")
                print(f"   🎯 Accuracy: {results[algorithm]['accuracy']:.1%}")
                print(f"   💰 Savings: {results[algorithm]['savings_percent']:.1f}% (€{results[algorithm]['cost_savings']:.2f})")
                print(f"   💡 Suggestions: {results[algorithm]['suggestions_count']}")
                
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                results[algorithm] = {'error': str(e)}
        
        # Show comparison
        print("\n📊 Algorithm Comparison:")
        print("=" * 50)
        successful_results = {k: v for k, v in results.items() if 'error' not in v}
        
        if successful_results:
            best_accuracy = max(successful_results.values(), key=lambda x: x['accuracy'])
            best_speed = min(successful_results.values(), key=lambda x: x['duration'])
            best_savings = max(successful_results.values(), key=lambda x: x['savings_percent'])
            
            print(f"🏆 Best Accuracy: {[k for k, v in successful_results.items() if v['accuracy'] == best_accuracy['accuracy']][0].upper()} ({best_accuracy['accuracy']:.1%})")
            print(f"⚡ Fastest: {[k for k, v in successful_results.items() if v['duration'] == best_speed['duration']][0].upper()} ({best_speed['duration']:.1f}s)")
            print(f"💰 Best Savings: {[k for k, v in successful_results.items() if v['savings_percent'] == best_savings['savings_percent']][0].upper()} ({best_savings['savings_percent']:.1f}%)")
        
        print("\n🎉 Demo completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

def run_tests():
    """Run test suite."""
    print("🧪 Running test suite...")
    
    # Check if pytest is available
    try:
        import pytest
    except ImportError:
        print("❌ pytest not installed - installing...")
        if not run_command(f"{sys.executable} -m pip install pytest pytest-cov"):
            return False
    
    # Run tests
    test_commands = [
        "python -m pytest tests/ -v",
        "python -m pytest tests/test_enhanced_optimizer.py -v",
        "python -m pytest tests/test_api.py -v",
    ]
    
    success = True
    for command in test_commands:
        print(f"\n🧪 Running: {command}")
        if not run_command(command):
            success = False
            print("❌ Test failed")
        else:
            print("✅ Test passed")
    
    return success

def create_backup():
    """Create system backup."""
    print("💾 Creating system backup...")
    
    try:
        from building_energy_optimizer.monitoring import create_backup
        
        result = create_backup("full", include_logs=True)
        
        if result.get('error'):
            print(f"❌ Backup failed: {result['error']}")
            return False
        else:
            backup_id = result['backup_id']
            size_mb = result['total_size_bytes'] / (1024**2)
            print(f"✅ Backup created: {backup_id} ({size_mb:.1f} MB)")
            
            # Show backup components
            if 'components' in result:
                for component, component_info in result['components'].items():
                    if component_info.get('status') == 'success':
                        print(f"   ✅ {component}: OK")
                    else:
                        print(f"   ⚠️ {component}: {component_info.get('reason', 'Unknown')}")
            
            return True
    
    except Exception as e:
        print(f"❌ Backup creation failed: {e}")
        return False

def performance_benchmark():
    """Run performance benchmark."""
    print("⚡ Running performance benchmark...")
    
    try:
        from building_energy_optimizer import create_enhanced_example_data, quick_optimize
        
        # Different data sizes
        test_cases = [
            ("1 week", '2024-01-01', '2024-01-07'),
            ("1 month", '2024-01-01', '2024-01-31'), 
            ("3 months", '2024-01-01', '2024-03-31')
        ]
        
        results = {}
        
        for case_name, start_date, end_date in test_cases:
            print(f"🔄 Testing {case_name} dataset...")
            
            # Generate data
            data = create_enhanced_example_data(start_date, end_date)
            data_size = len(data)
            
            # Test XGBoost performance
            start_time = time.time()
            result = quick_optimize(data, algorithm='xgboost')
            duration = time.time() - start_time
            
            accuracy = result.get('training_metrics', {}).get('val_r2', 0)
            
            results[case_name] = {
                'data_points': data_size,
                'duration_seconds': duration,
                'accuracy': accuracy,
                'data_points_per_second': data_size / duration
            }
            
            print(f"   📊 {data_size:,} points in {duration:.1f}s ({data_size/duration:.0f} points/sec)")
            print(f"   🎯 Accuracy: {accuracy:.1%}")
        
        # Show benchmark summary
        print("\n📈 Performance Benchmark Results:")
        print("=" * 50)
        for case_name, metrics in results.items():
            print(f"📅 {case_name}:")
            print(f"   • Data Points: {metrics['data_points']:,}")
            print(f"   • Duration: {metrics['duration_seconds']:.1f}s") 
            print(f"   • Processing Speed: {metrics['data_points_per_second']:.0f} points/sec")
            print(f"   • Accuracy: {metrics['accuracy']:.1%}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        return False

def show_status():
    """Show comprehensive system status."""
    print("📊 System Status Report")
    print("=" * 30)
    
    try:
        from building_energy_optimizer.monitoring import get_complete_system_status
        
        status = get_complete_system_status()
        overall = status['overall_status']
        
        # Overall status
        status_emoji = {
            'healthy': '✅',
            'warning': '⚠️', 
            'critical': '❌',
            'unknown': '❓'
        }
        
        print(f"{status_emoji.get(overall, '❓')} Overall Status: {overall.upper()}")
        print(f"📅 Last Check: {status['timestamp']}")
        print()
        
        # Health components
        if 'health' in status:
            health = status['health']
            print("🏥 Component Health:")
            for component, check_result in health['checks'].items():
                emoji = status_emoji.get(check_result['status'], '❓')
                response_time = check_result.get('response_time_ms', 0)
                print(f"   {emoji} {component}: {check_result['message']} ({response_time:.1f}ms)")
        
        # Performance metrics
        if 'performance' in status:
            performance = status['performance']['business_metrics']
            print(f"\n📈 Performance Metrics:")
            print(f"   🤖 Optimizations: {performance['total_optimizations']:,}")
            print(f"   🔮 Predictions: {performance['total_predictions']:,}")
            print(f"   ⚡ Energy Analyzed: {performance['total_energy_analyzed_kwh']:,.0f} kWh")
            print(f"   💰 Savings Identified: {performance['total_savings_identified_kwh']:,.0f} kWh")
        
        # Backup status
        if 'backups' in status:
            backup_info = status['backups']
            print(f"\n💾 Backup Status:")
            print(f"   📦 Total Backups: {backup_info['total_backups']}")
            if backup_info['latest_backup']:
                latest = backup_info['latest_backup']
                print(f"   🕐 Latest: {latest['backup_id']} ({latest.get('size_bytes', 0) / (1024**2):.1f} MB)")
        
        return overall in ['healthy', 'warning']
        
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        return False

def main():
    """Main deployment script."""
    parser = argparse.ArgumentParser(description="Building Energy Optimizer Deployment Manager")
    parser.add_argument('action', choices=[
        'setup', 'start', 'stop', 'restart', 'status', 'test', 'demo', 
        'backup', 'health', 'benchmark', 'clean', 'update'
    ], help="Action to perform")
    
    parser.add_argument('--mode', choices=['development', 'docker', 'production'], 
                       default='development', help="Deployment mode")
    parser.add_argument('--force', action='store_true', help="Force action without confirmation")
    parser.add_argument('--verbose', action='store_true', help="Verbose output")
    
    args = parser.parse_args()
    
    # Set verbose logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    
    print(f"🏢 Building Energy Optimizer Deployment Manager")
    print(f"🎯 Action: {args.action} | Mode: {args.mode}")
    print("=" * 50)
    
    success = True
    
    if args.action == 'setup':
        success = (
            check_requirements() and
            setup_environment() and
            setup_configuration() and
            initialize_database()
        )
        
        if success:
            print("\n🎉 Setup completed successfully!")
            print("Next steps:")
            print("  1. Edit .env file with your API keys")
            print("  2. Run: python deploy.py start")
            print("  3. Access dashboard at http://localhost:8501")
        else:
            print("\n❌ Setup failed - check errors above")
    
    elif args.action == 'start':
        success = start_services(args.mode)
    
    elif args.action == 'status':
        success = show_status()
    
    elif args.action == 'health':
        success = run_health_check()
    
    elif args.action == 'test':
        success = run_tests()
    
    elif args.action == 'demo':
        success = run_demo()
    
    elif args.action == 'benchmark':
        success = performance_benchmark()
    
    elif args.action == 'backup':
        success = create_backup()
    
    elif args.action == 'stop':
        if args.mode == 'docker':
            success = run_command("docker-compose down")
        else:
            print("🛑 Stopping local services...")
            # Kill processes using the ports
            run_command("pkill -f 'streamlit run'", check=False)
            run_command("pkill -f 'uvicorn'", check=False)
            print("✅ Services stopped")
    
    elif args.action == 'restart':
        if args.mode == 'docker':
            run_command("docker-compose restart")
        else:
            # Stop and start
            main_args = argparse.Namespace(action='stop', mode=args.mode, force=args.force, verbose=args.verbose)
            args = main_args
            print("🛑 Stopping services...")
            time.sleep(2)
            args.action = 'start'
            success = start_services(args.mode)
    
    elif args.action == 'clean':
        print("🧹 Cleaning up...")
        if args.force or input("Remove logs, models, and cache? (y/N): ").lower() == 'y':
            # Clean up
            cleanup_dirs = ['logs', '__pycache__', '.pytest_cache']
            for cleanup_dir in cleanup_dirs:
                if Path(cleanup_dir).exists():
                    import shutil
                    shutil.rmtree(cleanup_dir)
                    print(f"   🗑️ Removed {cleanup_dir}")
            
            # Remove compiled Python files
            run_command("find . -name '*.pyc' -delete", check=False)
            print("✅ Cleanup complete")
    
    elif args.action == 'update':
        print("🔄 Updating system...")
        success = (
            run_command("git pull") and
            run_command(f"{sys.executable} -m pip install -r requirements.txt") and
            run_command(f"{sys.executable} -m pip install -e .[all]")
        )
        
        if success:
            print("✅ Update completed - restart services to apply changes")
    
    # Final status
    if success:
        print(f"\n✅ Action '{args.action}' completed successfully!")
        exit_code = 0
    else:
        print(f"\n❌ Action '{args.action}' failed!")
        exit_code = 1
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
