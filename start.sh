#!/bin/bash

# 🏢⚡ Energy Optimizer Pro - Main Control Script
# ===============================================
# Universal control script for all operations

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
BACKEND_DIR="$PROJECT_ROOT/backend"

# Logging functions
log() { echo -e "${CYAN}[$(date +'%H:%M:%S')]${NC} $1"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }
info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

# Banner
print_banner() {
    echo -e "${CYAN}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════╗
║                  🏢⚡ ENERGY OPTIMIZER PRO                        ║
║                     Control Center v2.0                         ║
╚══════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        error "Docker is not running"
        echo "Please start Docker and try again"
        exit 1
    fi
}

# Install everything
install() {
    print_banner
    log "🚀 Installing Energy Optimizer Pro..."
    
    # Check prerequisites
    check_docker
    
    # Setup environment
    log "⚙️  Setting up environment..."
    
    # Frontend environment
    if [ ! -f "$FRONTEND_DIR/.env.local" ]; then
        cp "$FRONTEND_DIR/.env.example" "$FRONTEND_DIR/.env.local"
        success "Frontend .env.local created"
    fi
    
    # Backend environment  
    if [ ! -f "$BACKEND_DIR/.env" ]; then
        cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
        success "Backend .env created"
    fi
    
    # Create directories
    mkdir -p logs data/{postgres,redis,grafana,prometheus} backups uploads models
    
    # Install frontend dependencies
    log "📦 Installing frontend dependencies..."
    cd "$FRONTEND_DIR"
    npm install
    cd "$PROJECT_ROOT"
    success "Frontend dependencies installed"
    
    # Setup backend environment
    log "🐍 Setting up Python environment..."
    cd "$BACKEND_DIR"
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        success "Python virtual environment created"
    fi
    
    # Activate and install
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    pip install --upgrade pip
    pip install -r requirements.txt
    cd "$PROJECT_ROOT"
    success "Backend dependencies installed"
    
    # Setup database
    setup_db
    
    success "🎉 Installation completed successfully!"
    echo ""
    echo "Next steps:"
    echo "  1. 🚀 Start services: ./start.sh start"
    echo "  2. 🌐 Open http://localhost:3000"
    echo "  3. 🔑 Login with: admin@energy-optimizer.com / admin123"
}

# Setup database
setup_db() {
    log "🗄️  Setting up database..."
    
    check_docker
    
    # Start database services
    docker-compose up -d postgres redis
    
    # Wait for database
    log "Waiting for database to be ready..."
    for i in {1..30}; do
        if docker-compose exec -T postgres pg_isready -U energy_user >/dev/null 2>&1; then
            break
        fi
        sleep 2
        if [ $i -eq 30 ]; then
            error "Database failed to start"
            exit 1
        fi
    done
    
    # Run migrations
    log "Running database migrations..."
    cd "$BACKEND_DIR"
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    python -m alembic upgrade head
    cd "$PROJECT_ROOT"
    
    # Generate sample data
    log "Generating sample data..."
    cd "$BACKEND_DIR"
    python scripts/seed_data.py --buildings 5 --days 30
    cd "$PROJECT_ROOT"
    
    success "Database setup completed"
}

# Start services
start() {
    print_banner
    log "🚀 Starting Energy Optimizer Pro..."
    
    check_docker
    
    # Start services
    docker-compose up --build -d
    
    # Wait for services
    log "Waiting for services to start..."
    
    # Check frontend
    for i in {1..30}; do
        if curl -s -f http://localhost:3000 >/dev/null 2>&1; then
            success "Frontend is ready"
            break
        fi
        sleep 2
        if [ $i -eq 30 ]; then
            warning "Frontend taking longer than expected"
        fi
    done
    
    # Check backend
    for i in {1..30}; do
        if curl -s -f http://localhost:8000/health >/dev/null 2>&1; then
            success "Backend is ready"
            break
        fi
        sleep 2
        if [ $i -eq 30 ]; then
            warning "Backend taking longer than expected"
        fi
    done
    
    echo ""
    success "🎉 Energy Optimizer Pro is running!"
    echo ""
    echo -e "${CYAN}🌐 Access your application:${NC}"
    echo -e "  🖥️  Dashboard: ${GREEN}http://localhost:3000${NC}"
    echo -e "  🔧 API: ${GREEN}http://localhost:8000${NC}"
    echo -e "  📚 Docs: ${GREEN}http://localhost:8000/docs${NC}"
    echo ""
    echo -e "${CYAN}🔑 Login credentials:${NC}"
    echo -e "  👑 Admin: ${GREEN}admin@energy-optimizer.com / admin123${NC}"
    echo -e "  📊 Analyst: ${GREEN}analyst@energy-optimizer.com / analyst123${NC}"
    echo ""
    echo -e "${CYAN}📊 Useful commands:${NC}"
    echo "  ./start.sh logs     # View logs"
    echo "  ./start.sh status   # Check status"
    echo "  ./start.sh stop     # Stop services"
    echo ""
}

