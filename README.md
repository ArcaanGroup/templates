# Clean Architecture + DDD Axum Application Template

This is a template for a Rust web application following Clean Architecture and Domain-Driven Design (DDD) principles using Axum as the web framework.

## Project Structure

```
src/
├── application.rs       # Application layer: use cases, DTOs, ports
├── domain.rs            # Domain layer: entities, value objects, domain services
├── infrastructure.rs    # Infrastructure layer: database, config, repositories
├── presentation.rs      # Presentation layer: web handlers, controllers
├── shared_kernel.rs     # Shared types and utilities
├── application/         # Application layer submodules
│   ├── dtos.rs          # Data Transfer Objects
│   ├── ports.rs         # Port interfaces
│   └── usecases.rs      # Use case implementations
├── domain/              # Domain layer submodules
│   ├── entities.rs      # Domain entities
│   ├── events.rs        # Domain events
│   ├── services.rs      # Domain services and repositories
│   └── value_objects.rs # Value objects
├── infrastructure/      # Infrastructure layer submodules
│   ├── config.rs        # Configuration management
│   ├── database.rs      # Database connections and migrations
│   ├── middleware.rs    # Middleware implementations
│   └── repositories.rs  # Repository implementations
├── presentation/        # Presentation layer submodules (handlers and middleware if any)
├── shared_kernel/       # Shared types and utilities submodules
│   ├── types.rs         # Common types
│   └── utils.rs         # Common utilities
├── main.rs              # Application entry point
└── lib.rs               # Library exports for testing
```

## Architecture Principles

### Clean Architecture
- Dependencies point inward toward the domain
- Domain layer is independent of external concerns
- Use cases orchestrate interactions between domain and infrastructure

### Domain-Driven Design
- Rich domain models with business logic
- Value objects for encapsulating primitive types
- Domain events for communicating state changes
- Ubiquitous language throughout the codebase

## Layers

### Domain Layer
Contains business entities, value objects, domain services, and domain events. This is the core of the application and should be independent of any frameworks or external concerns.

### Application Layer
Contains use cases that orchestrate business logic, DTOs for data transfer, and ports (interfaces) that define contracts for infrastructure implementations.

### Infrastructure Layer
Contains implementations of ports defined in the application layer, database access, external service integrations, and configuration management.

### Presentation Layer
Contains web handlers, controllers, and other presentation concerns. This layer adapts between the external world and the application layer.

## Getting Started

1. Install Rust: https://www.rust-lang.org/tools/install
2. Set up a PostgreSQL database
3. Copy `.env.example` to `.env` and configure your database URL
4. Run the application: `cargo run`

## Testing

Run all tests:
```bash
cargo test
```

Run tests for a specific layer:
```bash
cargo test --test domain
cargo test --test application
cargo test --test integration
```

## Configuration

Configuration is managed through:
1. Environment variables prefixed with `APP_`
2. Configuration files (`config/default.toml`)
3. Default values in code

Example environment variable:
```bash
APP_SERVER_PORT=9000
APP_DATABASE_URL="postgresql://user:pass@localhost/mydb"
```

## Features

- Async/await support throughout
- Type-safe HTTP handling with Axum
- Comprehensive error handling
- Structured logging with tracing
- JWT authentication utilities
- Database integration with SQLx
- Input validation with validator
- Password hashing with bcrypt
- UUID support for identifiers
- Health check endpoint
