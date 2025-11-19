.PHONY: help install migrate create-admin run dev clean test lint format

# Default target
help:
	@echo "Employee Management API - Available Commands:"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make install      - Install dependencies with uv"
	@echo "  make migrate      - Run database migrations"
	@echo "  make create-admin - Create initial admin user"
	@echo "  make setup        - Full setup (install + migrate + create-admin)"
	@echo ""
	@echo "Run Commands:"
	@echo "  make run          - Start the production server"
	@echo "  make dev          - Start the development server with reload"
	@echo ""
	@echo "Database Commands:"
	@echo "  make migration    - Create a new migration"
	@echo "  make db-upgrade   - Apply pending migrations"
	@echo "  make db-downgrade - Rollback last migration"
	@echo ""
	@echo "Development Commands:"
	@echo "  make test         - Run tests (when implemented)"
	@echo "  make lint         - Run code linting"
	@echo "  make format       - Format code"
	@echo "  make clean        - Clean cache and temporary files"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make check        - Check if app imports correctly"
	@echo "  make logs         - Show application logs"

# Setup commands
install:
	@echo "📦 Installing dependencies..."
	uv sync

migrate:
	@echo "🗄️  Running database migrations..."
	uv run alembic upgrade head

create-admin:
	@echo "👤 Creating admin user..."
	uv run python create_admin.py

setup: install migrate create-admin
	@echo "✅ Setup complete! You can now run 'make run' to start the application."

# Run commands
run:
	@echo "🚀 Starting Employee Management API..."
	@echo "📍 Application will be available at: http://localhost:8000"
	@echo "📚 API Documentation: http://localhost:8000/docs"
	@echo "🏥 Health Check: http://localhost:8000/health"
	@echo ""
	uv run python run.py

dev:
	@echo "🔧 Starting development server with auto-reload..."
	@echo "📍 Application will be available at: http://localhost:8000"
	@echo "📚 API Documentation: http://localhost:8000/docs"
	@echo ""
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Database commands
migration:
	@read -p "Enter migration message: " msg; \
	echo "📝 Creating new migration: $$msg"; \
	uv run alembic revision --autogenerate -m "$$msg"

db-upgrade:
	@echo "⬆️  Applying pending migrations..."
	uv run alembic upgrade head

db-downgrade:
	@echo "⬇️  Rolling back last migration..."
	uv run alembic downgrade -1

# Development commands
test:
	@echo "🧪 Running tests..."
	@echo "⚠️  Tests not implemented yet. Add your test framework of choice."

lint:
	@echo "🔍 Running code linting..."
	@if command -v ruff >/dev/null 2>&1; then \
		echo "Using ruff for linting..."; \
		uv run ruff check .; \
	else \
		echo "⚠️  ruff not installed. Install with: uv add ruff"; \
	fi

format:
	@echo "🎨 Formatting code..."
	@if command -v ruff >/dev/null 2>&1; then \
		echo "Using ruff for formatting..."; \
		uv run ruff format .; \
	else \
		echo "⚠️  ruff not installed. Install with: uv add ruff"; \
	fi

# Utility commands
check:
	@echo "✅ Checking if application imports correctly..."
	uv run python -c "from app.main import app; print('✅ App imports successfully!')"

clean:
	@echo "🧹 Cleaning cache and temporary files..."
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name "*.egg-info" -delete
	@echo "✅ Cleanup complete!"

logs:
	@echo "📋 Application logs would be shown here..."
	@echo "💡 Tip: Add logging configuration to capture logs to files"

# Environment setup
env-example:
	@echo "📄 Creating .env file from .env.example..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ .env file created. Please update with your configuration."; \
	else \
		echo "⚠️  .env file already exists."; \
	fi