# Stop services
stop() {
    log "🛑 Stopping Energy Optimizer Pro..."
    docker-compose down
    success "All services stopped"
}

# Restart services
restart() {
    log "🔄 Restarting Energy Optimizer Pro..."
    docker-compose restart
    success "All services restarted"
}

# Show status
status() {
    print_banner
    log "📊 Energy Optimizer Pro Status"
    echo ""
    
    # Docker services status
    echo -e "${CYAN}🐳 Docker Services:${NC}"
    docker-compose ps
    echo ""
    
    # Service health checks
    echo -e "${CYAN}🔍 Health Checks:${NC}"
    
    services=(
        "Frontend|http://localhost:3000"
        "Backend API|http://localhost:8000"
        "Health Check|http://localhost:8000/health"
        "API Docs|http://localhost:8000/docs"
        "Grafana|http://localhost:3001"
    )
    
    for service_info in "${services[@]}"; do
        IFS='|' read -r name url <<< "$service_info"
        
        if curl -s -f --max-time 5 "$url" >/dev/null 2>&1; then
            echo -e "  ✅ $name: ${GREEN}OK${NC}"
        else
            echo -e "  ❌ $name: ${RED}DOWN${NC}"
        fi
    done
    echo ""
    
    # Resource usage
    echo -e "${CYAN}💾 Resource Usage:${NC}"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" | head -10
}

# Show logs
logs() {
    local service="${1:-}"
    
    if [ -n "$service" ]; then
        log "📋 Showing logs for $service..."
        docker-compose logs -f "$service"
    else
        log "📋 Showing all service logs..."
        docker-compose logs -f
    fi
}

# Clean up
clean() {
    warning "🧹 This will remove all data and containers!"
    echo -e "${YELLOW}Are you sure? (y/N)${NC}"
    read -r confirm
    
    if [[ $confirm =~ ^[Yy]$ ]]; then
        log "🧹 Cleaning up Energy Optimizer Pro..."
        
        # Stop and remove containers
        docker-compose down -v --remove-orphans
        
        # Remove images
        docker-compose down --rmi all
        
        # Clean build cache
        docker builder prune -f
        
        success "Cleanup completed"
    else
        info "Cleanup cancelled"
    fi
}

# Update system
update() {
    log "🔄 Updating Energy Optimizer Pro..."
    
    # Pull latest changes
    git pull origin main
    
    # Update dependencies
    log "📦 Updating frontend dependencies..."
    cd "$FRONTEND_DIR"
    npm install
    cd "$PROJECT_ROOT"
    
    log "🐍 Updating backend dependencies..."
    cd "$BACKEND_DIR"
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    pip install --upgrade -r requirements.txt
    cd "$PROJECT_ROOT"
    
    # Run migrations
    log "🗄️  Running database migrations..."
    cd "$BACKEND_DIR"
    python -m alembic upgrade head
    cd "$PROJECT_ROOT"
    
    # Rebuild and restart
    docker-compose up --build -d
    
    success "Update completed successfully"
}

# Run tests
test() {
    log "🧪 Running test suite..."
    
    # Frontend tests
    log "Testing frontend..."
    cd "$FRONTEND_DIR"
    npm run test:ci
    cd "$PROJECT_ROOT"
    
    # Backend tests
    log "Testing backend..."
    cd "$BACKEND_DIR"
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    python -m pytest tests/ -v
    cd "$PROJECT_ROOT"
    
    success "All tests passed"
}

# Performance benchmark
benchmark() {
    log "🚀 Running performance benchmarks..."
    
    cd "$BACKEND_DIR"
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    python scripts/benchmark.py benchmark
    cd "$PROJECT_ROOT"
    
    success "Benchmark completed"
}

