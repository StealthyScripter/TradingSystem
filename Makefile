# Makefile

# Investment Portfolio MVP - Docker Management
# Usage: make [target]

.PHONY: help build start stop restart clean logs status init test

# Default target
.DEFAULT_GOAL := help

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Docker compose command (check if docker compose or docker-compose is available)
DOCKER_COMPOSE := $(shell which docker-compose 2>/dev/null || echo "docker compose")

help: ## Show this help message
	@echo "$(BLUE)Investment Portfolio MVP - Docker Management$(NC)"
	@echo "$(BLUE)================================================$(NC)"
	@echo ""
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""
	@echo "Examples:"
	@echo "  make start          # Start all services"
	@echo "  make logs           # View logs from all services"
	@echo "  make status         # Check service status"

build: ## Build all Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	$(DOCKER_COMPOSE) build --parallel
	@echo "$(GREEN)✅ Build completed$(NC)"

start: ## Start all services
	@echo "$(BLUE)Starting all services...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@sleep 5
	@echo "$(GREEN)✅ Services started$(NC)"
	@make status

stop: ## Stop all services
	@echo "$(YELLOW)Stopping all services...$(NC)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✅ Services stopped$(NC)"

restart: ## Restart all services
	@echo "$(YELLOW)Restarting all services...$(NC)"
	$(DOCKER_COMPOSE) restart
	@echo "$(GREEN)✅ Services restarted$(NC)"

clean: ## Stop and remove containers, networks, and volumes
	@echo "$(RED)Cleaning up Docker resources...$(NC)"
	$(DOCKER_COMPOSE) down -v --rmi local --remove-orphans
	@echo "$(GREEN)✅ Cleanup completed$(NC)"

logs: ## View logs from all services
	@echo "$(BLUE)Viewing logs from all services (Ctrl+C to exit)...$(NC)"
	$(DOCKER_COMPOSE) logs -f

logs-backend: ## View backend logs only
	@echo "$(BLUE)Viewing backend logs...$(NC)"
	$(DOCKER_COMPOSE) logs -f backend

logs-frontend: ## View frontend logs only
	@echo "$(BLUE)Viewing frontend logs...$(NC)"
	$(DOCKER_COMPOSE) logs -f frontend

logs-db: ## View database logs only
	@echo "$(BLUE)Viewing database logs...$(NC)"
	$(DOCKER_COMPOSE) logs -f postgres

status: ## Check service status
	@echo "$(BLUE)Service Status:$(NC)"
	@$(DOCKER_COMPOSE) ps
	@echo ""
	@echo "$(BLUE)Health Checks:$(NC)"
	@curl -s http://localhost:8000/ >/dev/null && echo "$(GREEN)✅ Backend API (http://localhost:8000)$(NC)" || echo "$(RED)❌ Backend API$(NC)"
	@curl -s http://localhost:3000/ >/dev/null && echo "$(GREEN)✅ Frontend (http://localhost:3000)$(NC)" || echo "$(RED)❌ Frontend$(NC)"
	@$(DOCKER_COMPOSE) exec -T postgres pg_isready -U portfolio_user >/dev/null 2>&1 && echo "$(GREEN)✅ PostgreSQL Database$(NC)" || echo "$(RED)❌ PostgreSQL Database$(NC)"
	@$(DOCKER_COMPOSE) exec -T redis redis-cli ping >/dev/null 2>&1 && echo "$(GREEN)✅ Redis Cache$(NC)" || echo "$(RED)❌ Redis Cache$(NC)"

init: ## Initialize database with sample data
	@echo "$(BLUE)Initializing database...$(NC)"
	$(DOCKER_COMPOSE) exec backend python scripts/init_data.py
	@echo "$(GREEN)✅ Database initialized$(NC)"

shell-backend: ## Open shell in backend container
	@echo "$(BLUE)Opening shell in backend container...$(NC)"
	$(DOCKER_COMPOSE) exec backend /bin/bash

