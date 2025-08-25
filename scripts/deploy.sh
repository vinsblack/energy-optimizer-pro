#!/bin/bash

# 🏢⚡ Energy Optimizer Pro - Automated Deployment Script
# =======================================================
# Multi-environment deployment with zero-downtime rolling updates

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEPLOYMENT_DIR="/opt/energy-optimizer"
BACKUP_DIR="/opt/backups/energy-optimizer"
LOG_FILE="/var/log/energy-optimizer-deploy.log"

# Deployment configuration
ENVIRONMENTS=("development" "staging" "production")
DOCKER_REGISTRY="ghcr.io/your-username/energy-optimizer-pro"

# Logging functions
log() { 
    echo -e "${CYAN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}
success() { 
    echo -e "${GREEN}✅ $1${NC}" | tee -a "$LOG_FILE"
}
warning() { 
    echo -e "${YELLOW}⚠️  $1${NC}" | tee -a "$LOG_FILE"
}
error() { 
    echo -e "${RED}❌ $1${NC}" | tee -a "$LOG_FILE"
}
info() { 
    echo -e "${BLUE}ℹ️  $1${NC}" | tee -a "$LOG_FILE"
}

# Banner
print_banner() {
    clear
    echo -e "${CYAN}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════╗
║                  🏢⚡ ENERGY OPTIMIZER PRO                        ║
║                    Deployment Manager v2.0                      ║
║                                                                  ║
║                   Zero-Downtime Deployments                     ║
╚══════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Validate environment
validate_environment() {
    local env="$1"
    
    if [[ ! " ${ENVIRONMENTS[@]} " =~ " $env " ]]; then
        error "Invalid environment: $env"
        echo "Valid environments: ${ENVIRONMENTS[*]}"
        exit 1
    fi
    
    log "✅ Environment validated: $env"
}

# Check prerequisites
check_prerequisites() {
    local env="$1"
    
    log "🔍 Checking deployment prerequisites for $env..."
    
    # Check required commands
    local required_commands=("docker" "docker-compose" "git" "curl")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            error "Required command not found: $cmd"
            exit 1
        fi
    done
    
    # Check Docker daemon
    if ! docker info >/dev/null 2>&1; then
        error "Docker daemon is not running"
        exit 1
    fi
    
    # Check disk space (minimum 5GB)
    local available_space=$(df / | awk 'NR==2 {print $4}')
    if [ "$available_space" -lt 5242880 ]; then  # 5GB in KB
        error "Insufficient disk space. Required: 5GB, Available: $(( available_space / 1024 / 1024 ))GB"
        exit 1
    fi
    
    # Environment-specific checks
    case "$env" in
        "production")
            # Check SSL certificates
            if [ ! -f "$PROJECT_ROOT/nginx/ssl/energy-optimizer.com.crt" ]; then
                warning "SSL certificate not found for production"
                echo "Generate with: ./scripts/generate-ssl.sh"
            fi
            
            # Check backup directory
            if [ ! -d "$BACKUP_DIR" ]; then
                sudo mkdir -p "$BACKUP_DIR"
                sudo chown $USER:$USER "$BACKUP_DIR"
            fi
            ;;
        "staging")
            # Check staging configuration
            if [ ! -f "$PROJECT_ROOT/.env.staging" ]; then
                warning "Staging environment file not found"
                echo "Create .env.staging with staging configuration"
            fi
            ;;
    esac
    
    success "Prerequisites check passed"
}

