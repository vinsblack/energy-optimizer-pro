#!/usr/bin/env python3
"""
Building Energy Optimizer v2.0 - One-Click Installer
Professional installation script for Windows, macOS, and Linux.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
import urllib.request
import zipfile

# Colors for terminal output
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header():
    """Print installation header."""
    print(f"""
{Colors.BLUE}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                Building Energy Optimizer v2.0               ║
║           Professional One-Click Installation                ║
║                                                              ║
║  🏢 ML-Powered Energy Optimization System                   ║
║  ⚡ 91%+ Accuracy • 15-25% Energy Savings                  ║
║  🚀 Production-Ready • Commercial License                   ║
╚══════════════════════════════════════════════════════════════╝
{Colors.END}
    """)

def check_python_version():
    """Check Python version compatibility."""
    version = sys.version_info
    print(f"{Colors.BLUE}🐍 Python Version: {version.major}.{version.minor}.{version.micro}{Colors.END}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"{Colors.RED}❌ ERROR: Python 3.8+ required. You have Python {version.major}.{version.minor}{Colors.END}")
        print(f"{Colors.YELLOW}Please upgrade Python: https://python.org/downloads{Colors.END}")
        sys.exit(1)
    
    print(f"{Colors.GREEN}✅ Python version compatible{Colors.END}")
    return True

def check_pip():
    """Check if pip is available and upgrade if needed."""
    try:
        import pip
        print(f"{Colors.BLUE}📦 Upgrading pip...{Colors.END}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"{Colors.GREEN}✅ pip updated{Colors.END}")
        return True
    except:
        print(f"{Colors.RED}❌ pip not found. Please install pip first.{Colors.END}")
        return False

def create_virtual_environment():
    """Create and activate virtual environment."""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print(f"{Colors.YELLOW}⚠️ Virtual environment exists, removing...{Colors.END}")
        shutil.rmtree(venv_path)
    
    print(f"{Colors.BLUE}🔧 Creating virtual environment...{Colors.END}")
    subprocess.check_call([sys.executable, "-m", "venv", "venv"])
    print(f"{Colors.GREEN}✅ Virtual environment created{Colors.END}")
    
    # Get python executable path
    if platform.system() == "Windows":
        python_exe = venv_path / "Scripts" / "python.exe"
        activate_script = venv_path / "Scripts" / "activate.bat"
    else:
        python_exe = venv_path / "bin" / "python"
        activate_script = venv_path / "bin" / "activate"
    
    return str(python_exe), str(activate_script)

def install_dependencies(python_exe):
    """Install all required dependencies."""
    print(f"{Colors.BLUE}📚 Installing dependencies...{Colors.END}")
    
    # Core requirements
    requirements = [
        "numpy>=1.21.0,<2.0.0",
        "pandas>=1.5.0,<3.0.0",
        "scikit-learn>=1.1.0,<2.0.0",
        "matplotlib>=3.5.0,<4.0.0",
        "seaborn>=0.11.0,<1.0.0",
        "plotly>=5.10.0,<6.0.0",
        "xgboost>=2.0.0,<3.0.0",
        "lightgbm>=4.0.0,<5.0.0",
        "fastapi>=0.100.0,<1.0.0",
        "uvicorn[standard]>=0.18.0,<1.0.0",
        "python-multipart>=0.0.5,<1.0.0",
        "streamlit>=1.28.0,<2.0.0",
        "sqlalchemy>=1.4.0,<3.0.0",
        "python-dotenv>=0.19.0,<2.0.0",
        "click>=8.0.0,<9.0.0",
        "tqdm>=4.64.0,<5.0.0",
        "joblib>=1.2.0,<2.0.0",
        "requests>=2.28.0,<3.0.0",
        "python-jose[cryptography]>=3.3.0,<4.0.0",
        "passlib[bcrypt]>=1.7.0,<2.0.0",
        "psutil>=5.9.0,<6.0.0",
    ]
    
    for i, package in enumerate(requirements, 1):
        print(f"{Colors.BLUE}📦 Installing {package.split('>=')[0]} ({i}/{len(requirements)})...{Colors.END}")
        try:
            subprocess.check_call([python_exe, "-m", "pip", "install", package], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            print(f"{Colors.YELLOW}⚠️ Retrying {package.split('>=')[0]}...{Colors.END}")
            subprocess.check_call([python_exe, "-m", "pip", "install", package.split('>=')[0]])
    
    print(f"{Colors.GREEN}✅ All dependencies installed{Colors.END}")

def install_package(python_exe):
    """Install the Building Energy Optimizer package."""
    print(f"{Colors.BLUE}🏢 Installing Building Energy Optimizer...{Colors.END}")
    
    try:
        # Try installing in development mode
        subprocess.check_call([python_exe, "-m", "pip", "install", "-e", "."])
        print(f"{Colors.GREEN}✅ Building Energy Optimizer installed (development mode){Colors.END}")
    except:
        print(f"{Colors.YELLOW}⚠️ Development install failed, trying alternative...{Colors.END}")
        # Add src to Python path in a simple way
        create_path_helper()

def create_path_helper():
    """Create a simple path helper for imports."""
    path_helper = '''
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
'''
    
    with open('path_helper.py', 'w') as f:
        f.write(path_helper)
    
    print(f"{Colors.GREEN}✅ Import helper created{Colors.END}")

def setup_configuration():
    """Set up configuration files."""
    print(f"{Colors.BLUE}⚙️ Setting up configuration...{Colors.END}")
    
    # Copy .env.example to .env if it exists
    if Path('.env.example').exists() and not Path('.env').exists():
        shutil.copy('.env.example', '.env')
        print(f"{Colors.GREEN}✅ Configuration file (.env) created{Colors.END}")
    
    # Create data directories
    for directory in ['data', 'logs', 'backups', 'models']:
        Path(directory).mkdir(exist_ok=True)
    print(f"{Colors.GREEN}✅ Data directories created{Colors.END}")

def create_startup_scripts(python_exe, activate_script):
    """Create easy startup scripts."""
    print(f"{Colors.BLUE}🚀 Creating startup scripts...{Colors.END}")
    
    # Windows startup script
    if platform.system() == "Windows":
        startup_script = f'''@echo off
echo 🏢 Building Energy Optimizer v2.0
echo ================================
echo.
echo Starting services...
echo.

cd /d "%~dp0"
call "{activate_script}"

echo ✅ Virtual environment activated
echo.

echo Choose an option:
echo 1) Start API Server (http://localhost:8000)
echo 2) Start Dashboard (http://localhost:8501) 
echo 3) Start Both Services
echo 4) Run Demo
echo 5) Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo 🚀 Starting API Server...
    echo 📖 API Documentation: http://localhost:8000/docs
    echo.
    "{python_exe}" -c "import uvicorn; import sys; import os; sys.path.insert(0, 'src'); from api.main import app; uvicorn.run(app, host='0.0.0.0', port=8000)"
)

if "%choice%"=="2" (
    echo.
    echo 📊 Starting Dashboard...
    echo 🌐 Dashboard URL: http://localhost:8501
    echo.
    "{python_exe}" -m streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0
)

if "%choice%"=="3" (
    echo.
    echo 🚀 Starting both API and Dashboard...
    echo 📖 API: http://localhost:8000/docs
    echo 📊 Dashboard: http://localhost:8501
    echo.
    start /b "{python_exe}" -c "import uvicorn; import sys; import os; sys.path.insert(0, 'src'); from api.main import app; uvicorn.run(app, host='0.0.0.0', port=8000)"
    timeout /t 3 /nobreak > nul
    "{python_exe}" -m streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0
)

if "%choice%"=="4" (
    echo.
    echo 🧪 Running Demo...
    "{python_exe}" -c "import sys; sys.path.insert(0, 'src'); import building_energy_optimizer; data = building_energy_optimizer.create_enhanced_example_data('2024-01-01', '2024-01-07'); result = building_energy_optimizer.quick_optimize(data); print(f'Demo: {{result[\"report\"][\"summary\"][\"potential_savings_percent\"]:.1f}}%% savings, {{result[\"training_metrics\"][\"val_r2\"]:.1%%}} accuracy')"
    echo.
    pause
)

if "%choice%"=="5" (
    exit
)

pause
'''
        with open('start.bat', 'w') as f:
            f.write(startup_script)
        
        print(f"{Colors.GREEN}✅ Windows startup script created: start.bat{Colors.END}")
    
    # Unix startup script
    startup_script_unix = f'''#!/bin/bash
echo "🏢 Building Energy Optimizer v2.0"
echo "================================"
echo
echo "Starting services..."
echo

cd "$(dirname "$0")"
source "{activate_script}"

echo "✅ Virtual environment activated"
echo

echo "Choose an option:"
echo "1) Start API Server (http://localhost:8000)"
echo "2) Start Dashboard (http://localhost:8501)"
echo "3) Start Both Services" 
echo "4) Run Demo"
echo "5) Exit"
echo
read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo
        echo "🚀 Starting API Server..."
        echo "📖 API Documentation: http://localhost:8000/docs"
        echo
        "{python_exe}" -c "import uvicorn; import sys; import os; sys.path.insert(0, 'src'); from api.main import app; uvicorn.run(app, host='0.0.0.0', port=8000)"
        ;;
    2)
        echo
        echo "📊 Starting Dashboard..."  
        echo "🌐 Dashboard URL: http://localhost:8501"
        echo
        "{python_exe}" -m streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0
        ;;
    3)
        echo
        echo "🚀 Starting both API and Dashboard..."
        echo "📖 API: http://localhost:8000/docs"
        echo "📊 Dashboard: http://localhost:8501"
        echo
        "{python_exe}" -c "import uvicorn; import sys; import os; sys.path.insert(0, 'src'); from api.main import app; uvicorn.run(app, host='0.0.0.0', port=8000)" &
        sleep 3
        "{python_exe}" -m streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0
        ;;
    4)
        echo
        echo "🧪 Running Demo..."
        "{python_exe}" -c "import sys; sys.path.insert(0, 'src'); import building_energy_optimizer; data = building_energy_optimizer.create_enhanced_example_data('2024-01-01', '2024-01-07'); result = building_energy_optimizer.quick_optimize(data); print(f'Demo: {{result[\"report\"][\"summary\"][\"potential_savings_percent\"]:.1f}}%% savings, {{result[\"training_metrics\"][\"val_r2\"]:.1%%}} accuracy')"
        echo
        read -p "Press Enter to continue..."
        ;;
    5)
        exit 0
        ;;
esac
'''
    
    with open('start.sh', 'w') as f:
        f.write(startup_script_unix)
    
    # Make executable on Unix systems
    if platform.system() != "Windows":
        os.chmod('start.sh', 0o755)
        print(f"{Colors.GREEN}✅ Unix startup script created: start.sh{Colors.END}")

def run_demo(python_exe):
    """Run a quick demo to verify installation."""
    print(f"{Colors.BLUE}🧪 Running installation test...{Colors.END}")
    
    test_script = '''
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import building_energy_optimizer
    print("✅ Core module imported")
    
    data = building_energy_optimizer.create_enhanced_example_data('2024-01-01', '2024-01-03')
    print(f"✅ Generated {len(data)} data points")
    
    result = building_energy_optimizer.quick_optimize(data, algorithm='random_forest')
    savings = result['report']['summary']['potential_savings_percent']
    accuracy = result['training_metrics']['val_r2']
    
    print(f"✅ Optimization complete: {savings:.1f}% savings, {accuracy:.1%} accuracy")
    print("🎉 Installation test PASSED!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    exit(1)
'''
    
    with open('test_install.py', 'w') as f:
        f.write(test_script)
    
    try:
        subprocess.check_call([python_exe, 'test_install.py'])
        print(f"{Colors.GREEN}✅ Installation test completed successfully{Colors.END}")
        os.remove('test_install.py')
    except subprocess.CalledProcessError:
        print(f"{Colors.RED}❌ Installation test failed{Colors.END}")
        return False
    
    return True

def print_success_message():
    """Print success message with next steps."""
    print(f"""
{Colors.GREEN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                🎉 INSTALLATION SUCCESSFUL! 🎉               ║
║                                                              ║
║  Building Energy Optimizer v2.0 is ready to use!           ║
╚══════════════════════════════════════════════════════════════╝
{Colors.END}

{Colors.BLUE}{Colors.BOLD}🚀 QUICK START:{Colors.END}
""")
    
    if platform.system() == "Windows":
        print(f"{Colors.GREEN}  • Double-click: {Colors.BOLD}start.bat{Colors.END}")
        print(f"{Colors.GREEN}  • Or run: {Colors.BOLD}start.bat{Colors.END}")
    else:
        print(f"{Colors.GREEN}  • Run: {Colors.BOLD}./start.sh{Colors.END}")
        print(f"{Colors.GREEN}  • Or: {Colors.BOLD}bash start.sh{Colors.END}")
    
    print(f"""
{Colors.BLUE}{Colors.BOLD}🌐 ACCESS POINTS:{Colors.END}
{Colors.GREEN}  • 📊 Dashboard: http://localhost:8501{Colors.END}
{Colors.GREEN}  • 📖 API Docs:  http://localhost:8000/docs{Colors.END}
{Colors.GREEN}  • 🔍 Health:    http://localhost:8000/{Colors.END}

{Colors.BLUE}{Colors.BOLD}📚 FEATURES:{Colors.END}
{Colors.GREEN}  • ⚡ 91%+ ML Accuracy{Colors.END}
{Colors.GREEN}  • 💰 15-25% Energy Savings{Colors.END}
{Colors.GREEN}  • 🤖 3 AI Algorithms{Colors.END}
{Colors.GREEN}  • 📊 Interactive Dashboard{Colors.END}
{Colors.GREEN}  • 📡 REST API{Colors.END}
{Colors.GREEN}  • 🏢 Commercial Ready{Colors.END}

{Colors.YELLOW}⭐ Star us on GitHub: https://github.com/VincentGallo77/building-energy-optimizer{Colors.END}
{Colors.YELLOW}💬 Support: vincenzo.gallo77@hotmail.com{Colors.END}
""")

def main():
    """Main installation process."""
    print_header()
    
    print(f"{Colors.BLUE}🔍 System Check...{Colors.END}")
    print(f"{Colors.BLUE}💻 OS: {platform.system()} {platform.release()}{Colors.END}")
    
    if not check_python_version():
        return False
    
    if not check_pip():
        return False
    
    try:
        python_exe, activate_script = create_virtual_environment()
        install_dependencies(python_exe)
        install_package(python_exe)
        setup_configuration()
        create_startup_scripts(python_exe, activate_script)
        
        if run_demo(python_exe):
            print_success_message()
            return True
        else:
            print(f"{Colors.RED}❌ Installation verification failed{Colors.END}")
            return False
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️ Installation cancelled by user{Colors.END}")
        return False
    except Exception as e:
        print(f"\n{Colors.RED}❌ Installation failed: {e}{Colors.END}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