# Database operations
database() {
    local operation="${1:-}"
    
    case "$operation" in
        "backup")
            log "💾 Creating database backup..."
            timestamp=$(date +"%Y%m%d_%H%M%S")
            mkdir -p backups
            docker-compose exec -T postgres pg_dump -U energy_user energy_optimizer > "backups/backup_$timestamp.sql"
            success "Backup created: backups/backup_$timestamp.sql"
            ;;
        "restore")
            if [ -z "${2:-}" ]; then
                error "Usage: ./start.sh database restore <backup_file>"
                exit 1
            fi
            
            backup_file="$2"
            if [ ! -f "$backup_file" ]; then
                error "Backup file not found: $backup_file"
                exit 1
            fi
            
            warning "This will overwrite the current database!"
            echo -e "${YELLOW}Continue? (y/N)${NC}"
            read -r confirm
            
            if [[ $confirm =~ ^[Yy]$ ]]; then
                log "🔄 Restoring database from $backup_file..."
                docker-compose exec -T postgres psql -U energy_user energy_optimizer < "$backup_file"
                success "Database restored successfully"
            fi
            ;;
        "reset")
            warning "This will delete ALL data!"
            echo -e "${YELLOW}Are you sure? (y/N)${NC}"
            read -r confirm
            
            if [[ $confirm =~ ^[Yy]$ ]]; then
                log "🗄️  Resetting database..."
                docker-compose down postgres
                docker volume rm $(docker volume ls -q | grep postgres) 2>/dev/null || true
                docker-compose up -d postgres
                
                # Wait and setup
                sleep 10
                setup_db
                
                success "Database reset completed"
            fi
            ;;
        *)
            echo "Database operations:"
            echo "  ./start.sh database backup           # Create backup"
            echo "  ./start.sh database restore <file>   # Restore from backup"
            echo "  ./start.sh database reset            # Reset database"
            ;;
    esac
}

# Monitoring
monitoring() {
    local action="${1:-start}"
    
    case "$action" in
        "start")
            log "📊 Starting monitoring stack..."
            docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
            
            # Wait for Grafana
            for i in {1..30}; do
                if curl -s -f http://localhost:3001 >/dev/null 2>&1; then
                    break
                fi
                sleep 2
            done
            
            success "Monitoring stack started"
            echo ""
            echo -e "${CYAN}📊 Monitoring URLs:${NC}"
            echo -e "  🎨 Grafana: ${GREEN}http://localhost:3001${NC} (admin/admin123)"
            echo -e "  📈 Prometheus: ${GREEN}http://localhost:9090${NC}"
            echo -e "  🚨 Alertmanager: ${GREEN}http://localhost:9093${NC}"
            ;;
        "stop")
            log "📊 Stopping monitoring stack..."
            docker-compose -f docker-compose.monitoring.yml down
            success "Monitoring stack stopped"
            ;;
        "restart")
            monitoring stop
            monitoring start
            ;;
        *)
            echo "Monitoring commands:"
            echo "  ./start.sh monitoring start     # Start monitoring"
            echo "  ./start.sh monitoring stop      # Stop monitoring"
            echo "  ./start.sh monitoring restart   # Restart monitoring"
            ;;
    esac
}

# Development utilities
dev() {
    local command="${1:-}"
    
    case "$command" in
        "health")
            python3 scripts/dev-tools.py health
            ;;
        "setup")
            python3 scripts/dev-tools.py setup
            ;;
        "data")
            local buildings="${2:-5}"
            local days="${3:-30}"
            python3 scripts/dev-tools.py generate-data --buildings "$buildings" --days "$days"
            ;;
        "quality")
            python3 scripts/dev-tools.py quality
            ;;
        "stats")
            python3 scripts/dev-tools.py stats
            ;;
        "docs")
            python3 scripts/dev-tools.py docs
            ;;
        *)
            echo "Development commands:"
            echo "  ./start.sh dev health                    # System health check"
            echo "  ./start.sh dev setup                     # Development setup"
            echo "  ./start.sh dev data [buildings] [days]   # Generate sample data"
            echo "  ./start.sh dev quality                   # Code quality check"
            echo "  ./start.sh dev stats                     # Project statistics"
            echo "  ./start.sh dev docs                      # Generate API docs"
            ;;
    esac
}

# Frontend operations
frontend() {
    local command="${1:-}"
    
    cd "$FRONTEND_DIR"
    
    case "$command" in
        "dev")
            log "🎨 Starting frontend development server..."
            npm run dev
            ;;
        "build")
            log "🏗️  Building frontend..."
            npm run build
            success "Frontend build completed"
            ;;
        "test")
            log "🧪 Running frontend tests..."
            npm run test
            ;;
        "lint")
            log "🔍 Linting frontend code..."
            npm run lint
            ;;
        "type-check")
            log "🔍 Checking TypeScript types..."
            npm run type-check
            ;;
        *)
            echo "Frontend commands:"
            echo "  ./start.sh frontend dev         # Development server"
            echo "  ./start.sh frontend build       # Build for production"
            echo "  ./start.sh frontend test        # Run tests"
            echo "  ./start.sh frontend lint        # Lint code"
            echo "  ./start.sh frontend type-check  # TypeScript check"
            ;;
    esac
    
    cd "$PROJECT_ROOT"
}

