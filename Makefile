.PHONY: build run test lint clean docker-build docker-up docker-down help

APP_NAME := rust-clean-template

build: ## Build the binary
	cargo build --release

run: ## Run the application
	cargo run

test: ## Run tests with coverage
	cargo test

lint: ## Run linter
	cargo clippy -- -D warnings

clean: ## Clean build artifacts
	cargo clean

docker-build: ## Build Docker image
	docker build -t $(APP_NAME) .

docker-up: ## Start services with Docker Compose
	docker-compose up --build -d

docker-down: ## Stop services
	docker-compose down

help: ## Display this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