# Create backup
create_backup() {
    local env="$1"
    
    log "💾 Creating backup for $env environment..."
    
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_name="${env}_backup_${timestamp}"
    local backup_path="$BACKUP_DIR/$backup_name"
    
    mkdir -p "$backup_path"
    
    # Database backup
    if docker-compose ps | grep postgres >/dev/null; then
        log "📊 Backing up database..."
        docker-compose exec -T postgres pg_dump -U energy_user energy_optimizer > "$backup_path/database.sql"
        success "Database backup created"
    fi
    
    # Application files backup
    log "📁 Backing up application files..."
    tar -czf "$backup_path/application.tar.gz" \
        --exclude='node_modules' \
        --exclude='.next' \
        --exclude='__pycache__' \
        --exclude='venv' \
        --exclude='.git' \
        --exclude='logs' \
        --exclude='data' \
        -C "$PROJECT_ROOT" .
    
    # Redis backup
    if docker-compose ps | grep redis >/dev/null; then
        log "🔴 Backing up Redis data..."
        docker-compose exec -T redis redis-cli --rdb /data/backup.rdb
        docker cp "$(docker-compose ps -q redis):/data/backup.rdb" "$backup_path/redis.rdb"
        success "Redis backup created"
    fi
    
    # Configuration backup
    log "⚙️ Backing up configuration..."
    cp -r "$PROJECT_ROOT"/.env* "$backup_path/" 2>/dev/null || true
    cp -r "$PROJECT_ROOT"/docker-compose*.yml "$backup_path/"
    
    success "Backup created: $backup_path"
    echo "$backup_path" > "/tmp/energy_optimizer_last_backup"
}

# Test deployment
test_deployment() {
    local env="$1"
    
    log "🧪 Testing $env deployment..."
    
    # Health check URLs based on environment
    local frontend_url
    local backend_url
    
    case "$env" in
        "production")
            frontend_url="https://energy-optimizer.com"
            backend_url="https://api.energy-optimizer.com"
            ;;
        "staging")
            frontend_url="https://staging.energy-optimizer.com"
            backend_url="https://api-staging.energy-optimizer.com"
            ;;
        "development")
            frontend_url="http://localhost:3000"
            backend_url="http://localhost:8000"
            ;;
    esac
    
    # Wait for services to be ready
    log "⏳ Waiting for services to start..."
    
    local max_attempts=60
    local attempt=0
    
    # Backend health check
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -f "$backend_url/health" >/dev/null 2>&1; then
            success "Backend is healthy"
            break
        fi
        
        attempt=$((attempt + 1))
        sleep 5
        
        if [ $attempt -eq $max_attempts ]; then
            error "Backend health check failed after $((max_attempts * 5)) seconds"
            return 1
        fi
    done
    
    # Frontend health check
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -f "$frontend_url" >/dev/null 2>&1; then
            success "Frontend is healthy"
            break
        fi
        
        attempt=$((attempt + 1))
        sleep 5
        
        if [ $attempt -eq $max_attempts ]; then
            error "Frontend health check failed after $((max_attempts * 5)) seconds"
            return 1
        fi
    done
    
    # API functionality tests
    log "🔍 Running API tests..."
    
    # Test authentication
    local auth_response=$(curl -s -X POST "$backend_url/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"email":"admin@energy-optimizer.com","password":"admin123"}' \
        --max-time 10)
    
    if echo "$auth_response" | jq -e '.access_token' >/dev/null 2>&1; then
        success "Authentication test passed"
    else
        error "Authentication test failed"
        return 1
    fi
    
    # Test buildings endpoint
    local token=$(echo "$auth_response" | jq -r '.access_token')
    local buildings_response=$(curl -s -H "Authorization: Bearer $token" \
        "$backend_url/api/buildings" --max-time 10)
    
    if echo "$buildings_response" | jq -e '.[]' >/dev/null 2>&1; then
        success "Buildings API test passed"
    else
        error "Buildings API test failed"
        return 1
    fi
    
    # Database connectivity test
    log "🗄️ Testing database connectivity..."
    if docker-compose exec -T postgres pg_isready -U energy_user >/dev/null 2>&1; then
        success "Database connectivity test passed"
    else
        error "Database connectivity test failed"
        return 1
    fi
    
    # Redis connectivity test
    log "🔴 Testing Redis connectivity..."
    if docker-compose exec -T redis redis-cli ping >/dev/null 2>&1; then
        success "Redis connectivity test passed"
    else
        error "Redis connectivity test failed"
        return 1
    fi
    
    success "All deployment tests passed"
}