# Backend operations
backend() {
    local command="${1:-}"
    
    cd "$BACKEND_DIR"
    
    # Activate virtual environment
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    case "$command" in
        "dev")
            log "🐍 Starting backend development server..."
            uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
            ;;
        "test")
            log "🧪 Running backend tests..."
            python -m pytest tests/ -v
            ;;
        "lint")
            log "🔍 Linting backend code..."
            flake8 .
            black --check .
            isort --check-only .
            ;;
        "format")
            log "🎨 Formatting backend code..."
            black .
            isort .
            success "Code formatted"
            ;;
        "migration")
            local message="${2:-Auto migration}"
            log "🗄️  Creating database migration..."
            alembic revision --autogenerate -m "$message"
            success "Migration created"
            ;;
        "migrate")
            log "🗄️  Running database migrations..."
            alembic upgrade head
            success "Migrations completed"
            ;;
        "shell")
            log "🐍 Starting Python shell..."
            python
            ;;
        *)
            echo "Backend commands:"
            echo "  ./start.sh backend dev                    # Development server"
            echo "  ./start.sh backend test                   # Run tests"
            echo "  ./start.sh backend lint                   # Lint code"
            echo "  ./start.sh backend format                 # Format code"
            echo "  ./start.sh backend migration '<message>'  # Create migration"
            echo "  ./start.sh backend migrate                # Run migrations"
            echo "  ./start.sh backend shell                  # Python shell"
            ;;
    esac
    
    cd "$PROJECT_ROOT"
}

# Production operations
production() {
    local command="${1:-}"
    
    case "$command" in
        "deploy")
            log "🚀 Deploying to production..."
            chmod +x scripts/deploy.sh
            scripts/deploy.sh production
            ;;
        "backup")
            log "💾 Creating production backup..."
            timestamp=$(date +"%Y%m%d_%H%M%S")
            mkdir -p backups
            
            # Database backup
            docker-compose exec -T postgres pg_dump -U energy_user energy_optimizer > "backups/prod_backup_$timestamp.sql"
            
            # Application files backup
            tar -czf "backups/app_backup_$timestamp.tar.gz" \
                --exclude='node_modules' \
                --exclude='.next' \
                --exclude='__pycache__' \
                --exclude='venv' \
                --exclude='.git' \
                .
            
            success "Production backup created: backups/prod_backup_$timestamp.*"
            ;;
        "ssl")
            log "🔒 Setting up SSL certificates..."
            if command_exists certbot; then
                sudo certbot --nginx -d energy-optimizer.com
                success "SSL certificates configured"
            else
                error "Certbot not found. Install it first:"
                echo "  Ubuntu/Debian: sudo apt install certbot python3-certbot-nginx"
                echo "  CentOS/RHEL: sudo yum install certbot python3-certbot-nginx"
            fi
            ;;
        *)
            echo "Production commands:"
            echo "  ./start.sh production deploy    # Deploy to production"
            echo "  ./start.sh production backup    # Create production backup"
            echo "  ./start.sh production ssl       # Setup SSL certificates"
            ;;
    esac
}

