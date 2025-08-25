@echo off
setlocal enabledelayedexpansion

REM 🏢⚡ Energy Optimizer Pro - Windows Quick Start Script
REM ======================================================

title Energy Optimizer Pro - Setup and Launch

REM Colors for Windows (using PowerShell for colored output)
set "ESC="

echo.
echo ================================================================
echo    🏢⚡ ENERGY OPTIMIZER PRO - WINDOWS QUICK START
echo ================================================================
echo.

REM Function to print colored messages
:print_message
if "%1"=="info" (
    powershell -Command "Write-Host 'ℹ️  %~2' -ForegroundColor Cyan"
) else if "%1"=="success" (
    powershell -Command "Write-Host '✅ %~2' -ForegroundColor Green"
) else if "%1"=="warning" (
    powershell -Command "Write-Host '⚠️  %~2' -ForegroundColor Yellow"
) else if "%1"=="error" (
    powershell -Command "Write-Host '❌ %~2' -ForegroundColor Red"
) else if "%1"=="process" (
    powershell -Command "Write-Host '⚙️  %~2' -ForegroundColor Blue"
)
goto :eof

REM Check if we're in the right directory
if not exist "package.json" (
    call :print_message "error" "Please run this script from the project root directory"
    pause
    exit /b 1
)

REM Parse command line arguments
set "COMMAND=%1"
if "%COMMAND%"=="" set "COMMAND=help"

REM Main command router
if "%COMMAND%"=="install" goto :install
if "%COMMAND%"=="start" goto :start
if "%COMMAND%"=="stop" goto :stop
if "%COMMAND%"=="status" goto :status
if "%COMMAND%"=="logs" goto :logs
if "%COMMAND%"=="clean" goto :clean
if "%COMMAND%"=="test" goto :test
if "%COMMAND%"=="help" goto :help
goto :help

:install
call :print_message "info" "Installing Energy Optimizer Pro..."
call :check_requirements
if errorlevel 1 exit /b 1

call :setup_environment
call :install_dependencies
call :setup_database

call :print_message "success" "Installation completed successfully!"
call :print_message "info" "Run 'start.bat start' to launch the application"
goto :end

:start
call :print_message "process" "Starting Energy Optimizer Pro..."

echo.
echo Choose deployment method:
echo 1) Docker Compose (Recommended)
echo 2) Local Development
echo 3) Production Docker
echo.
set /p "DEPLOY_CHOICE=Enter your choice (1-3): "

if "%DEPLOY_CHOICE%"=="1" goto :start_docker
if "%DEPLOY_CHOICE%"=="2" goto :start_local
if "%DEPLOY_CHOICE%"=="3" goto :start_production

call :print_message "error" "Invalid choice. Exiting."
goto :end

:start_docker
call :print_message "process" "Starting with Docker Compose..."
docker-compose up --build
goto :end

:start_local
call :print_message "process" "Starting local development servers..."

REM Start backend in new window
call :print_message "process" "Starting FastAPI backend on port 8000..."
start "Energy Optimizer - Backend" cmd /k "cd backend && venv\Scripts\activate && python main.py"

REM Wait for backend to start
timeout /t 5 /nobreak > nul

REM Start frontend in new window  
call :print_message "process" "Starting Next.js frontend on port 3000..."
start "Energy Optimizer - Frontend" cmd /k "cd frontend && npm run dev"

call :print_message "success" "Services started successfully!"
call :print_message "info" "Frontend: http://localhost:3000"
call :print_message "info" "Backend API: http://localhost:8000"
call :print_message "info" "API Docs: http://localhost:8000/docs"

echo.
call :print_message "info" "Press any key to stop all services..."
pause > nul

REM Stop services
taskkill /f /im "python.exe" 2>nul
taskkill /f /im "node.exe" 2>nul
call :print_message "success" "Services stopped"
goto :end

:start_production
call :print_message "process" "Starting production deployment..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build
goto :end

:stop
call :print_message "process" "Stopping all services..."

REM Stop Docker services
docker-compose down 2>nul

REM Stop local processes
taskkill /f /im "python.exe" 2>nul
taskkill /f /im "node.exe" 2>nul

call :print_message "success" "All services stopped"
goto :end

:status
call :print_message "process" "Checking service status..."

REM Check if ports are in use
netstat -an | find ":3000" > nul
if !errorlevel! == 0 (
    call :print_message "success" "Frontend is running on port 3000"
) else (
    call :print_message "warning" "Frontend is not running"
)

netstat -an | find ":8000" > nul
if !errorlevel! == 0 (
    call :print_message "success" "Backend is running on port 8000"
) else (
    call :print_message "warning" "Backend is not running"
)

REM Check Docker services
docker-compose ps 2>nul | find "Up" > nul
if !errorlevel! == 0 (
    call :print_message "success" "Docker services are running"
    docker-compose ps
) else (
    call :print_message "warning" "Docker services are not running"
)
goto :end

:logs
call :print_message "info" "Showing application logs..."

REM Check if Docker is running
docker-compose ps 2>nul | find "Up" > nul
if !errorlevel! == 0 (
    call :print_message "info" "Showing Docker Compose logs..."
    docker-compose logs -f
) else (
    call :print_message "info" "Showing local logs..."
    if exist "logs\*.log" (
        type logs\*.log
    ) else (
        call :print_message "warning" "No log files found"
    )
)
goto :end