# Deploy to environment
deploy() {
    local env="$1"
    local version="${2:-latest}"
    
    print_banner
    log "🚀 Starting deployment to $env environment (version: $version)"
    
    # Validate inputs
    validate_environment "$env"
    check_prerequisites "$env"
    
    # Confirm production deployment
    if [ "$env" = "production" ]; then
        warning "🚨 PRODUCTION DEPLOYMENT"
        echo -e "${YELLOW}This will deploy to production. Continue? (yes/no)${NC}"
        read -r confirm
        if [ "$confirm" != "yes" ]; then
            info "Deployment cancelled"
            exit 0
        fi
    fi
    
    # Create backup
    create_backup "$env"
    
    # Set environment variables
    case "$env" in
        "production")
            export COMPOSE_FILE="docker-compose.yml:docker-compose.prod.yml"
            export COMPOSE_PROJECT_NAME="energy_optimizer_prod"
            ;;
        "staging")
            export COMPOSE_FILE="docker-compose.yml:docker-compose.staging.yml"
            export COMPOSE_PROJECT_NAME="energy_optimizer_staging"
            ;;
        "development")
            export COMPOSE_FILE="docker-compose.yml"
            export COMPOSE_PROJECT_NAME="energy_optimizer_dev"
            ;;
    esac
    
    # Pull latest images
    log "📥 Pulling latest Docker images..."
    docker-compose pull
    
    # Zero-downtime deployment strategy
    if [ "$env" = "production" ]; then
        log "🔄 Performing zero-downtime deployment..."
        
        # Scale up new instances
        docker-compose up -d --scale backend=2 --scale frontend=2 --no-recreate
        sleep 30
        
        # Test new instances
        if test_deployment "$env"; then
            # Remove old instances
            docker-compose up -d --scale backend=1 --scale frontend=1 --remove-orphans
            success "Zero-downtime deployment completed"
        else
            error "New instances failed health check, rolling back..."
            rollback "$env"
            exit 1
        fi
    else
        # Standard deployment for non-production
        log "🔄 Deploying $env environment..."
        docker-compose up -d --build --remove-orphans
    fi
    
    # Run database migrations
    log "🗄️ Running database migrations..."
    docker-compose exec -T backend alembic upgrade head
    
    # Clear cache
    log "🧹 Clearing application cache..."
    docker-compose exec -T redis redis-cli FLUSHDB >/dev/null 2>&1 || true
    
    # Test deployment
    if test_deployment "$env"; then
        success "🎉 Deployment to $env completed successfully!"
        
        # Send notification
        send_notification "$env" "success" "$version"
        
        # Print access information
        print_access_info "$env"
    else
        error "Deployment tests failed"
        
        # Rollback if production
        if [ "$env" = "production" ]; then
            warning "🔄 Rolling back production deployment..."
            rollback "$env"
        fi
        
        send_notification "$env" "failed" "$version"
        exit 1
    fi
}

# Rollback deployment
rollback() {
    local env="$1"
    
    log "🔄 Rolling back $env deployment..."
    
    # Get last backup
    local last_backup
    if [ -f "/tmp/energy_optimizer_last_backup" ]; then
        last_backup=$(cat "/tmp/energy_optimizer_last_backup")
    else
        error "No backup found for rollback"
        exit 1
    fi
    
    if [ ! -d "$last_backup" ]; then
        error "Backup directory not found: $last_backup"
        exit 1
    fi
    
    # Stop current services
    docker-compose down
    
    # Restore database
    if [ -f "$last_backup/database.sql" ]; then
        log "🗄️ Restoring database..."
        docker-compose up -d postgres
        sleep 10
        docker-compose exec -T postgres psql -U energy_user energy_optimizer < "$last_backup/database.sql"
        success "Database restored"
    fi
    
    # Restore Redis
    if [ -f "$last_backup/redis.rdb" ]; then
        log "🔴 Restoring Redis data..."
        docker-compose up -d redis
        sleep 5
        docker cp "$last_backup/redis.rdb" "$(docker-compose ps -q redis):/data/dump.rdb"
        docker-compose restart redis
        success "Redis data restored"
    fi
    
    # Restore application
    log "📁 Restoring application files..."
    tar -xzf "$last_backup/application.tar.gz" -C "$PROJECT_ROOT"
    
    # Start services with previous version
    docker-compose up -d
    
    # Test rollback
    if test_deployment "$env"; then
        success "🔄 Rollback completed successfully"
        send_notification "$env" "rollback" "previous"
    else
        error "Rollback failed - manual intervention required"
        exit 1
    fi
}

