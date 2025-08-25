#!/bin/bash

# 🏢⚡ Energy Optimizer Pro - Automatic Installation Script
# =========================================================
# One-command setup for Energy Optimizer Pro

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
REPO_URL="https://github.com/your-username/energy-optimizer-pro.git"
INSTALL_DIR="${HOME}/energy-optimizer-pro"
PYTHON_MIN_VERSION="3.11"
NODE_MIN_VERSION="18"

# Logging functions
log() { echo -e "${CYAN}[$(date +'%H:%M:%S')]${NC} $1"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }
info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

# Banner
print_banner() {
    clear
    echo -e "${CYAN}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════╗
║                  🏢⚡ ENERGY OPTIMIZER PRO                        ║
║                      Installation Script v2.0                   ║
║                                                                  ║
║              Transform your buildings with AI!                  ║
╚══════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    echo "🎯 One-command setup for the ultimate energy optimization platform"
    echo "📊 Expected installation time: 5-10 minutes"
    echo ""
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Version comparison
version_compare() {
    printf '%s\n%s\n' "$2" "$1" | sort -V -C
}

# Check system requirements
check_requirements() {
    log "Checking system requirements..."
    
    local missing_deps=()
    local warnings=()
    
    # Operating system check
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        info "✓ Linux detected"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        info "✓ macOS detected"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        info "✓ Windows detected (using Git Bash/WSL)"
    else
        warnings+=("Unsupported OS: $OSTYPE")
    fi
    
    # Git check
    if command_exists git; then
        local git_version=$(git --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
        info "✓ Git $git_version"
    else
        missing_deps+=("git")
    fi
    
    # Docker check
    if command_exists docker; then
        local docker_version=$(docker --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
        info "✓ Docker $docker_version"
        
        # Check if Docker daemon is running
        if ! docker info >/dev/null 2>&1; then
            warnings+=("Docker daemon is not running")
        fi
    else
        missing_deps+=("docker")
    fi
    
    # Docker Compose check
    if command_exists docker-compose; then
        local compose_version=$(docker-compose --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
        info "✓ Docker Compose $compose_version"
    else
        missing_deps+=("docker-compose")
    fi
    
    # Node.js check
    if command_exists node; then
        local node_version=$(node --version | sed 's/v//')
        if version_compare "$node_version" "$NODE_MIN_VERSION.0"; then
            info "✓ Node.js $node_version"
        else
            warnings+=("Node.js $node_version detected, but $NODE_MIN_VERSION+ recommended")
        fi
    else
        missing_deps+=("node")
    fi
    
    # npm check
    if command_exists npm; then
        local npm_version=$(npm --version)
        info "✓ npm $npm_version"
    else
        missing_deps+=("npm")
    fi
    
    # Python check
    if command_exists python3; then
        local python_version=$(python3 --version | grep -oE '[0-9]+\.[0-9]+')
        if version_compare "$python_version" "$PYTHON_MIN_VERSION"; then
            info "✓ Python $python_version"
        else
            warnings+=("Python $python_version detected, but $PYTHON_MIN_VERSION+ recommended")
        fi
    else
        missing_deps+=("python3")
    fi
    
    # pip check
    if command_exists pip3; then
        local pip_version=$(pip3 --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
        info "✓ pip $pip_version"
    else
        missing_deps+=("pip3")
    fi
    
    # Display warnings
    if [ ${#warnings[@]} -gt 0 ]; then
        warning "Warnings found:"
        for warn in "${warnings[@]}"; do
            echo "  ⚠️  $warn"
        done
        echo ""
    fi
    
    # Handle missing dependencies
    if [ ${#missing_deps[@]} -gt 0 ]; then
        error "Missing required dependencies:"
        for dep in "${missing_deps[@]}"; do
            echo "  ❌ $dep"
        done
        echo ""
        
        # Offer to install dependencies
        install_dependencies "${missing_deps[@]}"
        return 1
    fi
    
    success "All requirements met!"
    return 0
}

# Install missing dependencies
install_dependencies() {
    local deps=("$@")
    
    echo -e "${YELLOW}Would you like to install missing dependencies automatically? (y/N)${NC}"
    read -r install_deps
    
    if [[ $install_deps =~ ^[Yy]$ ]]; then
        log "Installing dependencies..."
        
        # Detect package manager and install
        if command_exists apt-get; then
            # Ubuntu/Debian
            sudo apt-get update
            for dep in "${deps[@]}"; do
                case $dep in
                    "docker")
                        sudo apt-get install -y docker.io docker-compose
                        sudo systemctl start docker
                        sudo systemctl enable docker
                        sudo usermod -aG docker $USER
                        ;;
                    "node")
                        curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
                        sudo apt-get install -y nodejs
                        ;;
                    "python3")
                        sudo apt-get install -y python3 python3-pip python3-venv
                        ;;
                    "git")
                        sudo apt-get install -y git
                        ;;
                esac
            done
        elif command_exists brew; then
            # macOS with Homebrew
            for dep in "${deps[@]}"; do
                case $dep in
                    "docker")
                        brew install --cask docker
                        ;;
                    "node")
                        brew install node@18
                        ;;
                    "python3")
                        brew install python@3.11
                        ;;
                    "git")
                        brew install git
                        ;;
                esac
            done
        elif command_exists yum; then
            # CentOS/RHEL
            for dep in "${deps[@]}"; do
                case $dep in
                    "docker")
                        sudo yum install -y docker docker-compose
                        sudo systemctl start docker
                        sudo systemctl enable docker
                        ;;
                    "node")
                        curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash -
                        sudo yum install -y nodejs
                        ;;
                    "python3")
                        sudo yum install -y python3 python3-pip
                        ;;
                    "git")
                        sudo yum install -y git
                        ;;
                esac
            done
        else
            error "Automatic installation not supported for your system"
            error "Please install the following manually:"
            for dep in "${deps[@]}"; do
                echo "  - $dep"
            done
            echo ""
            echo "Installation guides:"
            echo "  🐳 Docker: https://docs.docker.com/get-docker/"
            echo "  📦 Node.js: https://nodejs.org/"
            echo "  🐍 Python: https://python.org/"
            exit 1
        fi
        
        success "Dependencies installed!"
        warning "Please log out and back in for Docker permissions to take effect"
        echo "Then run this script again."
        exit 0
    else
        error "Cannot continue without required dependencies"
        exit 1
    fi
}

