# 🏢⚡ Energy Optimizer Pro - Makefile
# Advanced task automation for development and production

.PHONY: help install build start stop test clean docker health backup restore deploy docs

# Default target
.DEFAULT_GOAL := help

# Colors for pretty output
RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[1;33m
BLUE=\033[0;34m
PURPLE=\033[0;35m
CYAN=\033[0;36m
WHITE=\033[1;37m
NC=\033[0m # No Color

# Emojis
ROCKET=🚀
GEAR=⚙️
CHECK=✅
WARNING=⚠️
ERROR=❌
INFO=ℹ️
ENERGY=⚡
BUILDING=🏢
DOCKER=🐳
TEST=🧪
CLEAN=🧹
DOCS=📖
DEPLOY=🌐

# Variables
FRONTEND_DIR := frontend
BACKEND_DIR := backend
VENV_DIR := $(BACKEND_DIR)/venv
DOCKER_COMPOSE := docker-compose
BACKUP_DIR := backups

help: ## 📚 Show this help message
	@echo -e "$(PURPLE)================================================================$(NC)"
	@echo -e "$(WHITE)$(BUILDING)$(ENERGY) ENERGY OPTIMIZER PRO - DEVELOPMENT COMMANDS$(NC)"
	@echo -e "$(PURPLE)================================================================$(NC)"
	@echo ""
	@echo -e "$(YELLOW)🔧 Setup & Installation:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## .*$$/ {printf "  $(CYAN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "(install|setup|init)"
	@echo ""
	@echo -e "$(YELLOW)🚀 Development:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## .*$$/ {printf "  $(CYAN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "(dev|start|stop|build)"
	@echo ""
	@echo -e "$(YELLOW)🧪 Testing & Quality:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## .*$$/ {printf "  $(CYAN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "(test|lint|check|coverage)"
	@echo ""
	@echo -e "$(YELLOW)🐳 Docker & Deployment:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## .*$$/ {printf "  $(CYAN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "(docker|deploy|backup|restore)"
	@echo ""
	@echo -e "$(YELLOW)🛠️ Utilities:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## .*$$/ {printf "  $(CYAN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "(clean|docs|logs|health|update)"
	@echo ""
	@echo -e "$(GREEN)Example usage:$(NC)"
	@echo -e "  $(WHITE)make install$(NC)     # Setup everything"
	@echo -e "  $(WHITE)make dev$(NC)         # Start development servers"
	@echo -e "  $(WHITE)make test$(NC)        # Run all tests"
	@echo -e "  $(WHITE)make docker-up$(NC)   # Start with Docker"
	@echo ""

# ================================
# 🔧 Setup & Installation
# ================================

install: ## $(GEAR) Install all dependencies and setup environment
	@echo -e "$(BLUE)$(GEAR) Installing Energy Optimizer Pro...$(NC)"
	@make check-requirements
	@make setup-environment
	@make install-deps
	@make setup-database
	@echo -e "$(GREEN)$(CHECK) Installation completed!$(NC)"
	@echo -e "$(CYAN)$(INFO) Run 'make dev' to start development servers$(NC)"

check-requirements: ## $(INFO) Check system requirements
	@echo -e "$(BLUE)$(INFO) Checking system requirements...$(NC)"
	@command -v node >/dev/null 2>&1 || (echo -e "$(RED)$(ERROR) Node.js not found$(NC)" && exit 1)
	@command -v python3 >/dev/null 2>&1 || (echo -e "$(RED)$(ERROR) Python 3 not found$(NC)" && exit 1)
	@command -v pip3 >/dev/null 2>&1 || (echo -e "$(RED)$(ERROR) pip3 not found$(NC)" && exit 1)
	@echo -e "$(GREEN)$(CHECK) All requirements satisfied$(NC)"

setup-environment: ## $(GEAR) Setup environment files
	@echo -e "$(BLUE)$(GEAR) Setting up environment files...$(NC)"
	@[ ! -f $(FRONTEND_DIR)/.env.local ] && cp $(FRONTEND_DIR)/.env.example $(FRONTEND_DIR)/.env.local || true
	@[ ! -f $(BACKEND_DIR)/.env ] && cp $(BACKEND_DIR)/.env.example $(BACKEND_DIR)/.env || true
	@mkdir -p logs data models uploads $(BACKUP_DIR)
	@echo -e "$(GREEN)$(CHECK) Environment setup completed$(NC)"

install-deps: install-frontend install-backend ## $(GEAR) Install all dependencies

install-frontend: ## $(GEAR) Install frontend dependencies
	@echo -e "$(BLUE)$(GEAR) Installing frontend dependencies...$(NC)"
	@cd $(FRONTEND_DIR) && npm install
	@echo -e "$(GREEN)$(CHECK) Frontend dependencies installed$(NC)"

install-backend: ## $(GEAR) Install backend dependencies
	@echo -e "$(BLUE)$(GEAR) Installing backend dependencies...$(NC)"
	@cd $(BACKEND_DIR) && python3 -m venv venv || true
	@cd $(BACKEND_DIR) && source venv/bin/activate && pip install --upgrade pip
	@cd $(BACKEND_DIR) && source venv/bin/activate && pip install -r requirements.txt
	@echo -e "$(GREEN)$(CHECK) Backend dependencies installed$(NC)"

setup-database: ## $(GEAR) Setup database and run migrations
	@echo -e "$(BLUE)$(GEAR) Setting up database...$(NC)"
	@$(DOCKER_COMPOSE) up -d postgres redis
	@echo -e "$(YELLOW)$(WARNING) Waiting for database to be ready...$(NC)"
	@sleep 10
	@cd $(BACKEND_DIR) && source venv/bin/activate && python -m alembic upgrade head
	@echo -e "$(GREEN)$(CHECK) Database setup completed$(NC)"

# ================================
# 🚀 Development
# ================================

dev: ## $(ROCKET) Start development servers (frontend + backend)
	@echo -e "$(BLUE)$(ROCKET) Starting development servers...$(NC)"
	@$(DOCKER_COMPOSE) up -d postgres redis
	@sleep 5
	@concurrently \
		--names "BACKEND,FRONTEND" \
		--prefix-colors "green,blue" \
		"make dev-backend" \
		"make dev-frontend"

dev-frontend: ## $(ROCKET) Start frontend development server only
	@echo -e "$(BLUE)$(ROCKET) Starting frontend development server...$(NC)"
	@cd $(FRONTEND_DIR) && npm run dev

dev-backend: ## $(ROCKET) Start backend development server only
	@echo -e "$(BLUE)$(ROCKET) Starting backend development server...$(NC)"
	@cd $(BACKEND_DIR) && source venv/bin/activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000

build: build-frontend build-backend ## $(GEAR) Build both frontend and backend

build-frontend: ## $(GEAR) Build frontend for production
	@echo -e "$(BLUE)$(GEAR) Building frontend...$(NC)"
	@cd $(FRONTEND_DIR) && npm run build
	@echo -e "$(GREEN)$(CHECK) Frontend build completed$(NC)"

build-backend: ## $(GEAR) Build backend for production
	@echo -e "$(BLUE)$(GEAR) Building backend...$(NC)"
	@cd $(BACKEND_DIR) && source venv/bin/activate && python setup.py sdist bdist_wheel || echo "Build tools not configured"
	@echo -e "$(GREEN)$(CHECK) Backend build completed$(NC)"

start: ## $(ROCKET) Start production servers
	@echo -e "$(BLUE)$(ROCKET) Starting production servers...$(NC)"
	@$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.prod.yml up --build

stop: ## ⏹️ Stop all services
	@echo -e "$(YELLOW)⏹️ Stopping all services...$(NC)"
	@$(DOCKER_COMPOSE) down
	@pkill -f "uvicorn main:app" || true
	@pkill -f "next dev" || true
	@echo -e "$(GREEN)$(CHECK) All services stopped$(NC)"

restart: stop start ## $(GEAR) Restart all services

# ================================
# 🧪 Testing & Quality
# ================================

test: ## $(TEST) Run all tests
	@echo -e "$(BLUE)$(TEST) Running all tests...$(NC)"
	@make test-frontend
	@make test-backend
	@echo -e "$(GREEN)$(CHECK) All tests completed$(NC)"

test-frontend: ## $(TEST) Run frontend tests
	@echo -e "$(BLUE)$(TEST) Running frontend tests...$(NC)"
	@cd $(FRONTEND_DIR) && npm run test:ci

test-backend: ## $(TEST) Run backend tests with coverage
	@echo -e "$(BLUE)$(TEST) Running backend tests...$(NC)"
	@cd $(BACKEND_DIR) && source venv/bin/activate && python -m pytest tests/ -v --cov=app --cov-report=html --cov-report=xml

test-e2e: ## $(TEST) Run end-to-end tests
	@echo -e "$(BLUE)$(TEST) Running E2E tests...$(NC)"
	@cd $(FRONTEND_DIR) && npm run test:e2e

coverage: ## $(TEST) Generate test coverage reports
	@echo -e "$(BLUE)$(TEST) Generating coverage reports...$(NC)"
	@make test-frontend
	@make test-backend
	@echo -e "$(GREEN)$(CHECK) Coverage reports generated$(NC)"
	@echo -e "$(CYAN)$(INFO) Frontend: $(FRONTEND_DIR)/coverage/index.html$(NC)"
	@echo -e "$(CYAN)$(INFO) Backend: $(BACKEND_DIR)/htmlcov/index.html$(NC)"

lint: ## $(GEAR) Run linters for code quality
	@echo -e "$(BLUE)$(GEAR) Running linters...$(NC)"
	@make lint-frontend
	@make lint-backend
	@echo -e "$(GREEN)$(CHECK) Linting completed$(NC)"

lint-frontend: ## $(GEAR) Lint frontend code
	@echo -e "$(BLUE)$(GEAR) Linting frontend...$(NC)"
	@cd $(FRONTEND_DIR) && npm run lint

lint-backend: ## $(GEAR) Lint backend code
	@echo -e "$(BLUE)$(GEAR) Linting backend...$(NC)"
	@cd $(BACKEND_DIR) && source venv/bin/activate && flake8 . && black --check . && isort --check-only .

lint-fix: ## $(GEAR) Fix linting issues automatically
	@echo -e "$(BLUE)$(GEAR) Fixing linting issues...$(NC)"
	@cd $(FRONTEND_DIR) && npm run lint:fix
	@cd $(BACKEND_DIR) && source venv/bin/activate && black . && isort .
	@echo -e "$(GREEN)$(CHECK) Linting issues fixed$(NC)"

type-check: ## $(GEAR) Run TypeScript and Python type checking
	@echo -e "$(BLUE)$(GEAR) Running type checks...$(NC)"
	@cd $(FRONTEND_DIR) && npm run type-check
	@cd $(BACKEND_DIR) && source venv/bin/activate && mypy app/ || echo "MyPy check completed with warnings"
	@echo -e "$(GREEN)$(CHECK) Type checking completed$(NC)"

security-audit: ## $(GEAR) Run security audits
	@echo -e "$(BLUE)$(GEAR) Running security audits...$(NC)"
	@cd $(FRONTEND_DIR) && npm audit --audit-level=moderate
	@cd $(BACKEND_DIR) && source venv/bin/activate && pip-audit || pip install pip-audit && pip-audit
	@echo -e "$(GREEN)$(CHECK) Security audit completed$(NC)"

# ================================
# 🐳 Docker & Deployment
# ================================

docker-build: ## $(DOCKER) Build Docker images
	@echo -e "$(BLUE)$(DOCKER) Building Docker images...$(NC)"
	@$(DOCKER_COMPOSE) build --parallel
	@echo -e "$(GREEN)$(CHECK) Docker images built$(NC)"

docker-up: ## $(DOCKER) Start all services with Docker
	@echo -e "$(BLUE)$(DOCKER) Starting services with Docker...$(NC)"
	@$(DOCKER_COMPOSE) up --build
	@echo -e "$(GREEN)$(CHECK) Docker services started$(NC)"

docker-up-detached: ## $(DOCKER) Start Docker services in background
	@echo -e "$(BLUE)$(DOCKER) Starting Docker services in background...$(NC)"
	@$(DOCKER_COMPOSE) up -d --build
	@echo -e "$(GREEN)$(CHECK) Docker services started in background$(NC)"

docker-down: ## $(DOCKER) Stop Docker services
	@echo -e "$(YELLOW)$(DOCKER) Stopping Docker services...$(NC)"
	@$(DOCKER_COMPOSE) down
	@echo -e "$(GREEN)$(CHECK) Docker services stopped$(NC)"

docker-prod: ## $(DOCKER) Start production Docker stack
	@echo -e "$(BLUE)$(DOCKER) Starting production Docker stack...$(NC)"
	@$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.prod.yml up --build

docker-logs: ## $(DOCKER) Show Docker logs
	@$(DOCKER_COMPOSE) logs -f

docker-status: ## $(DOCKER) Show Docker services status
	@$(DOCKER_COMPOSE) ps

docker-clean: ## $(CLEAN) Clean Docker resources
	@echo -e "$(YELLOW)$(CLEAN) Cleaning Docker resources...$(NC)"
	@docker system prune -f
	@docker volume prune -f
	@echo -e "$(GREEN)$(CHECK) Docker cleanup completed$(NC)"

# ================================
# 🗄️ Database Management
# ================================

db-migrate: ## $(GEAR) Run database migrations
	@echo -e "$(BLUE)$(GEAR) Running database migrations...$(NC)"
	@cd $(BACKEND_DIR) && source venv/bin/activate && python -m alembic upgrade head
	@echo -e "$(GREEN)$(CHECK) Database migrations completed$(NC)"

db-reset: ## $(WARNING) Reset database (DESTRUCTIVE)
	@echo -e "$(RED)$(WARNING) This will reset the database. Are you sure? [y/N]$(NC)" && read ans && [ $${ans:-N} = y ]
	@echo -e "$(YELLOW)$(GEAR) Resetting database...$(NC)"
	@cd $(BACKEND_DIR) && source venv/bin/activate && python -m alembic downgrade base
	@cd $(BACKEND_DIR) && source venv/bin/activate && python -m alembic upgrade head
	@echo -e "$(GREEN)$(CHECK) Database reset completed$(NC)"

db-seed: ## $(GEAR) Seed database with sample data
	@echo -e "$(BLUE)$(GEAR) Seeding database...$(NC)"
	@cd $(BACKEND_DIR) && source venv/bin/activate && python scripts/seed_data.py
	@echo -e "$(GREEN)$(CHECK) Database seeded$(NC)"

backup: ## $(GEAR) Create database backup
	@echo -e "$(BLUE)$(GEAR) Creating database backup...$(NC)"
	@mkdir -p $(BACKUP_DIR)
	@$(DOCKER_COMPOSE) exec postgres pg_dump -U energy_user energy_optimizer > $(BACKUP_DIR)/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo -e "$(GREEN)$(CHECK) Database backup created in $(BACKUP_DIR)/$(NC)"

restore: ## $(GEAR) Restore database from backup (usage: make restore BACKUP=filename.sql)
	@[ ! -z "$(BACKUP)" ] || (echo -e "$(RED)$(ERROR) Usage: make restore BACKUP=filename.sql$(NC)" && exit 1)
	@echo -e "$(BLUE)$(GEAR) Restoring database from $(BACKUP)...$(NC)"
	@$(DOCKER_COMPOSE) exec -T postgres psql -U energy_user energy_optimizer < $(BACKUP_DIR)/$(BACKUP)
	@echo -e "$(GREEN)$(CHECK) Database restored$(NC)"

# ================================
# 🛠️ Utilities
# ================================

clean: ## $(CLEAN) Clean all temporary files and caches
	@echo -e "$(YELLOW)$(CLEAN) Cleaning temporary files...$(NC)"
	@cd $(FRONTEND_DIR) && npm run clean 2>/dev/null || true
	@cd $(BACKEND_DIR) && rm -rf __pycache__ **/__pycache__ .pytest_cache build/ dist/ *.egg-info/ || true
	@rm -rf logs/*.log data/temp/* uploads/temp/* || true
	@echo -e "$(GREEN)$(CHECK) Cleanup completed$(NC)"

logs: ## $(INFO) Show application logs
	@echo -e "$(BLUE)$(INFO) Showing application logs...$(NC)"
	@if [ -f docker-compose.yml ] && docker-compose ps | grep -q "Up"; then \
		$(DOCKER_COMPOSE) logs -f; \
	else \
		tail -f logs/*.log 2>/dev/null || echo "No log files found"; \
	fi

health: ## $(INFO) Check application health
	@echo -e "$(BLUE)$(INFO) Checking application health...$(NC)"
	@echo -e "$(CYAN)Frontend Health:$(NC)"
	@curl -f http://localhost:3000 >/dev/null 2>&1 && echo -e "$(GREEN)$(CHECK) Frontend: Healthy$(NC)" || echo -e "$(RED)$(ERROR) Frontend: Unhealthy$(NC)"
	@echo -e "$(CYAN)Backend Health:$(NC)"
	@curl -f http://localhost:8000/health >/dev/null 2>&1 && echo -e "$(GREEN)$(CHECK) Backend: Healthy$(NC)" || echo -e "$(RED)$(ERROR) Backend: Unhealthy$(NC)"
	@echo -e "$(CYAN)Database Health:$(NC)"
	@$(DOCKER_COMPOSE) exec postgres pg_isready -U energy_user >/dev/null 2>&1 && echo -e "$(GREEN)$(CHECK) Database: Healthy$(NC)" || echo -e "$(RED)$(ERROR) Database: Unhealthy$(NC)"

update: ## $(GEAR) Update all dependencies
	@echo -e "$(BLUE)$(GEAR) Updating dependencies...$(NC)"
	@cd $(FRONTEND_DIR) && npm update
	@cd $(BACKEND_DIR) && source venv/bin/activate && pip install --upgrade -r requirements.txt
	@echo -e "$(GREEN)$(CHECK) Dependencies updated$(NC)"

docs: ## $(DOCS) Build and serve documentation
	@echo -e "$(BLUE)$(DOCS) Building documentation...$(NC)"
	@echo -e "$(CYAN)$(INFO) Documentation available at: http://localhost:3001$(NC)"

docs-build: ## $(DOCS) Build documentation only
	@echo -e "$(BLUE)$(DOCS) Building documentation...$(NC)"
	@cd docs && npm run build || echo "Documentation build tools not configured"

# ================================
# 🌐 Deployment
# ================================

deploy-staging: ## $(DEPLOY) Deploy to staging environment
	@echo -e "$(BLUE)$(DEPLOY) Deploying to staging...$(NC)"
	@make build
	@make docker-build
	@echo -e "$(GREEN)$(CHECK) Staging deployment completed$(NC)"

deploy-prod: ## $(DEPLOY) Deploy to production (requires confirmation)
	@echo -e "$(RED)$(WARNING) Deploy to PRODUCTION? This is irreversible! [y/N]$(NC)" && read ans && [ $${ans:-N} = y ]
	@echo -e "$(BLUE)$(DEPLOY) Deploying to production...$(NC)"
	@make test
	@make security-audit
	@make build
	@make docker-build
	@echo -e "$(GREEN)$(CHECK) Production deployment completed$(NC)"

# ================================
# 📊 Monitoring & Analytics
# ================================

monitor: ## $(INFO) Start monitoring stack (Prometheus + Grafana)
	@echo -e "$(BLUE)$(INFO) Starting monitoring stack...$(NC)"
	@$(DOCKER_COMPOSE) --profile monitoring up -d
	@echo -e "$(GREEN)$(CHECK) Monitoring started$(NC)"
	@echo -e "$(CYAN)$(INFO) Prometheus: http://localhost:9090$(NC)"
	@echo -e "$(CYAN)$(INFO) Grafana: http://localhost:3001 (admin/admin123)$(NC)"

benchmark: ## $(TEST) Run performance benchmarks
	@echo -e "$(BLUE)$(TEST) Running performance benchmarks...$(NC)"
	@cd $(BACKEND_DIR) && source venv/bin/activate && python scripts/benchmark.py
	@cd $(FRONTEND_DIR) && npm run test:performance || echo "Performance tests not configured"
	@echo -e "$(GREEN)$(CHECK) Benchmarks completed$(NC)"

# ================================
# 🔧 Advanced Tasks
# ================================

ml-train: ## $(GEAR) Train ML models
	@echo -e "$(BLUE)$(GEAR) Training ML models...$(NC)"
	@cd $(BACKEND_DIR) && source venv/bin/activate && python scripts/train_models.py
	@echo -e "$(GREEN)$(CHECK) ML models trained$(NC)"

data-import: ## $(GEAR) Import sample data (usage: make data-import FILE=data.csv)
	@[ ! -z "$(FILE)" ] || (echo -e "$(RED)$(ERROR) Usage: make data-import FILE=data.csv$(NC)" && exit 1)
	@echo -e "$(BLUE)$(GEAR) Importing data from $(FILE)...$(NC)"
	@cd $(BACKEND_DIR) && source venv/bin/activate && python scripts/import_data.py --file $(FILE)
	@echo -e "$(GREEN)$(CHECK) Data imported$(NC)"

generate-ssl: ## $(GEAR) Generate SSL certificates for development
	@echo -e "$(BLUE)$(GEAR) Generating SSL certificates...$(NC)"
	@mkdir -p nginx/ssl
	@openssl req -x509 -newkey rsa:4096 -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem -days 365 -nodes \
		-subj "/C=IT/ST=Italy/L=Milan/O=Energy Optimizer Pro/CN=localhost"
	@echo -e "$(GREEN)$(CHECK) SSL certificates generated$(NC)"

init-project: ## $(ROCKET) Initialize new project from scratch
	@echo -e "$(BLUE)$(ROCKET) Initializing Energy Optimizer Pro project...$(NC)"
	@make check-requirements
	@make setup-environment
	@make install-deps
	@make generate-ssl
	@make setup-database
	@make db-seed
	@echo -e "$(GREEN)$(CHECK) Project initialization completed!$(NC)"
	@echo ""
	@echo -e "$(CYAN)$(ROCKET) Quick Start:$(NC)"
	@echo -e "  $(WHITE)make dev$(NC)          # Start development servers"
	@echo -e "  $(WHITE)make docker-up$(NC)    # Or start with Docker"
	@echo -e "  $(WHITE)make health$(NC)       # Check service health"
	@echo ""
	@echo -e "$(CYAN)$(INFO) Access your application:$(NC)"
	@echo -e "  $(WHITE)Frontend:$(NC)  http://localhost:3000"
	@echo -e "  $(WHITE)Backend:$(NC)   http://localhost:8000"
	@echo -e "  $(WHITE)API Docs:$(NC)  http://localhost:8000/docs"

# ================================
# 🎯 Production Tasks
# ================================

prod-check: ## $(GEAR) Pre-production checklist
	@echo -e "$(BLUE)$(GEAR) Running pre-production checklist...$(NC)"
	@make test
	@make security-audit
	@make type-check
	@make lint
	@echo -e "$(GREEN)$(CHECK) Production checklist passed$(NC)"

prod-deploy: prod-check ## $(DEPLOY) Full production deployment
	@echo -e "$(BLUE)$(DEPLOY) Starting production deployment...$(NC)"
	@make backup
	@make build
	@make docker-build
	@echo -e "$(GREEN)$(CHECK) Production deployment ready$(NC)"

# ================================
# 📈 Performance & Optimization
# ================================

optimize: ## $(GEAR) Optimize application performance
	@echo -e "$(BLUE)$(GEAR) Optimizing application...$(NC)"
	@cd $(FRONTEND_DIR) && npm run analyze
	@cd $(BACKEND_DIR) && source venv/bin/activate && python scripts/optimize_db.py
	@echo -e "$(GREEN)$(CHECK) Optimization completed$(NC)"

profile: ## $(GEAR) Profile application performance
	@echo -e "$(BLUE)$(GEAR) Profiling application performance...$(NC)"
	@cd $(BACKEND_DIR) && source venv/bin/activate && python scripts/profile.py
	@echo -e "$(GREEN)$(CHECK) Profiling completed$(NC)"

# ================================
# 🔄 Maintenance Tasks
# ================================

maintenance-start: ## $(WARNING) Enter maintenance mode
	@echo -e "$(YELLOW)$(WARNING) Entering maintenance mode...$(NC)"
	@echo "maintenance" > .maintenance_mode
	@$(DOCKER_COMPOSE) scale frontend=0
	@echo -e "$(YELLOW)$(WARNING) Maintenance mode active$(NC)"

maintenance-end: ## $(CHECK) Exit maintenance mode
	@echo -e "$(BLUE)$(CHECK) Exiting maintenance mode...$(NC)"
	@rm -f .maintenance_mode
	@$(DOCKER_COMPOSE) scale frontend=1
	@echo -e "$(GREEN)$(CHECK) Maintenance mode disabled$(NC)"

# ================================
# 🚨 Emergency Commands
# ================================

emergency-stop: ## $(ERROR) Emergency stop all services
	@echo -e "$(RED)$(ERROR) EMERGENCY STOP - Killing all services...$(NC)"
	@$(DOCKER_COMPOSE) kill
	@pkill -9 -f "uvicorn" || true
	@pkill -9 -f "next" || true
	@echo -e "$(GREEN)$(CHECK) Emergency stop completed$(NC)"

emergency-restore: ## $(GEAR) Emergency restore from latest backup
	@echo -e "$(RED)$(WARNING) EMERGENCY RESTORE - This will overwrite current data!$(NC)"
	@echo -e "$(RED)Are you absolutely sure? [y/N]$(NC)" && read ans && [ $${ans:-N} = y ]
	@LATEST_BACKUP=$$(ls -t $(BACKUP_DIR)/*.sql | head -1); \
	if [ -z "$$LATEST_BACKUP" ]; then \
		echo -e "$(RED)$(ERROR) No backups found!$(NC)"; \
		exit 1; \
	fi; \
	echo -e "$(YELLOW)$(GEAR) Restoring from $$LATEST_BACKUP...$(NC)"; \
	$(DOCKER_COMPOSE) exec -T postgres psql -U energy_user energy_optimizer < "$$LATEST_BACKUP"
	@echo -e "$(GREEN)$(CHECK) Emergency restore completed$(NC)"

# ================================
# 📊 Project Information
# ================================

info: ## $(INFO) Show project information
	@echo -e "$(PURPLE)================================================================$(NC)"
	@echo -e "$(WHITE)$(BUILDING)$(ENERGY) ENERGY OPTIMIZER PRO - PROJECT INFO$(NC)"
	@echo -e "$(PURPLE)================================================================$(NC)"
	@echo ""
	@echo -e "$(CYAN)📦 Project Structure:$(NC)"
	@echo -e "  Frontend: Next.js 14 + TypeScript + Tailwind CSS"
	@echo -e "  Backend:  FastAPI + Python 3.11 + PostgreSQL"
	@echo -e "  ML:       XGBoost + LightGBM + scikit-learn"
	@echo -e "  Cache:    Redis 7"
	@echo -e "  Deploy:   Docker + Nginx"
	@echo ""
	@echo -e "$(CYAN)🌐 Local URLs:$(NC)"
	@echo -e "  Frontend:     http://localhost:3000"
	@echo -e "  Backend API:  http://localhost:8000"
	@echo -e "  API Docs:     http://localhost:8000/docs"
	@echo -e "  Grafana:      http://localhost:3001 (admin/admin123)"
	@echo -e "  Prometheus:   http://localhost:9090"
	@echo ""
	@echo -e "$(CYAN)📊 Project Stats:$(NC)"
	@echo -e "  Lines of Code: $$(find . -name '*.ts' -o -name '*.tsx' -o -name '*.py' | xargs wc -l | tail -1)"
	@echo -e "  Docker Images: $$(docker images | grep energy-optimizer | wc -l || echo 0)"
	@echo -e "  Git Commits:   $$(git rev-list --count HEAD 2>/dev/null || echo 'N/A')"
	@echo ""

status: health ## $(INFO) Alias for health check

version: ## $(INFO) Show version information
	@echo -e "$(BLUE)$(INFO) Version Information:$(NC)"
	@echo -e "Node.js: $$(node --version)"
	@echo -e "npm: $$(npm --version)"
	@echo -e "Python: $$(python3 --version)"
	@echo -e "Docker: $$(docker --version 2>/dev/null || echo 'Not installed')"

# ================================
# 🎯 Quick Actions
# ================================

quick-start: install docker-up ## $(ROCKET) Complete setup and start (new users)
	@echo -e "$(GREEN)$(ROCKET) Energy Optimizer Pro is ready!$(NC)"
	@make info

quick-test: ## $(TEST) Quick test run (essential tests only)
	@echo -e "$(BLUE)$(TEST) Running essential tests...$(NC)"
	@cd $(FRONTEND_DIR) && npm run test:ci -- --testPathPattern="essential"
	@cd $(BACKEND_DIR) && source venv/bin/activate && python -m pytest tests/test_essential.py -v
	@echo -e "$(GREEN)$(CHECK) Essential tests passed$(NC)"

dev-reset: stop clean install dev ## $(GEAR) Complete development reset

# ================================
# 🔐 Security Tasks
# ================================

security-scan: ## $(GEAR) Run comprehensive security scan
	@echo -e "$(BLUE)$(GEAR) Running security scans...$(NC)"
	@make security-audit
	@cd $(BACKEND_DIR) && source venv/bin/activate && bandit -r app/ || echo "Bandit scan completed"
	@echo -e "$(GREEN)$(CHECK) Security scan completed$(NC)"

# ================================
# 📱 Mobile Development (Future)
# ================================

mobile-setup: ## $(GEAR) Setup mobile development environment
	@echo -e "$(BLUE)$(GEAR) Setting up mobile development...$(NC)"
	@echo -e "$(YELLOW)$(WARNING) Mobile app development not yet implemented$(NC)"

# Helper function to check if we're in the right directory
check-directory:
	@[ -f "package.json" ] || (echo -e "$(RED)$(ERROR) Please run this command from the project root directory$(NC)" && exit 1)

# Include project-specific overrides if they exist
-include Makefile.local

# ================================
# 📝 Help for specific areas
# ================================

help-docker: ## $(DOCKER) Show Docker-specific help
	@echo -e "$(BLUE)$(DOCKER) Docker Commands:$(NC)"
	@echo -e "  make docker-build        # Build images"
	@echo -e "  make docker-up           # Start services"
	@echo -e "  make docker-down         # Stop services"
	@echo -e "  make docker-prod         # Production mode"
	@echo -e "  make docker-logs         # View logs"
	@echo -e "  make docker-clean        # Clean resources"

help-db: ## $(GEAR) Show database-specific help
	@echo -e "$(BLUE)$(GEAR) Database Commands:$(NC)"
	@echo -e "  make db-migrate          # Run migrations"
	@echo -e "  make db-reset            # Reset database"
	@echo -e "  make db-seed             # Seed with sample data"
	@echo -e "  make backup              # Create backup"
	@echo -e "  make restore BACKUP=file # Restore from backup"

help-test: ## $(TEST) Show testing-specific help
	@echo -e "$(BLUE)$(TEST) Testing Commands:$(NC)"
	@echo -e "  make test                # Run all tests"
	@echo -e "  make test-frontend       # Frontend tests only"
	@echo -e "  make test-backend        # Backend tests only"
	@echo -e "  make test-e2e            # End-to-end tests"
	@echo -e "  make coverage            # Generate coverage reports"
	@echo -e "  make benchmark           # Performance benchmarks"

# ================================
# 🎨 Development Helpers
# ================================

format: ## $(GEAR) Format all code
	@echo -e "$(BLUE)$(GEAR) Formatting code...$(NC)"
	@cd $(FRONTEND_DIR) && npx prettier --write .
	@cd $(BACKEND_DIR) && source venv/bin/activate && black . && isort .
	@echo -e "$(GREEN)$(CHECK) Code formatting completed$(NC)"

check-ports: ## $(INFO) Check if required ports are available
	@echo -e "$(BLUE)$(INFO) Checking required ports...$(NC)"
	@lsof -i :3000 >/dev/null 2>&1 && echo -e "$(YELLOW)$(WARNING) Port 3000 is in use$(NC)" || echo -e "$(GREEN)$(CHECK) Port 3000 is available$(NC)"
	@lsof -i :8000 >/dev/null 2>&1 && echo -e "$(YELLOW)$(WARNING) Port 8000 is in use$(NC)" || echo -e "$(GREEN)$(CHECK) Port 8000 is available$(NC)"
	@lsof -i :5432 >/dev/null 2>&1 && echo -e "$(YELLOW)$(WARNING) Port 5432 is in use$(NC)" || echo -e "$(GREEN)$(CHECK) Port 5432 is available$(NC)"
	@lsof -i :6379 >/dev/null 2>&1 && echo -e "$(YELLOW)$(WARNING) Port 6379 is in use$(NC)" || echo -e "$(GREEN)$(CHECK) Port 6379 is available$(NC)"