# Print access information
print_access_info() {
    local env="$1"
    
    echo ""
    echo -e "${GREEN}================================================================${NC}"
    echo -e "${GREEN}🎉 DEPLOYMENT TO $env COMPLETED SUCCESSFULLY!${NC}"
    echo -e "${GREEN}================================================================${NC}"
    echo ""
    
    case "$env" in
        "production")
            echo -e "${CYAN}🌐 Production URLs:${NC}"
            echo -e "  🖥️  Dashboard: ${GREEN}https://energy-optimizer.com${NC}"
            echo -e "  🔧 API: ${GREEN}https://api.energy-optimizer.com${NC}"
            echo -e "  📚 Documentation: ${GREEN}https://docs.energy-optimizer.com${NC}"
            echo -e "  📊 Monitoring: ${GREEN}https://monitoring.energy-optimizer.com${NC}"
            ;;
        "staging")
            echo -e "${CYAN}🧪 Staging URLs:${NC}"
            echo -e "  🖥️  Dashboard: ${GREEN}https://staging.energy-optimizer.com${NC}"
            echo -e "  🔧 API: ${GREEN}https://api-staging.energy-optimizer.com${NC}"
            echo -e "  📊 Monitoring: ${GREEN}https://monitoring-staging.energy-optimizer.com${NC}"
            ;;
        "development")
            echo -e "${CYAN}🛠️ Development URLs:${NC}"
            echo -e "  🖥️  Dashboard: ${GREEN}http://localhost:3000${NC}"
            echo -e "  🔧 API: ${GREEN}http://localhost:8000${NC}"
            echo -e "  📚 API Docs: ${GREEN}http://localhost:8000/docs${NC}"
            echo -e "  📊 Grafana: ${GREEN}http://localhost:3001${NC}"
            ;;
    esac
    
    echo ""
    echo -e "${CYAN}📊 Useful Commands:${NC}"
    echo "  ./scripts/deploy.sh status $env     # Check deployment status"
    echo "  ./scripts/deploy.sh logs $env       # View deployment logs"
    echo "  ./scripts/deploy.sh monitor $env    # Monitor deployment"
    echo "  ./scripts/deploy.sh rollback $env   # Rollback if needed"
    echo ""
}