# Clone repository
clone_repository() {
    log "Cloning Energy Optimizer Pro repository..."
    
    if [ -d "$INSTALL_DIR" ]; then
        warning "Installation directory already exists: $INSTALL_DIR"
        echo -e "${YELLOW}Remove existing installation? (y/N)${NC}"
        read -r remove_existing
        
        if [[ $remove_existing =~ ^[Yy]$ ]]; then
            rm -rf "$INSTALL_DIR"
            success "Existing installation removed"
        else
            error "Installation cancelled"
            exit 1
        fi
    fi
    
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    success "Repository cloned successfully"
}

# Setup environment
setup_environment() {
    log "Setting up development environment..."
    
    # Make scripts executable
    chmod +x scripts/*.sh
    chmod +x start.sh
    
    # Setup environment files
    if [ ! -f "frontend/.env.local" ]; then
        cp frontend/.env.example frontend/.env.local
        success "Frontend environment file created"
    fi
    
    if [ ! -f "backend/.env" ]; then
        cp backend/.env.example backend/.env
        success "Backend environment file created"
    fi
    
    # Create required directories
    mkdir -p logs data/{postgres,redis,grafana,prometheus} backups uploads models
    
    success "Environment setup completed"
}

# Install dependencies
install_project_dependencies() {
    log "Installing project dependencies..."
    
    # Frontend dependencies
    log "Installing frontend dependencies (this may take a few minutes)..."
    cd frontend
    npm install
    cd ..
    success "Frontend dependencies installed"
    
    # Backend dependencies
    log "Setting up Python virtual environment..."
    cd backend
    python3 -m venv venv
    
    # Activate virtual environment and install dependencies
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        # Windows
        source venv/Scripts/activate
    else
        # Unix-like
        source venv/bin/activate
    fi
    
    pip install --upgrade pip
    pip install -r requirements.txt
    cd ..
    
    success "Backend dependencies installed"
}

# Setup database
setup_database() {
    log "Setting up database..."
    
    # Start database services
    docker-compose up -d postgres redis
    
    # Wait for database to be ready
    log "Waiting for database to be ready..."
    for i in {1..30}; do
        if docker-compose exec -T postgres pg_isready -U energy_user >/dev/null 2>&1; then
            break
        fi
        sleep 2
        if [ $i -eq 30 ]; then
            error "Database failed to start within 60 seconds"
            exit 1
        fi
    done
    
    # Run migrations
    log "Running database migrations..."
    cd backend
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    python -m alembic upgrade head
    cd ..
    
    success "Database setup completed"
}

# Generate sample data
generate_sample_data() {
    log "Generating sample data..."
    
    cd backend
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    python scripts/seed_data.py --buildings 5 --days 30
    cd ..
    
    success "Sample data generated"
}

# Test installation
test_installation() {
    log "Testing installation..."
    
    # Build frontend
    log "Building frontend..."
    cd frontend
    npm run build
    cd ..
    
    # Test backend
    log "Testing backend..."
    cd backend
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    python -c "from app.main import app; print('Backend imports successful')"
    cd ..
    
    success "Installation tests passed"
}

# Start services
start_services() {
    log "Starting Energy Optimizer Pro services..."
    
    # Start all services
    docker-compose up --build -d
    
    # Wait for services to be ready
    log "Waiting for services to start..."
    
    for i in {1..60}; do
        if curl -s -f http://localhost:8000/health >/dev/null 2>&1; then
            break
        fi
        sleep 2
        if [ $i -eq 60 ]; then
            error "Services failed to start within 120 seconds"
            echo "Check logs with: docker-compose logs"
            exit 1
        fi
    done
    
    success "All services started successfully"
}

# Print success message
print_success() {
    echo ""
    echo -e "${GREEN}================================================================${NC}"
    echo -e "${GREEN}🎉 ENERGY OPTIMIZER PRO INSTALLATION COMPLETED!${NC}"
    echo -e "${GREEN}================================================================${NC}"
    echo ""
    echo -e "${CYAN}🌐 Your Energy Optimizer Pro is ready at:${NC}"
    echo ""
    echo -e "${BLUE}  🖥️  Frontend Dashboard: ${GREEN}http://localhost:3000${NC}"
    echo -e "${BLUE}  🔧 Backend API: ${GREEN}http://localhost:8000${NC}"
    echo -e "${BLUE}  📚 API Documentation: ${GREEN}http://localhost:8000/docs${NC}"
    echo -e "${BLUE}  📊 Monitoring (Grafana): ${GREEN}http://localhost:3001${NC}"
    echo ""
    echo -e "${CYAN}🔑 Test Credentials:${NC}"
    echo -e "${BLUE}  👑 Admin: ${GREEN}admin@energy-optimizer.com / admin123${NC}"
    echo -e "${BLUE}  📊 Analyst: ${GREEN}analyst@energy-optimizer.com / analyst123${NC}"
    echo -e "${BLUE}  👥 Manager: ${GREEN}manager@energy-optimizer.com / manager123${NC}"
    echo ""
    echo -e "${CYAN}🚀 Next Steps:${NC}"
    echo "  1. 🌐 Open your browser to http://localhost:3000"
    echo "  2. 🔑 Login with the admin credentials above"
    echo "  3. 🏢 Add your first building to start optimizing"
    echo "  4. 📊 Explore the sample data and analytics"
    echo "  5. 🤖 Run your first AI optimization"
    echo ""
    echo -e "${CYAN}📚 Useful Commands:${NC}"
    echo "  ./start.sh status    # Check service status"
    echo "  ./start.sh logs      # View service logs"
    echo "  ./start.sh stop      # Stop all services"
    echo "  ./start.sh restart   # Restart services"
    echo ""
    echo -e "${CYAN}📖 Documentation:${NC}"
    echo "  📋 User Guide: docs/user-guide.md"
    echo "  🔧 Admin Guide: docs/admin-guide.md"
    echo "  🤖 ML Guide: docs/machine-learning.md"
    echo "  🔌 API Reference: http://localhost:8000/docs"
    echo ""
    echo -e "${GREEN}🏢⚡ Start optimizing your buildings today!${NC}"
    echo ""
}

# Error handler
handle_error() {
    local exit_code=$?
    echo ""
    error "Installation failed with exit code $exit_code"
    echo ""
    echo -e "${CYAN}📞 Getting Help:${NC}"
    echo "  📖 Documentation: https://docs.energy-optimizer.com"
    echo "  🐛 Issues: https://github.com/your-username/energy-optimizer-pro/issues"
    echo "  💬 Discord: https://discord.gg/energy-optimizer"
    echo "  📧 Email: support@energy-optimizer.com"
    echo ""
    echo -e "${CYAN}🔍 Debugging:${NC}"
    echo "  ./start.sh logs      # Check service logs"
    echo "  docker-compose ps    # Check container status"
    echo "  docker-compose logs  # View detailed logs"
    exit $exit_code
}

# Cleanup on exit
cleanup_on_exit() {
    echo ""
    warning "Installation interrupted"
    log "Cleaning up..."
    
    # Stop any running services
    if [ -d "$INSTALL_DIR" ]; then
        cd "$INSTALL_DIR"
        docker-compose down 2>/dev/null || true
    fi
    
    exit 1
}

# Main installation function
main_install() {
    print_banner
    
    # Set error handlers
    trap handle_error ERR
    trap cleanup_on_exit INT TERM
    
    # Installation steps
    log "🚀 Starting Energy Optimizer Pro installation..."
    echo ""
    
    # Step 1: Check requirements
    echo -e "${CYAN}📋 Step 1/7: Checking system requirements...${NC}"
    if ! check_requirements; then
        exit 1
    fi
    echo ""
    
    # Step 2: Clone repository
    echo -e "${CYAN}📥 Step 2/7: Downloading Energy Optimizer Pro...${NC}"
    clone_repository
    echo ""
    
    # Step 3: Setup environment
    echo -e "${CYAN}⚙️  Step 3/7: Setting up environment...${NC}"
    setup_environment
    echo ""
    
    # Step 4: Install dependencies
    echo -e "${CYAN}📦 Step 4/7: Installing dependencies...${NC}"
    install_project_dependencies
    echo ""
    
    # Step 5: Setup database
    echo -e "${CYAN}🗄️  Step 5/7: Setting up database...${NC}"
    setup_database
    echo ""
    
    # Step 6: Generate sample data
    echo -e "${CYAN}📊 Step 6/7: Generating sample data...${NC}"
    generate_sample_data
    echo ""
    
    # Step 7: Test and start
    echo -e "${CYAN}🧪 Step 7/7: Testing and starting services...${NC}"
    test_installation
    start_services
    echo ""
    
    # Success message
    print_success
}

# ================================
# 🎯 CLI Interface
# ================================

case "${1:-install}" in
    "install")
        main_install
        ;;
    "check")
        print_banner
        check_requirements
        ;;
    "help"|"--help"|"-h")
        echo "🏢⚡ Energy Optimizer Pro - Installation Script"
        echo ""
        echo "Usage: $0 [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  install    Complete installation (default)"
        echo "  check      Check system requirements only"
        echo "  help       Show this help message"
        echo ""
        echo "Examples:"
        echo "  curl -fsSL https://install.energy-optimizer.com | bash"
        echo "  bash install.sh install"
        echo "  bash install.sh check"
        echo ""
        echo "🌐 For more information, visit:"
        echo "  https://docs.energy-optimizer.com"
        echo ""
        ;;
    *)
        error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