shell-frontend: ## Open shell in frontend container
	@echo "$(BLUE)Opening shell in frontend container...$(NC)"
	$(DOCKER_COMPOSE) exec frontend /bin/sh

shell-db: ## Open PostgreSQL shell
	@echo "$(BLUE)Opening PostgreSQL shell...$(NC)"
	$(DOCKER_COMPOSE) exec postgres psql -U portfolio_user -d portfolio_db

test: ## Run tests
	@echo "$(BLUE)Running backend tests...$(NC)"
	$(DOCKER_COMPOSE) exec backend python -m pytest
	@echo "$(BLUE)Running frontend tests...$(NC)"
	$(DOCKER_COMPOSE) exec frontend npm test

dev: ## Start services in development mode with hot reload
	@echo "$(BLUE)Starting development environment...$(NC)"
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml up

prod: ## Start services in production mode
	@echo "$(BLUE)Starting production environment...$(NC)"
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.prod.yml up -d

backup-db: ## Backup database
	@echo "$(BLUE)Creating database backup...$(NC)"
	@mkdir -p backups
	$(DOCKER_COMPOSE) exec -T postgres pg_dump -U portfolio_user portfolio_db > backups/portfolio_backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✅ Database backup created in backups/$(NC)"

restore-db: ## Restore database from backup (usage: make restore-db BACKUP=filename.sql)
	@echo "$(BLUE)Restoring database from backup...$(NC)"
	@if [ -z "$(BACKUP)" ]; then \
		echo "$(RED)Error: Please specify BACKUP file: make restore-db BACKUP=filename.sql$(NC)"; \
		exit 1; \
	fi
	$(DOCKER_COMPOSE) exec -T postgres psql -U portfolio_user -d portfolio_db < $(BACKUP)
	@echo "$(GREEN)✅ Database restored$(NC)"

monitor: ## Monitor resource usage
	@echo "$(BLUE)Resource Usage (Ctrl+C to exit):$(NC)"
	@watch 'docker stats --no-stream'

urls: ## Display service URLs
	@echo "$(BLUE)Service URLs:$(NC)"
	@echo "$(GREEN)📱 Frontend:        $(NC)http://localhost:3000"
	@echo "$(GREEN)🔧 Backend API:     $(NC)http://localhost:8000"
	@echo "$(GREEN)📊 API Docs:        $(NC)http://localhost:8000/docs"
	@echo "$(GREEN)🗄️  Database:       $(NC)postgresql://portfolio_user:***@localhost:5432/portfolio_db"
	@echo "$(GREEN)🔴 Redis:          $(NC)redis://localhost:6379"

setup: ## Initial setup - build and start with initialization
	@echo "$(BLUE)Setting up Investment Portfolio MVP...$(NC)"
	@make build
	@make start
	@sleep 10
	@make init
	@make urls
	@echo "$(GREEN)🎉 Setup completed! Portfolio is ready to use$(NC)"

quick-start: setup ## Alias for setup

# Development helpers
npm-install: ## Install npm dependencies
	$(DOCKER_COMPOSE) exec frontend npm install

pip-install: ## Install pip dependencies
	$(DOCKER_COMPOSE) exec backend pip install -r requirements.txt

upgrade: ## Pull latest images and restart
	@echo "$(BLUE)Upgrading services...$(NC)"
	$(DOCKER_COMPOSE) pull
	$(DOCKER_COMPOSE) up -d --build
	@echo "$(GREEN)✅ Services upgraded$(NC)"

# Maintenance
prune: ## Clean up Docker system
	@echo "$(YELLOW)Pruning Docker system...$(NC)"
	docker system prune -f
	docker volume prune -f
	@echo "$(GREEN)✅ Docker system cleaned$(NC)"

reset: ## Reset everything (DANGEROUS - removes all data)
	@echo "$(RED)⚠️  This will remove ALL data and containers!$(NC)"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@make clean
	@make prune
	@echo "$(GREEN)✅ System reset completed$(NC)"