# Send deployment notification
send_notification() {
    local env="$1"
    local status="$2"
    local version="$3"
    
    local webhook_url=""
    local message=""
    local color=""
    
    case "$status" in
        "success")
            color="good"
            message="🎉 Deployment to $env completed successfully!"
            ;;
        "failed")
            color="danger"
            message="❌ Deployment to $env failed!"
            ;;
        "rollback")
            color="warning"
            message="🔄 Rollback to $env completed"
            ;;
    esac
    
    # Slack notification (if webhook configured)
    if [ -n "${SLACK_WEBHOOK_URL:-}" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{
                \"text\": \"$message\",
                \"attachments\": [{
                    \"color\": \"$color\",
                    \"fields\": [
                        {\"title\": \"Environment\", \"value\": \"$env\", \"short\": true},
                        {\"title\": \"Version\", \"value\": \"$version\", \"short\": true},
                        {\"title\": \"Timestamp\", \"value\": \"$(date)\", \"short\": true},
                        {\"title\": \"Deployed By\", \"value\": \"$USER\", \"short\": true}
                    ]
                }]
            }" \
            "$SLACK_WEBHOOK_URL" >/dev/null 2>&1 || true
    fi
    
    # Email notification (if configured)
    if command -v mail >/dev/null 2>&1 && [ -n "${EMAIL_RECIPIENTS:-}" ]; then
        echo "$message - Environment: $env, Version: $version, Time: $(date)" | \
            mail -s "Energy Optimizer Pro Deployment - $env" "$EMAIL_RECIPIENTS" || true
    fi
}

# Monitor deployment
monitor() {
    local env="$1"
    
    log "📊 Monitoring $env deployment..."
    
    # Show real-time logs
    echo "📋 Real-time logs (Ctrl+C to exit):"
    docker-compose logs -f --tail=50
}

# Show deployment status
status() {
    local env="$1"
    
    print_banner
    log "📊 $env Deployment Status"
    echo ""
    
    # Service status
    echo -e "${CYAN}🐳 Services Status:${NC}"
    docker-compose ps
    echo ""
    
    # Container health
    echo -e "${CYAN}🔍 Container Health:${NC}"
    docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    
    # Resource usage
    echo -e "${CYAN}💾 Resource Usage:${NC}"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
    echo ""
    
    # Recent logs
    echo -e "${CYAN}📋 Recent Logs (last 20 lines):${NC}"
    docker-compose logs --tail=20
}

# Environment-specific deployment functions
deploy_development() {
    log "🛠️ Deploying to development environment..."
    
    # Use development configuration
    export COMPOSE_FILE="docker-compose.yml"
    export COMPOSE_PROJECT_NAME="energy_optimizer_dev"
    
    # Quick deployment for development
    docker-compose up -d --build
    
    success "Development deployment completed"
}

deploy_staging() {
    log "🧪 Deploying to staging environment..."
    
    # Use staging configuration
    export COMPOSE_FILE="docker-compose.yml:docker-compose.staging.yml"
    export COMPOSE_PROJECT_NAME="energy_optimizer_staging"
    
    # Pull and deploy
    docker-compose pull
    docker-compose up -d --build --remove-orphans
    
    # Run staging-specific tests
    log "🧪 Running staging tests..."
    sleep 30
    test_deployment "staging"
    
    success "Staging deployment completed"
}

deploy_production() {
    log "🏭 Deploying to production environment..."
    
    # Use production configuration  
    export COMPOSE_FILE="docker-compose.yml:docker-compose.prod.yml"
    export COMPOSE_PROJECT_NAME="energy_optimizer_prod"
    
    # Extra production safety checks
    log "🔒 Running production safety checks..."
    
    # Check SSL certificates
    if [ ! -f "nginx/ssl/energy-optimizer.com.crt" ]; then
        error "Production SSL certificate not found"
        exit 1
    fi
    
    # Check production environment variables
    if [ ! -f ".env.production" ]; then
        error "Production environment file not found"
        exit 1
    fi
    
    # Load production environment
    source .env.production
    
    # Validate critical environment variables
    local required_vars=("SECRET_KEY" "DB_PASSWORD" "API_URL")
    for var in "${required_vars[@]}"; do
        if [ -z "${!var:-}" ]; then
            error "Required environment variable not set: $var"
            exit 1
        fi
    done
    
    # Zero-downtime deployment
    log "🔄 Performing zero-downtime production deployment..."
    
    # Pull latest images
    docker-compose pull
    
    # Scale up additional instances
    docker-compose up -d --scale backend=2 --scale frontend=2 --no-recreate
    
    # Wait for new instances to be healthy
    sleep 60
    
    # Test new instances
    if test_deployment "production"; then
        # Scale down to normal capacity
        docker-compose up -d --scale backend=1 --scale frontend=1 --remove-orphans
        
        # Run database migrations
        docker-compose exec -T backend alembic upgrade head
        
        success "Production deployment completed successfully"
    else
        error "Production deployment health check failed"
        rollback "production"
        exit 1
    fi
}

# Health check for specific environment
health_check() {
    local env="$1"
    
    log "🔍 Running comprehensive health check for $env..."
    
    # Set URLs based on environment
    local base_url
    case "$env" in
        "production")
            base_url="https://api.energy-optimizer.com"
            ;;
        "staging") 
            base_url="https://api-staging.energy-optimizer.com"
            ;;
        "development")
            base_url="http://localhost:8000"
            ;;
    esac
    
    # Comprehensive health checks
    local endpoints=(
        "/health:Health Check"
        "/api/buildings:Buildings API"
        "/api/dashboard/metrics:Dashboard Metrics"
        "/auth/health:Authentication"
    )
    
    local failed_checks=0
    
    for endpoint_info in "${endpoints[@]}"; do
        IFS=':' read -r endpoint name <<< "$endpoint_info"
        
        if curl -s -f --max-time 10 "$base_url$endpoint" >/dev/null 2>&1; then
            success "$name: OK"
        else
            error "$name: FAILED"
            failed_checks=$((failed_checks + 1))
        fi
    done
    
    # Overall health status
    if [ $failed_checks -eq 0 ]; then
        success "All health checks passed ✅"
        return 0
    else
        error "$failed_checks health checks failed ❌"
        return 1
    fi
}

