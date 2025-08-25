#!/usr/bin/env python3
"""
🏢⚡ Energy Optimizer Pro - Development Tools
============================================
Comprehensive development utilities and tools
"""

import os
import sys
import json
import time
import click
import subprocess
import asyncio
import httpx
import psutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, TaskID
from rich.tree import Tree
from rich.text import Text
from rich import box

# Initialize Rich console
console = Console()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
BACKEND_DIR = PROJECT_ROOT / "backend"
LOGS_DIR = PROJECT_ROOT / "logs"

class DevTools:
    """🛠️ Development tools and utilities"""
    
    def __init__(self):
        self.console = console
        
    def print_banner(self):
        """Print the Energy Optimizer Pro banner"""
        banner = """
╔══════════════════════════════════════════════════════════════════╗
║                  🏢⚡ ENERGY OPTIMIZER PRO                        ║
║                   Development Tools v2.0                        ║
║                                                                  ║
║              🛠️ Comprehensive Development Suite                   ║
╚══════════════════════════════════════════════════════════════════╝
        """
        self.console.print(Panel(banner, style="cyan"))

    def health_check(self) -> bool:
        """🔍 Comprehensive system health check"""
        self.print_banner()
        self.console.print("🔍 Running comprehensive health check...\n")
        
        checks = []
        
        # System checks
        checks.extend(self._check_system_resources())
        
        # Service checks
        checks.extend(self._check_services())
        
        # Database checks
        checks.extend(self._check_database())
        
        # Application checks
        checks.extend(self._check_application())
        
        # Display results
        self._display_health_results(checks)
        
        # Return overall status
        return all(check['status'] for check in checks)

    def _check_system_resources(self) -> List[Dict]:
        """💻 Check system resource usage"""
        checks = []
        
        # CPU Usage
        cpu_percent = psutil.cpu_percent(interval=1)
        checks.append({
            'category': 'System',
            'name': 'CPU Usage',
            'status': cpu_percent < 80,
            'value': f"{cpu_percent}%",
            'threshold': '< 80%',
            'details': f"Current: {cpu_percent}% | Cores: {psutil.cpu_count()}"
        })
        
        # Memory Usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        checks.append({
            'category': 'System',
            'name': 'Memory Usage',
            'status': memory_percent < 85,
            'value': f"{memory_percent}%",
            'threshold': '< 85%',
            'details': f"Used: {memory.used // (1024**3)}GB / Total: {memory.total // (1024**3)}GB"
        })
        
        # Disk Usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        checks.append({
            'category': 'System',
            'name': 'Disk Usage',
            'status': disk_percent < 90,
            'value': f"{disk_percent:.1f}%",
            'threshold': '< 90%',
            'details': f"Used: {disk.used // (1024**3)}GB / Total: {disk.total // (1024**3)}GB"
        })
        
        return checks

    def _check_services(self) -> List[Dict]:
        """🐳 Check Docker services status"""
        checks = []
        
        try:
            # Check Docker daemon
            result = subprocess.run(['docker', 'info'], capture_output=True, text=True)
            docker_running = result.returncode == 0
            
            checks.append({
                'category': 'Docker',
                'name': 'Docker Daemon',
                'status': docker_running,
                'value': 'Running' if docker_running else 'Stopped',
                'threshold': 'Running',
                'details': 'Docker daemon accessible'
            })
            
            if docker_running:
                # Check containers
                result = subprocess.run(['docker-compose', 'ps', '--format', 'json'], 
                                      capture_output=True, text=True, cwd=PROJECT_ROOT)
                
                if result.returncode == 0:
                    containers = []
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            try:
                                container = json.loads(line)
                                containers.append(container)
                            except:
                                continue
                    
                    for container in containers:
                        is_healthy = container.get('State', '').lower() == 'running'
                        checks.append({
                            'category': 'Services',
                            'name': container.get('Name', 'Unknown'),
                            'status': is_healthy,
                            'value': container.get('State', 'Unknown'),
                            'threshold': 'Running',
                            'details': f"Ports: {container.get('Ports', 'N/A')}"
                        })
        
        except Exception as e:
            checks.append({
                'category': 'Docker',
                'name': 'Docker Services',
                'status': False,
                'value': 'Error',
                'threshold': 'Running',
                'details': str(e)
            })
        
        return checks

    def _check_database(self) -> List[Dict]:
        """🗄️ Check database connectivity and performance"""
        checks = []
        
        try:
            # PostgreSQL check
            result = subprocess.run([
                'docker-compose', 'exec', '-T', 'postgres', 
                'pg_isready', '-U', 'energy_user'
            ], capture_output=True, text=True, cwd=PROJECT_ROOT)
            
            postgres_healthy = result.returncode == 0
            checks.append({
                'category': 'Database',
                'name': 'PostgreSQL',
                'status': postgres_healthy,
                'value': 'Connected' if postgres_healthy else 'Disconnected',
                'threshold': 'Connected',
                'details': 'PostgreSQL connection test'
            })
            
            # Redis check
            result = subprocess.run([
                'docker-compose', 'exec', '-T', 'redis', 
                'redis-cli', 'ping'
            ], capture_output=True, text=True, cwd=PROJECT_ROOT)
            
            redis_healthy = result.returncode == 0 and 'PONG' in result.stdout
            checks.append({
                'category': 'Database',
                'name': 'Redis',
                'status': redis_healthy,
                'value': 'Connected' if redis_healthy else 'Disconnected',
                'threshold': 'Connected',
                'details': 'Redis ping test'
            })
            
        except Exception as e:
            checks.append({
                'category': 'Database',
                'name': 'Database Check',
                'status': False,
                'value': 'Error',
                'threshold': 'Connected',
                'details': str(e)
            })
        
        return checks

    def _check_application(self) -> List[Dict]:
        """🚀 Check application endpoints and functionality"""
        checks = []
        
        endpoints = [
            ('Backend Health', 'http://localhost:8000/health'),
            ('Backend API', 'http://localhost:8000/api/health'),
            ('Frontend', 'http://localhost:3000'),
            ('API Docs', 'http://localhost:8000/docs'),
        ]
        
        for name, url in endpoints:
            try:
                import requests
                response = requests.get(url, timeout=5)
                is_healthy = response.status_code == 200
                
                checks.append({
                    'category': 'Application',
                    'name': name,
                    'status': is_healthy,
                    'value': f"HTTP {response.status_code}",
                    'threshold': 'HTTP 200',
                    'details': f"Response time: {response.elapsed.total_seconds():.3f}s"
                })
                
            except Exception as e:
                checks.append({
                    'category': 'Application',
                    'name': name,
                    'status': False,
                    'value': 'Unreachable',
                    'threshold': 'HTTP 200',
                    'details': str(e)
                })
        
        return checks

    def _display_health_results(self, checks: List[Dict]):
        """📊 Display health check results in a table"""
        table = Table(title="🏢⚡ System Health Check Results", box=box.ROUNDED)
        
        table.add_column("Category", style="cyan", no_wrap=True)
        table.add_column("Check", style="white", no_wrap=True)
        table.add_column("Status", justify="center", no_wrap=True)
        table.add_column("Value", style="yellow", no_wrap=True)
        table.add_column("Threshold", style="blue", no_wrap=True)
        table.add_column("Details", style="dim")
        
        for check in checks:
            status_icon = "✅" if check['status'] else "❌"
            status_color = "green" if check['status'] else "red"
            
            table.add_row(
                check['category'],
                check['name'],
                Text(status_icon, style=status_color),
                check['value'],
                check['threshold'],
                check['details']
            )
        
        self.console.print(table)
        
        # Summary
        total_checks = len(checks)
        passed_checks = sum(1 for check in checks if check['status'])
        failed_checks = total_checks - passed_checks
        
        if failed_checks == 0:
            self.console.print(Panel(
                f"🎉 All {total_checks} health checks passed!",
                style="green", title="✅ Health Check Summary"
            ))
        else:
            self.console.print(Panel(
                f"⚠️ {failed_checks} of {total_checks} checks failed",
                style="red", title="❌ Health Check Summary"
            ))

    def setup_development(self):
        """🔧 Setup development environment"""
        self.print_banner()
        self.console.print("🔧 Setting up development environment...\n")
        
        with Progress() as progress:
            # Tasks
            task1 = progress.add_task("📦 Installing frontend dependencies...", total=100)
            task2 = progress.add_task("🐍 Setting up Python environment...", total=100)
            task3 = progress.add_task("🗄️ Setting up database...", total=100)
            task4 = progress.add_task("📊 Generating sample data...", total=100)
            
            # Frontend setup
            self._run_command(['npm', 'install'], cwd=FRONTEND_DIR)
            progress.update(task1, completed=100)
            
            # Backend setup
            self._setup_python_env()
            progress.update(task2, completed=100)
            
            # Database setup
            self._setup_database()
            progress.update(task3, completed=100)
            
            # Sample data
            self._generate_sample_data(buildings=3, days=7)
            progress.update(task4, completed=100)
        
        self.console.print("✅ Development environment setup completed!")

    def generate_sample_data(self, buildings: int = 5, days: int = 30):
        """📊 Generate sample data for testing"""
        self.print_banner()
        self.console.print(f"📊 Generating sample data ({buildings} buildings, {days} days)...\n")
        
        # Import and run data generation
        sys.path.append(str(BACKEND_DIR))
        
        from scripts.seed_data import DataSeeder
        
        seeder = DataSeeder()
        seeder.generate_sample_data(buildings=buildings, days=days)
        
        self.console.print("✅ Sample data generation completed!")

    def code_quality_check(self):
        """🔍 Run comprehensive code quality checks"""
        self.print_banner()
        self.console.print("🔍 Running code quality checks...\n")
        
        results = []
        
        # Frontend checks
        self.console.print("🎨 Checking frontend code quality...")
        frontend_results = self._check_frontend_quality()
        results.extend(frontend_results)
        
        # Backend checks
        self.console.print("🐍 Checking backend code quality...")
        backend_results = self._check_backend_quality()
        results.extend(backend_results)
        
        # Display results
        self._display_quality_results(results)

    def _check_frontend_quality(self) -> List[Dict]:
        """🎨 Check frontend code quality"""
        checks = []
        
        # ESLint
        result = self._run_command(['npm', 'run', 'lint'], cwd=FRONTEND_DIR)
        checks.append({
            'tool': 'ESLint',
            'category': 'Frontend',
            'status': result.returncode == 0,
            'details': 'JavaScript/TypeScript linting'
        })
        
        # TypeScript check
        result = self._run_command(['npm', 'run', 'type-check'], cwd=FRONTEND_DIR)
        checks.append({
            'tool': 'TypeScript',
            'category': 'Frontend', 
            'status': result.returncode == 0,
            'details': 'Type checking'
        })
        
        # Prettier check
        result = self._run_command(['npx', 'prettier', '--check', '.'], cwd=FRONTEND_DIR)
        checks.append({
            'tool': 'Prettier',
            'category': 'Frontend',
            'status': result.returncode == 0,
            'details': 'Code formatting'
        })
        
        return checks

    def _check_backend_quality(self) -> List[Dict]:
        """🐍 Check backend code quality"""
        checks = []
        
        # Activate virtual environment
        venv_python = BACKEND_DIR / "venv" / "bin" / "python"
        if not venv_python.exists():
            venv_python = BACKEND_DIR / "venv" / "Scripts" / "python.exe"
        
        # Flake8
        result = self._run_command([str(venv_python), '-m', 'flake8', '.'], cwd=BACKEND_DIR)
        checks.append({
            'tool': 'Flake8',
            'category': 'Backend',
            'status': result.returncode == 0,
            'details': 'PEP 8 compliance'
        })
        
        # Black
        result = self._run_command([str(venv_python), '-m', 'black', '--check', '.'], cwd=BACKEND_DIR)
        checks.append({
            'tool': 'Black',
            'category': 'Backend',
            'status': result.returncode == 0,
            'details': 'Code formatting'
        })
        
        # isort
        result = self._run_command([str(venv_python), '-m', 'isort', '--check-only', '.'], cwd=BACKEND_DIR)
        checks.append({
            'tool': 'isort',
            'category': 'Backend',
            'status': result.returncode == 0,
            'details': 'Import sorting'
        })
        
        return checks

    def _display_quality_results(self, results: List[Dict]):
        """📊 Display code quality results"""
        table = Table(title="🔍 Code Quality Check Results", box=box.ROUNDED)
        
        table.add_column("Category", style="cyan")
        table.add_column("Tool", style="white")
        table.add_column("Status", justify="center")
        table.add_column("Details", style="dim")
        
        for result in results:
            status_icon = "✅" if result['status'] else "❌"
            status_color = "green" if result['status'] else "red"
            
            table.add_row(
                result['category'],
                result['tool'],
                Text(status_icon, style=status_color),
                result['details']
            )
        
        self.console.print(table)
        
        # Summary
        total_checks = len(results)
        passed_checks = sum(1 for r in results if r['status'])
        
        if passed_checks == total_checks:
            self.console.print(Panel(
                f"🎉 All {total_checks} quality checks passed!",
                style="green", title="✅ Quality Summary"
            ))
        else:
            failed_checks = total_checks - passed_checks
            self.console.print(Panel(
                f"⚠️ {failed_checks} of {total_checks} checks failed",
                style="red", title="❌ Quality Summary"
            ))

    def project_statistics(self):
        """📊 Generate comprehensive project statistics"""
        self.print_banner()
        self.console.print("📊 Analyzing project statistics...\n")
        
        stats = {
            'files': self._count_files(),
            'lines': self._count_lines(),
            'dependencies': self._count_dependencies(),
            'tests': self._count_tests(),
            'git': self._git_statistics()
        }
        
        self._display_statistics(stats)

    def _count_files(self) -> Dict:
        """📁 Count files by type"""
        file_counts = {}
        
        extensions = {
            '.ts': 'TypeScript',
            '.tsx': 'TypeScript React',
            '.js': 'JavaScript', 
            '.jsx': 'JavaScript React',
            '.py': 'Python',
            '.sql': 'SQL',
            '.yml': 'YAML',
            '.yaml': 'YAML',
            '.json': 'JSON',
            '.md': 'Markdown',
            '.sh': 'Shell Scripts',
            '.env': 'Environment'
        }
        
        for ext, lang in extensions.items():
            count = len(list(PROJECT_ROOT.rglob(f"*{ext}")))
            if count > 0:
                file_counts[lang] = count
        
        return file_counts

    def _count_lines(self) -> Dict:
        """📝 Count lines of code"""
        line_counts = {}
        
        # Frontend TypeScript/JavaScript
        frontend_files = list(FRONTEND_DIR.rglob("*.ts")) + list(FRONTEND_DIR.rglob("*.tsx"))
        frontend_lines = sum(self._count_file_lines(f) for f in frontend_files)
        line_counts['Frontend'] = frontend_lines
        
        # Backend Python
        backend_files = list(BACKEND_DIR.rglob("*.py"))
        backend_lines = sum(self._count_file_lines(f) for f in backend_files)
        line_counts['Backend'] = backend_lines
        
        # Configuration
        config_files = list(PROJECT_ROOT.rglob("*.yml")) + list(PROJECT_ROOT.rglob("*.yaml"))
        config_lines = sum(self._count_file_lines(f) for f in config_files)
        line_counts['Configuration'] = config_lines
        
        return line_counts

    def _count_file_lines(self, file_path: Path) -> int:
        """📝 Count lines in a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return sum(1 for line in f if line.strip())
        except:
            return 0

    def _count_dependencies(self) -> Dict:
        """📦 Count project dependencies"""
        deps = {}
        
        # Frontend dependencies
        try:
            with open(FRONTEND_DIR / "package.json", 'r') as f:
                package_json = json.load(f)
                deps['Frontend'] = len(package_json.get('dependencies', {}))
                deps['Frontend Dev'] = len(package_json.get('devDependencies', {}))
        except:
            pass
        
        # Backend dependencies
        try:
            with open(BACKEND_DIR / "requirements.txt", 'r') as f:
                deps['Backend'] = len([line for line in f if line.strip() and not line.startswith('#')])
        except:
            pass
        
        return deps

    def _count_tests(self) -> Dict:
        """🧪 Count test files"""
        test_counts = {}
        
        # Frontend tests
        frontend_tests = len(list(FRONTEND_DIR.rglob("*.test.*"))) + len(list(FRONTEND_DIR.rglob("*.spec.*")))
        test_counts['Frontend Tests'] = frontend_tests
        
        # Backend tests
        backend_tests = len(list((BACKEND_DIR / "tests").rglob("test_*.py")))
        test_counts['Backend Tests'] = backend_tests
        
        # E2E tests
        e2e_tests = len(list(FRONTEND_DIR.rglob("*.e2e.*")))
        test_counts['E2E Tests'] = e2e_tests
        
        return test_counts

    def _git_statistics(self) -> Dict:
        """📊 Git repository statistics"""
        try:
            # Commit count
            result = subprocess.run(['git', 'rev-list', '--count', 'HEAD'], 
                                  capture_output=True, text=True, cwd=PROJECT_ROOT)
            commit_count = int(result.stdout.strip()) if result.returncode == 0 else 0
            
            # Contributors
            result = subprocess.run(['git', 'shortlog', '-sn', '--all'], 
                                  capture_output=True, text=True, cwd=PROJECT_ROOT)
            contributors = len(result.stdout.strip().split('\n')) if result.returncode == 0 else 0
            
            # Branches
            result = subprocess.run(['git', 'branch', '-r'], 
                                  capture_output=True, text=True, cwd=PROJECT_ROOT)
            branches = len(result.stdout.strip().split('\n')) if result.returncode == 0 else 0
            
            return {
                'Commits': commit_count,
                'Contributors': contributors,
                'Branches': branches
            }
        except:
            return {}

    def _display_statistics(self, stats: Dict):
        """📊 Display project statistics"""
        
        # Files table
        if stats['files']:
            files_table = Table(title="📁 File Statistics", box=box.ROUNDED)
            files_table.add_column("File Type", style="cyan")
            files_table.add_column("Count", justify="right", style="green")
            
            for file_type, count in stats['files'].items():
                files_table.add_row(file_type, str(count))
            
            self.console.print(files_table)
        
        # Lines of code table
        if stats['lines']:
            lines_table = Table(title="📝 Lines of Code", box=box.ROUNDED)
            lines_table.add_column("Component", style="cyan")
            lines_table.add_column("Lines", justify="right", style="green")
            
            total_lines = 0
            for component, lines in stats['lines'].items():
                lines_table.add_row(component, f"{lines:,}")
                total_lines += lines
            
            lines_table.add_row("Total", f"{total_lines:,}", style="bold yellow")
            self.console.print(lines_table)
        
        # Dependencies table
        if stats['dependencies']:
            deps_table = Table(title="📦 Dependencies", box=box.ROUNDED)
            deps_table.add_column("Type", style="cyan")
            deps_table.add_column("Count", justify="right", style="green")
            
            for dep_type, count in stats['dependencies'].items():
                deps_table.add_row(dep_type, str(count))
            
            self.console.print(deps_table)
        
        # Git statistics
        if stats['git']:
            git_table = Table(title="📊 Git Statistics", box=box.ROUNDED)
            git_table.add_column("Metric", style="cyan")
            git_table.add_column("Value", justify="right", style="green")
            
            for metric, value in stats['git'].items():
                git_table.add_row(metric, str(value))
            
            self.console.print(git_table)

    def generate_api_docs(self):
        """📖 Generate comprehensive API documentation"""
        self.print_banner()
        self.console.print("📖 Generating API documentation...\n")
        
        # Start backend if not running
        self.console.print("🔍 Checking if backend is running...")
        try:
            import requests
            response = requests.get('http://localhost:8000/health', timeout=5)
            if response.status_code != 200:
                raise Exception("Backend not healthy")
        except:
            self.console.print("🚀 Starting backend for docs generation...")
            self._run_command(['./start.sh', 'backend', 'dev'], background=True)
            time.sleep(15)
        
        # Generate OpenAPI spec
        self.console.print("📋 Extracting OpenAPI specification...")
        try:
            import requests
            response = requests.get('http://localhost:8000/openapi.json')
            openapi_spec = response.json()
            
            # Save OpenAPI spec
            docs_dir = PROJECT_ROOT / "docs" / "api"
            docs_dir.mkdir(parents=True, exist_ok=True)
            
            with open(docs_dir / "openapi.json", 'w') as f:
                json.dump(openapi_spec, f, indent=2)
            
            self.console.print("✅ OpenAPI specification saved")
            
        except Exception as e:
            self.console.print(f"❌ Failed to generate OpenAPI spec: {e}")

    def _run_command(self, cmd: List[str], cwd: Optional[Path] = None, background: bool = False) -> subprocess.CompletedProcess:
        """🔧 Run a command with proper handling"""
        try:
            if background:
                subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return subprocess.CompletedProcess(cmd, 0)
            else:
                return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=300)
        except subprocess.TimeoutExpired:
            self.console.print(f"⏰ Command timed out: {' '.join(cmd)}")
            return subprocess.CompletedProcess(cmd, 1)
        except Exception as e:
            self.console.print(f"❌ Command failed: {e}")
            return subprocess.CompletedProcess(cmd, 1)

    def _setup_python_env(self):
        """🐍 Setup Python virtual environment"""
        venv_dir = BACKEND_DIR / "venv"
        
        if not venv_dir.exists():
            self._run_command(['python3', '-m', 'venv', 'venv'], cwd=BACKEND_DIR)
        
        # Install requirements
        venv_python = venv_dir / "bin" / "python"
        if not venv_python.exists():
            venv_python = venv_dir / "Scripts" / "python.exe"
        
        self._run_command([str(venv_python), '-m', 'pip', 'install', '--upgrade', 'pip'], cwd=BACKEND_DIR)
        self._run_command([str(venv_python), '-m', 'pip', 'install', '-r', 'requirements.txt'], cwd=BACKEND_DIR)

    def _setup_database(self):
        """🗄️ Setup database"""
        # Start database services
        self._run_command(['docker-compose', 'up', '-d', 'postgres', 'redis'], cwd=PROJECT_ROOT)
        
        # Wait for database
        time.sleep(10)
        
        # Run migrations
        venv_python = BACKEND_DIR / "venv" / "bin" / "python"
        if not venv_python.exists():
            venv_python = BACKEND_DIR / "venv" / "Scripts" / "python.exe"
        
        self._run_command([str(venv_python), '-m', 'alembic', 'upgrade', 'head'], cwd=BACKEND_DIR)

    def _generate_sample_data(self, buildings: int, days: int):
        """📊 Generate sample data"""
        venv_python = BACKEND_DIR / "venv" / "bin" / "python"
        if not venv_python.exists():
            venv_python = BACKEND_DIR / "venv" / "Scripts" / "python.exe"
        
        self._run_command([
            str(venv_python), 'scripts/seed_data.py',
            '--buildings', str(buildings),
            '--days', str(days)
        ], cwd=BACKEND_DIR)


# ================================
# 🎯 CLI Interface
# ================================

@click.group()
@click.version_option(version='2.0.0', prog_name='Energy Optimizer Pro Dev Tools')
def cli():
    """🏢⚡ Energy Optimizer Pro - Development Tools"""
    pass

@cli.command()
def health():
    """🔍 Run comprehensive system health check"""
    tools = DevTools()
    success = tools.health_check()
    sys.exit(0 if success else 1)

@cli.command()
def setup():
    """🔧 Setup development environment"""
    tools = DevTools()
    tools.setup_development()

@cli.command()
@click.option('--buildings', default=5, help='Number of sample buildings')
@click.option('--days', default=30, help='Days of historical data')
def generate_data(buildings: int, days: int):
    """📊 Generate sample data for testing"""
    tools = DevTools()
    tools.generate_sample_data(buildings, days)

@cli.command()
def quality():
    """🔍 Run code quality checks"""
    tools = DevTools()
    tools.code_quality_check()

@cli.command()
def stats():
    """📊 Show project statistics"""
    tools = DevTools()
    tools.project_statistics()

@cli.command()
def docs():
    """📖 Generate API documentation"""
    tools = DevTools()
    tools.generate_api_docs()

if __name__ == '__main__':
    cli()
