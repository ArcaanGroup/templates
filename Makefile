.PHONY: build run dev test lint clean coverage swag seed tools docker-build docker-up docker-down help

TOOLS_DIR := $(shell pwd)/.tools

APP_NAME := go-clean-template
BUILD_DIR := ./bin

build: ## Build the binary
	go build -ldflags="-s -w" -o $(BUILD_DIR)/$(APP_NAME) ./cmd/main.go

run: ## Run the application
	go run ./cmd/main.go

dev: tools ## Run with live-reload (air)
	$(TOOLS_DIR)/air

test: ## Run tests with coverage
	go test -v -coverprofile=coverage.out -covermode=atomic ./...

lint: ## Run linter
	golangci-lint run ./...

swag: ## Regenerate Swagger docs
	swag init -g cmd/main.go --parseDependency --parseInternal --output docs
	sed -i '/LeftDelim\|RightDelim/d' docs/docs.go

clean: ## Clean build artifacts
	rm -rf $(BUILD_DIR) $(TOOLS_DIR) tmp/ coverage.out coverage.html

tools: $(TOOLS_DIR)/air ## Install development tools

$(TOOLS_DIR)/air:
	@mkdir -p $(TOOLS_DIR)
	GOBIN=$(TOOLS_DIR) go install github.com/air-verse/air@latest

coverage: test ## Show test coverage in browser
	go tool cover -html=coverage.out -o coverage.html

init: ## Run the bootstrap CLI (init project or generate entities)
	go run ./cmd/init/main.go

seed: ## Seed initial data (roles, users)
	go run ./cmd/seed/main.go

docker-build: ## Build Docker image
	docker build -t $(APP_NAME) .

docker-up: ## Start services with Docker Compose
	docker-compose up --build -d

docker-down: ## Stop services
	docker-compose down

help: ## Display this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