# ================================
# 🎯 CLI Interface
# ================================

case "${1:-help}" in
    "deploy")
        if [ $# -lt 2 ]; then
            error "Usage: $0 deploy <environment> [version]"
            echo "Environments: ${ENVIRONMENTS[*]}"
            exit 1
        fi
        deploy "$2" "${3:-latest}"
        ;;
    "rollback")
        if [ $# -lt 2 ]; then
            error "Usage: $0 rollback <environment>"
            exit 1
        fi
        rollback "$2"
        ;;
    "backup")
        if [ $# -lt 2 ]; then
            error "Usage: $0 backup <environment>"
            exit 1
        fi
        create_backup "$2"
        ;;
    "test")
        if [ $# -lt 2 ]; then
            error "Usage: $0 test <environment>"
            exit 1
        fi
        test_deployment "$2"
        ;;
    "status")
        if [ $# -lt 2 ]; then
            error "Usage: $0 status <environment>"
            exit 1
        fi
        status "$2"
        ;;
    "monitor")
        if [ $# -lt 2 ]; then
            error "Usage: $0 monitor <environment>"
            exit 1
        fi
        monitor "$2"
        ;;
    "health")
        if [ $# -lt 2 ]; then
            error "Usage: $0 health <environment>"
            exit 1
        fi
        health_check "$2"
        ;;
    "logs")
        if [ $# -lt 2 ]; then
            error "Usage: $0 logs <environment> [service]"
            exit 1
        fi
        docker-compose logs -f "${3:-}"
        ;;
    "development"|"dev")
        deploy_development
        ;;
    "staging")
        deploy_staging
        ;;
    "production"|"prod")
        deploy_production
        ;;
    "help"|"--help"|"-h")
        print_banner
        echo "🏢⚡ Energy Optimizer Pro - Deployment Manager"
        echo ""
        echo "Usage: $0 [COMMAND] [OPTIONS]"
        echo ""
        echo -e "${CYAN}🚀 Deployment Commands:${NC}"
        echo "  deploy <env> [version]    Deploy to environment"
        echo "  development              Quick deploy to development"
        echo "  staging                  Deploy to staging"
        echo "  production               Deploy to production"
        echo ""
        echo -e "${CYAN}🔧 Management Commands:${NC}"
        echo "  status <env>             Show deployment status"
        echo "  monitor <env>            Monitor deployment logs"
        echo "  test <env>               Test deployment health"
        echo "  health <env>             Comprehensive health check"
        echo "  logs <env> [service]     Show deployment logs"
        echo ""
        echo -e "${CYAN}🔄 Recovery Commands:${NC}"
        echo "  backup <env>             Create deployment backup"
        echo "  rollback <env>           Rollback to previous version"
        echo ""
        echo -e "${CYAN}🌍 Environments:${NC}"
        echo "  development              Local development"
        echo "  staging                  Pre-production testing"
        echo "  production               Live production"
        echo ""
        echo -e "${CYAN}📋 Examples:${NC}"
        echo "  $0 deploy staging v1.2.0     # Deploy version 1.2.0 to staging"
        echo "  $0 production                 # Quick production deployment"
        echo "  $0 status production          # Check production status"
        echo "  $0 rollback production        # Rollback production"
        echo "  $0 health staging             # Health check staging"
        echo ""
        echo -e "${CYAN}⚙️ Configuration:${NC}"
        echo "  Environment variables can be set in:"
        echo "    - .env.development"
        echo "    - .env.staging" 
        echo "    - .env.production"
        echo ""
        echo -e "${CYAN}📞 Support:${NC}"
        echo "  📖 Documentation: https://docs.energy-optimizer.com"
        echo "  🐛 Issues: https://github.com/your-username/energy-optimizer-pro/issues"
        echo "  💬 Discord: https://discord.gg/energy-optimizer"
        echo ""
        ;;
    *)
        error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
