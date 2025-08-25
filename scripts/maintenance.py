#!/usr/bin/env python3
"""
Utility and maintenance script for Building Energy Optimizer.
"""
import os
import sys
import subprocess
import shutil
import argparse
import json
from pathlib import Path
from datetime import datetime, timedelta
import sqlite3

def print_header(title):
    """Print formatted header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def clean_project():
    """Clean project artifacts."""
    print_header("🧹 CLEANING PROJECT")
    
    # Directories to clean
    clean_dirs = [
        "__pycache__",
        ".pytest_cache", 
        "*.egg-info",
        ".mypy_cache",
        ".coverage",
        "htmlcov",
        "dist",
        "build"
    ]
    
    files_removed = 0
    for pattern in clean_dirs:
        for path in Path(".").rglob(pattern):
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
                print(f"🗑️ Removed directory: {path}")
                files_removed += 1
            elif path.is_file():
                path.unlink()
                print(f"🗑️ Removed file: {path}")
                files_removed += 1
    
    # Clean log files older than 30 days
    log_dir = Path("logs")
    if log_dir.exists():
        cutoff_date = datetime.now() - timedelta(days=30)
        for log_file in log_dir.glob("*.log*"):
            if log_file.stat().st_mtime < cutoff_date.timestamp():
                log_file.unlink()
                print(f"🗑️ Removed old log: {log_file}")
                files_removed += 1
    
    print(f"✅ Cleanup complete! Removed {files_removed} items")

def check_project_health():
    """Check project health and dependencies."""
    print_header("🔍 PROJECT HEALTH CHECK")
    
    issues = []
    
    # Check required files
    required_files = [
        "requirements.txt",
        "setup.py", 
        "README.md",
        "src/building_energy_optimizer/__init__.py",
        "src/building_energy_optimizer/optimizer.py",
        "tests/test_enhanced_optimizer.py"
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            issues.append(f"Missing required file: {file_path}")
        else:
            print(f"✅ {file_path}")
    
    # Check Python imports
    print("\n🐍 Checking Python imports...")
    try:
        sys.path.insert(0, "src")
        import building_energy_optimizer
        print("✅ Main package imports successfully")
        
        # Check optional dependencies
        try:
            import xgboost
            print("✅ XGBoost available")
        except ImportError:
            issues.append("XGBoost not installed (optional)")
        
        try:
            import lightgbm
            print("✅ LightGBM available")
        except ImportError:
            issues.append("LightGBM not installed (optional)")
        
        try:
            import fastapi
            print("✅ FastAPI available")
        except ImportError:
            issues.append("FastAPI not installed")
        
        try:
            import streamlit
            print("✅ Streamlit available")
        except ImportError:
            issues.append("Streamlit not installed")
        
    except ImportError as e:
        issues.append(f"Failed to import main package: {e}")
    
    # Check database
    print("\n🗄️ Checking database...")
    if os.path.exists("building_energy.db"):
        try:
            conn = sqlite3.connect("building_energy.db")
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"✅ Database has {len(tables)} tables")
            conn.close()
        except Exception as e:
            issues.append(f"Database error: {e}")
    else:
        print("ℹ️ No database found (will be created on first run)")
    
    # Check model files
    print("\n🧠 Checking trained models...")
    model_files = list(Path(".").glob("*.joblib"))
    if model_files:
        for model_file in model_files:
            file_size = model_file.stat().st_size / (1024*1024)  # MB
            print(f"✅ Found model: {model_file.name} ({file_size:.1f} MB)")
    else:
        print("ℹ️ No trained models found")
    
    # Summary
    if issues:
        print(f"\n⚠️ Found {len(issues)} issues:")
        for issue in issues:
            print(f"   • {issue}")
        return False
    else:
        print("\n🎉 Project health check passed!")
        return True

def generate_performance_report():
    """Generate performance benchmark report."""
    print_header("📊 PERFORMANCE BENCHMARK")
    
    try:
        # Run performance tests
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/test_enhanced_optimizer.py::TestPerformance",
            "-v", "--tb=short"
        ], capture_output=True, text=True)
        
        print("🏃 Performance test results:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Warnings:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Failed to run performance tests: {e}")
        return False

def backup_models():
    """Backup trained models."""
    print_header("💾 BACKING UP MODELS")
    
    # Create backup directory
    backup_dir = Path("backups") / datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Backup model files
    model_files = list(Path(".").glob("*.joblib"))
    models_backed_up = 0
    
    for model_file in model_files:
        backup_path = backup_dir / model_file.name
        shutil.copy2(model_file, backup_path)
        print(f"💾 Backed up: {model_file.name}")
        models_backed_up += 1
    
    # Backup database
    if os.path.exists("building_energy.db"):
        backup_db_path = backup_dir / "building_energy.db"
        shutil.copy2("building_energy.db", backup_db_path)
        print(f"💾 Backed up: building_energy.db")
        models_backed_up += 1
    
    # Backup configuration
    if os.path.exists(".env"):
        backup_env_path = backup_dir / "env_backup.txt"
        shutil.copy2(".env", backup_env_path)
        print(f"💾 Backed up: .env")
    
    print(f"✅ Backup complete! {models_backed_up} files backed up to {backup_dir}")

def update_dependencies():
    """Update project dependencies."""
    print_header("📦 UPDATING DEPENDENCIES")
    
    try:
        # Update pip
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True)
        print("✅ pip updated")
        
        # Update dependencies
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "-r", "requirements.txt"], 
                      check=True)
        print("✅ Dependencies updated")
        
        # Reinstall package
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", ".[all]"], 
                      check=True)
        print("✅ Package reinstalled")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to update dependencies: {e}")
        return False

def generate_project_stats():
    """Generate project statistics."""
    print_header("📈 PROJECT STATISTICS")
    
    # Count lines of code
    code_files = []
    for ext in ['*.py', '*.yml', '*.yaml', '*.json', '*.md']:
        code_files.extend(Path(".").rglob(ext))
    
    total_lines = 0
    file_count = 0
    
    for file_path in code_files:
        if 'venv' in str(file_path) or '__pycache__' in str(file_path):
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
                total_lines += lines
                file_count += 1
        except:
            continue
    
    print(f"📊 Code Statistics:")
    print(f"   • Total files: {file_count}")
    print(f"   • Total lines: {total_lines:,}")
    print(f"   • Average lines per file: {total_lines // file_count if file_count > 0 else 0}")
    
    # Database stats
    if os.path.exists("building_energy.db"):
        try:
            conn = sqlite3.connect("building_energy.db")
            cursor = conn.cursor()
            
            # Count buildings
            cursor.execute("SELECT COUNT(*) FROM buildings")
            building_count = cursor.fetchone()[0]
            
            # Count energy records
            cursor.execute("SELECT COUNT(*) FROM energy_records")
            record_count = cursor.fetchone()[0]
            
            print(f"\n🗄️ Database Statistics:")
            print(f"   • Buildings: {building_count}")
            print(f"   • Energy records: {record_count:,}")
            
            conn.close()
        except:
            print("⚠️ Could not read database statistics")
    
    # Model files
    model_files = list(Path(".").glob("*.joblib"))
    if model_files:
        total_size = sum(f.stat().st_size for f in model_files)
        print(f"\n🧠 Model Statistics:")
        print(f"   • Model files: {len(model_files)}")
        print(f"   • Total size: {total_size / (1024*1024):.1f} MB")

def main():
    """Main utility function."""
    parser = argparse.ArgumentParser(description="Building Energy Optimizer Utility")
    parser.add_argument("action", choices=[
        "clean", "health", "performance", "backup", 
        "update", "stats", "all"
    ], help="Action to perform")
    
    args = parser.parse_args()
    
    print("🛠️ Building Energy Optimizer Utility v2.0")
    
    success = True
    
    if args.action == "clean":
        clean_project()
    elif args.action == "health":
        success = check_project_health()
    elif args.action == "performance":
        success = generate_performance_report()
    elif args.action == "backup":
        backup_models()
    elif args.action == "update":
        success = update_dependencies()
    elif args.action == "stats":
        generate_project_stats()
    elif args.action == "all":
        print("🔄 Running all maintenance tasks...")
        clean_project()
        success &= check_project_health()
        backup_models()
        generate_project_stats()
        success &= generate_performance_report()
    
    if success:
        print("\n🎉 All tasks completed successfully!")
        return 0
    else:
        print("\n⚠️ Some tasks completed with warnings or errors.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
