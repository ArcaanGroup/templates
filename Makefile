.PHONY: help install dev install-dev run test lint format type-check clean migrate create-db

# Default target
help:
	@echo "Available commands:"
	@echo "  make install       - Install production dependencies"
	@echo "  make install-dev   - Install all dependencies (including dev)"
	@echo "  make run           - Run development server"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linters (ruff)"
	@echo "  make format        - Format code (black, isort)"
	@echo "  make type-check    - Run type checker (mypy)"
	@echo "  make migrate       - Run database migrations"
	@echo "  make create-db     - Create database"
	@echo "  make clean         - Clean cache and temporary files"

# Installation
install:
	pdm install

install-dev:
	pdm install --dev

# Development
run:
	pdm run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Testing
test:
	pdm run pytest

test-cov:
	pdm run pytest --cov=app --cov-report=html --cov-report=term

# Code Quality
lint:
	pdm run ruff check .

format:
	pdm run black .
	pdm run isort .

format-check:
	pdm run black --check .
	pdm run isort --check .

type-check:
	pdm run mypy app

# Database
migrate:
	pdm run alembic upgrade head

migrate-create:
	@read -p "Migration message: " msg; \
	pdm run alembic revision --autogenerate -m "$$msg"

create-db:
	pdm run python scripts/create_db.py

# Cleanup
clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	rm -rf htmlcov/
	rm -rf .coverage
