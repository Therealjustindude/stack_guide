.PHONY: help dev build up down logs clean test lint format

# Default target
help:
	@echo "StackGuide - Local-first AI Knowledge Assistant"
	@echo ""
	@echo "🚀 Quick Start Commands:"
	@echo "  stackguide      - Full setup & launch (build + dev)"
	@echo "  stackguide-cli  - Setup, launch & open CLI automatically"
	@echo "  quick-query     - Smart query that starts services if needed"
	@echo ""
	@echo "🔄 Development Workflows:"
	@echo "  dev             - Start development environment (hot reload)"
	@echo "  dev-refresh     - Rebuild and restart (for dependency changes)"
	@echo "  dev-restart     - Quick restart (no rebuild)"
	@echo "  dev-cycle       - Full cycle: clean + build + dev"
	@echo "  dev-logs        - Start dev environment with logs"
	@echo "  dev-monitor     - Start dev environment with monitoring"
	@echo ""
	@echo "🔧 Core Commands:"
	@echo "  build           - Build all Docker images"
	@echo "  up              - Start production environment"
	@echo "  down            - Stop all services"
	@echo "  logs            - View logs from all services"
	@echo "  clean           - Remove all containers, images, and volumes"
	@echo ""
	@echo "💻 CLI & Queries:"
	@echo "  cli             - Open interactive CLI"
	@echo "  query           - Run specific query (requires Q= parameter)"
	@echo ""
	@echo "🧪 Development Tools:"
	@echo "  test            - Run tests"
	@echo "  lint            - Run linting"
	@echo "  format          - Format code"
	@echo "  setup           - Initial setup and configuration"
	@echo "  ingest          - Ingest data from local sources"

# Development environment with hot reloading (CPU mode by default)
dev:
	@echo "🚀 Starting StackGuide development environment (CPU mode)..."
	docker compose -f docker-compose.dev.yml --profile cpu up --build



# Development environment with GPU support
dev-gpu:
	@echo "🚀 Starting StackGuide development environment (GPU mode)..."
	docker compose -f docker-compose.dev.yml --profile gpu up --build

# Build all Docker images
build:
	@echo "🔨 Building StackGuide Docker images..."
	docker compose build

# Production environment
up:
	@echo "🚀 Starting StackGuide production environment..."
	docker compose up -d

# Stop all services
down:
	@echo "🛑 Stopping StackGuide services..."
	docker compose down

# View logs
logs:
	@echo "📋 Viewing StackGuide logs..."
	docker compose logs -f

# CLI commands
cli:
	@echo "💻 Starting StackGuide CLI..."
	docker compose exec api python -m cli.main

# Query via CLI
query:
	@echo "🔍 Running StackGuide query..."
	docker compose exec api python -m cli.main query "$(Q)"

# Clean everything
clean:
	@echo "🧹 Cleaning up StackGuide..."
	docker-compose down -v --rmi all
	docker system prune -f
	rm -rf data/ models/

# Run tests
test:
	@echo "🧪 Running StackGuide tests..."
	docker-compose exec api pytest

# Run linting
lint:
	@echo "🔍 Running StackGuide linting..."
	docker-compose exec api flake8 app/
	docker-compose exec api black --check app/

# Format code
format:
	@echo "✨ Formatting StackGuide code..."
	docker-compose exec api black app/
	docker-compose exec api isort app/

# Initial setup
setup:
	@echo "⚙️  Setting up StackGuide..."
	mkdir -p data/chroma models
	@echo "📁 Created directories: data/chroma, models"
	@echo "🔑 Please ensure you have:"
	@echo "   - Docker and Docker Compose installed"
	@echo "   - NVIDIA Docker runtime (for GPU support)"
	@echo "   - gpt-oss model files in ./models/"
	@echo "   - .env file configured"

# Data ingestion
ingest:
	@echo "📚 Ingesting data into StackGuide..."
	docker-compose exec api python -m app.core.ingestion.main

# Quick start - full setup and launch
stackguide:
	@echo "🚀 StackGuide - Full Setup & Launch"
	@echo "Building images..."
	@make build
	@echo "Starting services..."
	@make dev

# Quick start with CLI ready
stackguide-cli:
	@echo "🚀 StackGuide - Setup, Launch & CLI Ready"
	@echo "Building images..."
	@make build
	@echo "Starting services..."
	@make dev
	@echo "⏳ Waiting for services to be ready..."
	@sleep 10
	@echo "💻 Opening CLI..."
	@make cli

# Development workflow - rebuild and restart
dev-refresh:
	@echo "🔄 Refreshing development environment..."
	@make down
	@make build
	@make dev

# Quick restart (no rebuild)
dev-restart:
	@echo "🔄 Restarting services..."
	@make down
	@make dev

# Full development cycle
dev-cycle:
	@echo "🔄 Full development cycle..."
	@make down
	@make clean
	@make build
	@make dev

# Development with logs
dev-logs:
	@echo "🚀 Starting StackGuide with logs..."
	@make dev &
	@sleep 5
	@make logs

# Quick query (builds and runs if needed)
quick-query:
	@echo "🔍 Quick Query Mode"
	@if ! docker compose ps | grep -q "Up"; then \
		echo "Services not running, starting them..."; \
		make build; \
		make dev; \
		sleep 15; \
	fi
	@echo "Running query: $(Q)"
	@make query Q="$(Q)"

# Development with monitoring
dev-monitor:
	@echo "🚀 Starting StackGuide with monitoring..."
	@make dev &
	@sleep 5
	@echo "📊 Service Status:"
	@docker compose ps
	@echo "📋 Recent Logs:"
	@make logs
