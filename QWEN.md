# QWEN.md - Clean Architecture + DDD Axum Application Template

## Project Overview

This is a Rust web application template following Clean Architecture and Domain-Driven Design (DDD) principles using Axum as the web framework. The project implements a modern, layered architecture with clear separation of concerns and follows Rust's current module system conventions.

### Key Technologies
- **Rust** (Edition 2021) - Systems programming language with focus on safety and performance
- **Axum** - Web framework for building async web applications
- **Tokio** - Async runtime for Rust
- **Serde** - Serialization/deserialization framework
- **SQLx** - Compile-time checked SQL queries (via dependencies)
- **Tracing** - Structured application observability
- **UUID** - Universally unique identifier generation
- **Validator** - Input validation
- **BCrypt** - Password hashing
- **JSON Web Tokens** - Authentication mechanism

### Architecture Pattern
The project follows Clean Architecture principles with four distinct layers:
1. **Domain Layer** - Contains business entities, value objects, domain services, and domain events
2. **Application Layer** - Contains use cases, DTOs, and ports (interfaces)
3. **Infrastructure Layer** - Contains concrete implementations of ports, database access, configuration
4. **Presentation Layer** - Contains web handlers and controllers

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

## Building and Running

### Prerequisites
- Rust (latest stable version)
- PostgreSQL database (for production use)

### Setup Instructions
1. Install Rust: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
2. Clone or copy the project
3. Copy `.env.example` to `.env` and configure your database URL
4. Install dependencies: `cargo build`

### Running the Application
```bash
# Run the application
cargo run

# Run in release mode
cargo run --release

# Build without running
cargo build
```

### Testing
```bash
# Run all tests
cargo test

# Run tests for a specific layer
cargo test --test domain
cargo test --test application
cargo test --test integration

# Run tests with output
cargo test -- --nocapture
```

## Development Conventions

### Module System
The project uses the modern Rust module system where:
- Top-level modules are defined as individual `.rs` files (e.g., `application.rs`, `domain.rs`)
- Submodules are individual `.rs` files within their respective directories
- A `lib.rs` file is provided to allow modules to be tested externally

### Error Handling
- Uses `thiserror` for error definitions with descriptive error messages
- Implements proper error chaining with `#[from]` attributes
- Follows Rust's `Result<T, E>` pattern throughout

### Async/Await
- All I/O operations are asynchronous
- Uses `tokio` runtime for async execution
- Proper error propagation with `?` operator

### Logging and Tracing
- Uses `tracing` crate for structured logging
- Different log levels supported (INFO, DEBUG, WARN, ERROR)
- Centralized initialization in main function

### Configuration
- Multiple configuration sources supported:
  1. Environment variables prefixed with `APP_`
  2. Configuration files (`config/default.toml`)
  3. Default values in code
- Uses `config` crate for hierarchical configuration management

### Domain-Driven Design Patterns
- Value Objects: Encapsulate primitive types with validation (Email, Password)
- Entities: Domain objects with identity and lifecycle
- Domain Services: Business logic that doesn't naturally fit in entities
- Domain Events: Communicate state changes between bounded contexts
- Repository Pattern: Abstract persistence mechanisms

### Testing Strategy
- Unit tests for pure domain logic
- Integration tests for use case coordination
- Mock implementations for external dependencies
- Comprehensive test coverage for business rules

## Key Features

- **Async/await support** throughout the application
- **Type-safe HTTP handling** with Axum
- **Comprehensive error handling** with proper error types
- **Structured logging** with tracing
- **JWT authentication utilities**
- **Database integration** with SQLx
- **Input validation** with validator
- **Password hashing** with bcrypt
- **UUID support** for identifiers
- **Health check endpoint**
- **Clean Architecture** with clear separation of concerns
- **Domain-Driven Design** patterns implemented
- **Modern Rust module system** following current best practices

## Configuration

The application supports multiple configuration sources with the following precedence:
1. Environment variables (prefixed with `APP_`)
2. Configuration files (`config/default.toml`)
3. Default values in code

Example environment variables:
```bash
APP_SERVER_PORT=9000
APP_DATABASE_URL="postgresql://user:pass@localhost/mydb"
APP_JWT_SECRET="my_secure_secret"
```

## Important Notes

- The project uses an in-memory repository implementation by default for simplicity
- For production use, replace with a persistent database implementation
- JWT tokens have configurable expiration times
- Passwords are hashed using bcrypt with appropriate cost factors
- The application follows security best practices for web applications
- All external dependencies are properly versioned in Cargo.toml