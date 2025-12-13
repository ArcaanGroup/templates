# Makefile for FastAPI project

# Variables
PYTHON := $(shell which python)
PDM := $(shell which pdm)
PORT := 8000

# Default target
.PHONY: help
help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_0-9%-]+:.*?## .*$$' $(word 1,$(MAKEFILE_LIST)) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "%-30s %s\n", $$1, $$2}'

.PHONY: install
install: ## Install project dependencies with PDM
	@echo "Installing dependencies..."
	$(PDM) install

.PHONY: dev
dev: ## Run the development server
	@echo "Starting development server on port $(PORT)..."
	$(PDM) run uvicorn app.main:app --reload --host 0.0.0.0 --port $(PORT)

.PHONY: run
run: ## Run the server in production mode
	@echo "Starting server in production mode..."
	$(PDM) run uvicorn app.main:app --host 0.0.0.0 --port $(PORT)

.PHONY: test
test: ## Run tests with pytest
	@echo "Running tests..."
	$(PDM) run pytest

.PHONY: test-cov
test-cov: ## Run tests with coverage
	@echo "Running tests with coverage..."
	$(PDM) run pytest --cov=.

.PHONY: test-verbose
test-verbose: ## Run tests in verbose mode
	@echo "Running tests in verbose mode..."
	$(PDM) run pytest -v

.PHONY: lint
lint: ## Lint the code (basic check)
	@echo "Checking code format..."
	@$(PDM) run python -m py_compile app/main.py
	@echo "Code checks completed"

.PHONY: clean
clean: ## Clean Python cache files
	@find . -type d -name __pycache__ -delete
	@find . -type f -name "*.py[co]" -delete
	@find . -type f -name "*~" -delete
	@find . -type f -name ".coverage" -delete
	@echo "Cleaned Python cache files"

.PHONY: check
check: ## Check the status of the project
	@echo "Project directory: $(PWD)"
	@echo "Python interpreter: $(PYTHON)"
	@echo "PDM: $(PDM)"
	@$(PDM) list

.PHONY: shell
shell: ## Open Python shell with project environment
	@$(PDM) run python

.PHONY: create-db
create-db: ## Create the database if it doesn't exist
	@echo "Creating the database if it doesn't exist..."
	$(PDM) run python scripts/create_db.py

.PHONY: serve
serve: dev ## Alias for dev (run development server)

.PHONY: auth
auth: ## Run the authorization manager CLI
	@echo "Starting Authorization Manager..."
	$(PDM) run python scripts/auth_manager.py

.PHONY: resource
resource: ## Create a new resource with all 4 layers (models, service, repository, controller)
	@echo "Creating a new resource..."
	$(PDM) run python scripts/create_resource.py

.PHONY: migrate
migrate: ## Create a new auto-generated migration
	@echo "Creating a new auto-generated migration..."
	@read -p "Enter migration message: " msg; \
	$(PDM) run alembic revision --autogenerate -m "$$msg"

.PHONY: upgrade
upgrade: ## Upgrade the database to the latest version
	@echo "Upgrading the database to the latest version..."
	$(PDM) run alembic upgrade head

.PHONY: seed
seed: ## Seed the database with initial data
	@echo "Seeding the database with initial data..."
	$(PDM) run python scripts/seed.py
