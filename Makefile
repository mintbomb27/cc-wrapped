.PHONY: help build up down restart logs clean test

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build all Docker images
	docker-compose build

up: ## Start all services
	docker-compose up

up-detached: ## Start all services in detached mode
	docker-compose up -d

down: ## Stop all services
	docker-compose down

restart: ## Restart all services
	docker-compose restart

restart-backend: ## Restart only the backend service
	docker-compose restart backend

restart-frontend: ## Restart only the frontend service
	docker-compose restart frontend

logs: ## View logs from all services
	docker-compose logs -f

logs-backend: ## View logs from backend service
	docker-compose logs -f backend

logs-frontend: ## View logs from frontend service
	docker-compose logs -f frontend

clean: ## Stop services and remove volumes (WARNING: deletes database)
	docker-compose down -v

rebuild: ## Rebuild and restart all services
	docker-compose down
	docker-compose build --no-cache
	docker-compose up

rebuild-detached: ## Rebuild and restart all services in detached mode
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

status: ## Show status of all services
	docker-compose ps

shell-backend: ## Open a shell in the backend container
	docker-compose exec backend /bin/bash

shell-frontend: ## Open a shell in the frontend container
	docker-compose exec frontend /bin/sh

test: ## Run a quick test to check if services are responding
	@echo "Testing backend health..."
	@curl -f http://localhost:8000/health || echo "Backend not responding"
	@echo "\nTesting frontend..."
	@curl -f http://localhost:3000 || echo "Frontend not responding"
	@echo "\nTesting API through frontend proxy..."
	@curl -f http://localhost:3000/api/v1/ || echo "API proxy not working"