:test
call :print_message "process" "Running tests..."

REM Frontend tests
call :print_message "process" "Running frontend tests..."
cd frontend
call npm run test:ci
cd ..

REM Backend tests
call :print_message "process" "Running backend tests..."
cd backend
call venv\Scripts\activate.bat && python -m pytest
cd ..

call :print_message "success" "All tests completed"
goto :end

:clean
call :print_message "process" "Cleaning up..."

REM Stop services first
call :stop

REM Clean Docker
docker system prune -f 2>nul

REM Clean temporary files
if exist "frontend\.next" rmdir /s /q "frontend\.next"
if exist "backend\__pycache__" rmdir /s /q "backend\__pycache__"
del /q logs\*.log 2>nul

call :print_message "success" "Cleanup completed"
goto :end

:check_requirements
call :print_message "info" "Checking system requirements..."

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    call :print_message "error" "Node.js not found. Please install Node.js 18+ from https://nodejs.org"
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('node --version') do (
        call :print_message "success" "Node.js found: %%i"
    )
)

REM Check npm
npm --version >nul 2>&1
if errorlevel 1 (
    call :print_message "error" "npm not found. Please install npm"
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('npm --version') do (
        call :print_message "success" "npm found: v%%i"
    )
)

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    call :print_message "error" "Python not found. Please install Python 3.11+ from https://python.org"
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('python --version') do (
        call :print_message "success" "Python found: %%i"
    )
)

REM Check pip
pip --version >nul 2>&1
if errorlevel 1 (
    call :print_message "error" "pip not found. Please install pip"
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('pip --version') do (
        call :print_message "success" "pip found: %%i"
    )
)

REM Check Docker (optional)
docker --version >nul 2>&1
if errorlevel 1 (
    call :print_message "warning" "Docker not found. Docker deployment will be unavailable"
) else (
    for /f "tokens=*" %%i in ('docker --version') do (
        call :print_message "success" "Docker found: %%i"
    )
)

exit /b 0

:setup_environment
call :print_message "process" "Setting up environment..."

REM Create environment files
if not exist "frontend\.env.local" (
    copy "frontend\.env.example" "frontend\.env.local" >nul
    call :print_message "success" "Frontend .env.local created"
)

if not exist "backend\.env" (
    copy "backend\.env.example" "backend\.env" >nul
    call :print_message "success" "Backend .env created"
)

REM Create required directories
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "models" mkdir models
if not exist "uploads" mkdir uploads
if not exist "backups" mkdir backups

call :print_message "success" "Required directories created"
goto :eof

:install_dependencies
call :print_message "process" "Installing dependencies..."

REM Install frontend dependencies
call :print_message "process" "Installing frontend dependencies..."
cd frontend
call npm install
if errorlevel 1 (
    call :print_message "error" "Frontend dependency installation failed"
    cd ..
    exit /b 1
)
cd ..
call :print_message "success" "Frontend dependencies installed"

REM Install backend dependencies
call :print_message "process" "Installing backend dependencies..."
cd backend

REM Create virtual environment
if not exist "venv" (
    call :print_message "process" "Creating Python virtual environment..."
    python -m venv venv
    call :print_message "success" "Virtual environment created"
)

REM Activate virtual environment and install dependencies
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    call :print_message "error" "Backend dependency installation failed"
    cd ..
    exit /b 1
)
cd ..
call :print_message "success" "Backend dependencies installed"

goto :eof

:setup_database
call :print_message "process" "Setting up database..."

REM Check if Docker is available
docker --version >nul 2>&1
if errorlevel 1 (
    call :print_message "warning" "Docker not available. Please setup PostgreSQL manually:"
    echo   1. Install PostgreSQL 15+
    echo   2. Create database 'energy_optimizer'
    echo   3. Update DATABASE_URL in backend\.env
    echo   4. Run: cd backend ^&^& venv\Scripts\activate ^&^& python -m alembic upgrade head
) else (
    call :print_message "process" "Starting PostgreSQL with Docker..."
    docker-compose up -d postgres redis
    
    REM Wait for database
    call :print_message "process" "Waiting for database to be ready..."
    timeout /t 10 /nobreak > nul
    
    REM Run migrations
    call :print_message "process" "Running database migrations..."
    cd backend
    call venv\Scripts\activate.bat
    python -m alembic upgrade head
    cd ..
    
    call :print_message "success" "Database setup completed with Docker"
)

goto :eof

:help
echo.
echo Usage: start.bat [OPTION]
echo.
echo Options:
echo   install     Install dependencies and setup environment
echo   start       Start the application
echo   stop        Stop all running services
echo   status      Check service status
echo   logs        Show application logs
echo   test        Run tests
echo   clean       Clean up temporary files
echo   help        Show this help message
echo.
echo Examples:
echo   start.bat install    # Setup everything
echo   start.bat start      # Start the application
echo   start.bat logs       # View logs
echo.
goto :end

:end
echo.
call :print_message "info" "Visit the application at: http://localhost:3000"
call :print_message "info" "API documentation: http://localhost:8000/docs"
call :print_message "info" "For help: start.bat help"
echo.
call :print_message "success" "Energy Optimizer Pro is ready! 🏢⚡"
echo.
pause
