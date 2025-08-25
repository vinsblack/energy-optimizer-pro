#!/usr/bin/env python3
"""
Complete deployment script for Building Energy Optimizer v2.0
"""
import os
import sys
import subprocess
import shutil
import platform
import argparse
from pathlib import Path

def print_banner():
    """Print deployment banner."""
    print("🏢" + "="*60)
    print("  BUILDING ENERGY OPTIMIZER v2.0 - DEPLOYMENT")
    print("="*62)

def check_requirements():
    """Check system requirements."""
    print("\n1️⃣ Checking system requirements...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check pip
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        print("✅ pip available")
    except subprocess.CalledProcessError:
        print("❌ pip not available")
        return False
    
    # Check Docker (optional)
    try:
        subprocess.run(["docker", "--version"], 
                      check=True, capture_output=True)
        print("✅ Docker available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ Docker not available (optional for local development)")
    
    # Check Docker Compose (optional)
    try:
        subprocess.run(["docker-compose", "--version"], 
                      check=True, capture_output=True)
        print("✅ Docker Compose available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ Docker Compose not available (optional)")
    
    return True

def setup_environment():
    """Setup Python environment and dependencies."""
    print("\n2️⃣ Setting up Python environment...")
    
    # Create virtual environment if it doesn't exist
    venv_path = Path("venv")
    if not venv_path.exists():
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created")
    
    # Determine activation script
    if platform.system() == "Windows":
        activate_script = venv_path / "Scripts" / "activate.bat"
        pip_executable = venv_path / "Scripts" / "pip.exe"
        python_executable = venv_path / "Scripts" / "python.exe"
    else:
        activate_script = venv_path / "bin" / "activate"
        pip_executable = venv_path / "bin" / "pip"
        python_executable = venv_path / "bin" / "python"
    
    # Install dependencies
    print("📚 Installing dependencies...")
    try:
        # Upgrade pip first
        subprocess.run([str(python_executable), "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True)
        
        # Install requirements
        subprocess.run([str(pip_executable), "install", "-r", "requirements.txt"], 
                      check=True)
        
        # Install package in development mode
        subprocess.run([str(pip_executable), "install", "-e", ".[all]"], 
                      check=True)
        
        print("✅ Dependencies installed successfully")
        return str(python_executable)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return None

def setup_configuration():
    """Setup configuration files."""
    print("\n3️⃣ Setting up configuration...")
    
    # Copy .env.example to .env if it doesn't exist
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            shutil.copy(".env.example", ".env")
            print("✅ Created .env file from example")
            print("⚠️  Please edit .env file with your API keys and settings")
        else:
            print("❌ .env.example not found")
    else:
        print("✅ .env file already exists")
    
    # Create directories
    directories = ["logs", "models", "data", "reports"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def run_tests(python_executable):
    """Run test suite."""
    print("\n4️⃣ Running test suite...")
    
    try:
        result = subprocess.run([
            python_executable, "-m", "pytest", "tests/", 
            "--tb=short", "-v"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
            return True
        else:
            print("❌ Some tests failed:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False

def generate_sample_data(python_executable):
    """Generate sample data for demonstration."""
    print("\n5️⃣ Generating sample data...")
    
    try:
        # Run the complete demo
        result = subprocess.run([
            python_executable, "scripts/demo_complete.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Sample data generated successfully")
            print("✅ Demonstration completed")
            return True
        else:
            print("❌ Failed to generate sample data:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Failed to run demo: {e}")
        return False

def docker_deployment():
    """Deploy using Docker Compose."""
    print("\n🐳 Docker Deployment Option")
    print("="*40)
    
    if not shutil.which("docker-compose"):
        print("❌ Docker Compose not available")
        return False
    
    print("🔧 Available Docker commands:")
    print("   docker-compose up -d          # Start all services")
    print("   docker-compose up api         # Start only API")
    print("   docker-compose up dashboard   # Start only dashboard")
    print("   docker-compose logs -f        # View logs")
    print("   docker-compose down           # Stop all services")
    
    deploy_choice = input("\n🤔 Deploy with Docker now? (y/N): ").lower()
    
    if deploy_choice == 'y':
        print("🚀 Starting Docker deployment...")
        try:
            subprocess.run(["docker-compose", "up", "-d"], check=True)
            print("✅ Docker services started successfully!")
            print("🌐 API available at: http://localhost:8000")
            print("📊 Dashboard available at: http://localhost:8501")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Docker deployment failed: {e}")
            return False
    
    return True

def local_deployment(python_executable):
    """Deploy locally without Docker."""
    print("\n💻 Local Deployment Option")
    print("="*40)
    
    print("🔧 Available local commands:")
    print(f"   {python_executable} scripts/start_api.py        # Start API server")
    print(f"   {python_executable} scripts/start_dashboard.py  # Start dashboard")
    print(f"   {python_executable} scripts/demo_complete.py    # Run complete demo")
    
    deploy_choice = input("\n🤔 Start local services now? (y/N): ").lower()
    
    if deploy_choice == 'y':
        service_choice = input("Which service? (api/dashboard/both): ").lower()
        
        if service_choice in ['api', 'both']:
            print("🚀 Starting API server...")
            print("📖 API Documentation: http://localhost:8000/docs")
            
        if service_choice in ['dashboard', 'both']:
            print("📊 Starting dashboard...")
            print("🌐 Dashboard: http://localhost:8501")
        
        if service_choice == 'both':
            print("⚠️  Note: Start each service in a separate terminal")
        
        return True
    
    return True

def print_final_instructions():
    """Print final setup instructions."""
    print("\n🎉 Deployment Setup Complete!")
    print("="*40)
    
    print("\n📋 Next Steps:")
    print("   1. Edit .env file with your API keys")
    print("   2. Choose deployment method:")
    print("      🐳 Docker: docker-compose up -d")
    print("      💻 Local: python scripts/start_api.py")
    print("   3. Access the application:")
    print("      🌐 API Docs: http://localhost:8000/docs")
    print("      📊 Dashboard: http://localhost:8501")
    
    print("\n🔗 Important URLs:")
    print("   • API Health: http://localhost:8000/")
    print("   • API Documentation: http://localhost:8000/docs")
    print("   • Interactive API: http://localhost:8000/redoc") 
    print("   • Dashboard: http://localhost:8501")
    
    print("\n📚 Documentation:")
    print("   • README.md - Complete project overview")
    print("   • docs/api/ - API documentation")
    print("   • examples/ - Usage examples")
    
    print("\n🛠 Development Commands:")
    print("   • pytest tests/ - Run test suite")
    print("   • black src/ - Format code")
    print("   • flake8 src/ - Lint code")
    
    print("\n💡 Pro Tips:")
    print("   • Use XGBoost algorithm for best performance")
    print("   • Enable renewable energy in building config for advanced suggestions")
    print("   • Monitor logs/ directory for troubleshooting")
    print("   • Scale with Docker Compose for production")

def main():
    """Main deployment function."""
    parser = argparse.ArgumentParser(description="Deploy Building Energy Optimizer")
    parser.add_argument("--skip-tests", action="store_true", help="Skip test execution")
    parser.add_argument("--docker-only", action="store_true", help="Setup for Docker deployment only")
    parser.add_argument("--local-only", action="store_true", help="Setup for local deployment only")
    
    args = parser.parse_args()
    
    print_banner()
    
    # Check requirements
    if not check_requirements():
        print("\n❌ System requirements not met. Please install required software.")
        return 1
    
    # Setup configuration
    setup_configuration()
    
    python_executable = None
    
    # Setup Python environment (unless Docker only)
    if not args.docker_only:
        python_executable = setup_environment()
        if not python_executable:
            print("\n❌ Failed to setup Python environment")
            return 1
    
    # Run tests (unless skipped or Docker only)
    if not args.skip_tests and not args.docker_only and python_executable:
        if not run_tests(python_executable):
            print("\n⚠️ Tests failed, but continuing deployment...")
    
    # Generate sample data (unless Docker only)
    if not args.docker_only and python_executable:
        generate_sample_data(python_executable)
    
    # Deployment options
    if args.docker_only:
        docker_deployment()
    elif args.local_only:
        if python_executable:
            local_deployment(python_executable)
    else:
        # Show both options
        print("\n🔄 Choose Deployment Method:")
        print("   1. 🐳 Docker (recommended for production)")
        print("   2. 💻 Local (recommended for development)")
        print("   3. ⏭️ Skip deployment (setup only)")
        
        choice = input("\nEnter choice (1/2/3): ").strip()
        
        if choice == "1":
            docker_deployment()
        elif choice == "2" and python_executable:
            local_deployment(python_executable)
        elif choice == "3":
            print("⏭️ Skipping deployment")
        else:
            print("⚠️ Invalid choice or Python not available")
    
    # Final instructions
    print_final_instructions()
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