# Show help
show_help() {
    print_banner
    echo -e "${CYAN}🎯 Energy Optimizer Pro Control Center${NC}"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo -e "${CYAN}🏗️  Setup Commands:${NC}"
    echo "  install              Complete installation and setup"
    echo "  setup-db             Setup database only"
    echo "  update               Update to latest version"
    echo ""
    echo -e "${CYAN}🚀 Service Commands:${NC}"
    echo "  start                Start all services"
    echo "  stop                 Stop all services"
    echo "  restart              Restart all services"
    echo "  status               Show service status"
    echo "  logs [service]       Show logs (all or specific service)"
    echo ""
    echo -e "${CYAN}🧪 Development Commands:${NC}"
    echo "  dev health           System health check"
    echo "  dev setup            Development environment setup"
    echo "  dev data [n] [days]  Generate sample data"
    echo "  dev quality          Code quality check"
    echo "  dev stats            Project statistics"
    echo "  dev docs             Generate API documentation"
    echo ""
    echo -e "${CYAN}🎨 Frontend Commands:${NC}"
    echo "  frontend dev         Start frontend dev server"
    echo "  frontend build       Build frontend"
    echo "  frontend test        Run frontend tests"
    echo "  frontend lint        Lint frontend code"
    echo ""
    echo -e "${CYAN}🐍 Backend Commands:${NC}"
    echo "  backend dev          Start backend dev server"
    echo "  backend test         Run backend tests"
    echo "  backend lint         Lint backend code"
    echo "  backend format       Format backend code"
    echo "  backend migrate      Run database migrations"
    echo "  backend shell        Python shell"
    echo ""
    echo -e "${CYAN}🗄️  Database Commands:${NC}"
    echo "  database backup      Create database backup"
    echo "  database restore     Restore from backup"
    echo "  database reset       Reset database (delete all data)"
    echo ""
    echo -e "${CYAN}📊 Monitoring Commands:${NC}"
    echo "  monitoring start     Start monitoring stack"
    echo "  monitoring stop      Stop monitoring stack"
    echo "  monitoring restart   Restart monitoring"
    echo ""
    echo -e "${CYAN}🚀 Production Commands:${NC}"
    echo "  production deploy    Deploy to production"
    echo "  production backup    Create production backup"
    echo "  production ssl       Setup SSL certificates"
    echo ""
    echo -e "${CYAN}🧪 Testing Commands:${NC}"
    echo "  test                 Run all tests"
    echo "  benchmark            Run performance benchmarks"
    echo ""
    echo -e "${CYAN}🧹 Maintenance Commands:${NC}"
    echo "  clean                Clean up containers and data"
    echo "  reset                Complete reset (clean + setup)"
    echo ""
    echo -e "${CYAN}📖 Information:${NC}"
    echo "  help                 Show this help message"
    echo "  version              Show version information"
    echo ""
    echo -e "${CYAN}🌐 Quick Access URLs:${NC}"
    echo -e "  🖥️  Dashboard: ${GREEN}http://localhost:3000${NC}"
    echo -e "  🔧 API: ${GREEN}http://localhost:8000${NC}"
    echo -e "  📚 Docs: ${GREEN}http://localhost:8000/docs${NC}"
    echo -e "  📊 Grafana: ${GREEN}http://localhost:3001${NC} (admin/admin123)"
    echo ""
    echo -e "${CYAN}🔑 Default Credentials:${NC}"
    echo -e "  👑 Admin: ${GREEN}admin@energy-optimizer.com / admin123${NC}"
    echo -e "  📊 Analyst: ${GREEN}analyst@energy-optimizer.com / analyst123${NC}"
    echo ""
}

# Show version
show_version() {
    local version=$(grep '"version"' package.json 2>/dev/null | sed 's/.*"version": "\([^"]*\)".*/\1/' || echo "unknown")
    echo -e "${CYAN}🏢⚡ Energy Optimizer Pro${NC}"
    echo -e "Version: ${GREEN}$version${NC}"
    echo -e "Build: ${BLUE}$(date +%Y%m%d)${NC}"
    echo ""
}

# Reset everything
reset() {
    warning "🔄 This will completely reset Energy Optimizer Pro!"
    echo -e "${YELLOW}This will delete all data and containers. Continue? (y/N)${NC}"
    read -r confirm
    
    if [[ $confirm =~ ^[Yy]$ ]]; then
        log "🔄 Resetting Energy Optimizer Pro..."
        
        # Clean everything
        clean
        
        # Fresh setup
        setup_db
        
        success "Reset completed successfully"
        echo "Run './start.sh start' to start the application"
    else
        info "Reset cancelled"
    fi
}

# ================================
# 🎯 Main CLI Router
# ================================

case "${1:-help}" in
    "install")
        install
        ;;
    "setup-db")
        setup_db
        ;;
    "start")
        start
        ;;
    "stop")
        stop
        ;;
    "restart")
        restart
        ;;
    "status")
        status
        ;;
    "logs")
        logs "${2:-}"
        ;;
    "update")
        update
        ;;
    "test")
        test
        ;;
    "benchmark")
        benchmark
        ;;
    "clean")
        clean
        ;;
    "reset")
        reset
        ;;
    "dev")
        dev "${2:-}" "${3:-}" "${4:-}"
        ;;
    "frontend")
        frontend "${2:-}"
        ;;
    "backend")
        backend "${2:-}" "${3:-}"
        ;;
    "database")
        database "${2:-}" "${3:-}"
        ;;
    "monitoring")
        monitoring "${2:-}"
        ;;
    "production")
        production "${2:-}"
        ;;
    "version"|"-v"|"--version")
        show_version
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        error "Unknown command: $1"
        echo "Use './start.sh help' for usage information"
        exit 1
        ;;
esac
