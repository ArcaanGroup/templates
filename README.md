# go-clean-template (Rust)

A production-grade **Clean Architecture** template for Rust applications, emphasizing separation of concerns, testability, and maintainability.

## Architecture

```
src/
├── main.rs               → Application entry point (DI wiring, server lifecycle)
├── domain/               → Enterprise business rules (entities, errors)
├── application/          → Use cases / application business rules, repository traits
├── interface/            → Adapters (HTTP handlers, middleware, router, DTOs)
└── infrastructure/       → External implementations (persistence, logger, config)
```

**Dependency rule:** Dependencies point inward. `domain` knows nothing of the outside world. `infrastructure` implements repository traits defined in `application`.

## Layers

| Layer | Purpose | Dependencies |
|---|---|---|
| **Domain** | Entities, domain errors | None |
| **Application** | Use case implementations, repository traits | Domain |
| **Interface** | HTTP handlers, middleware, router, DTOs | Application |
| **Infrastructure** | Logger, in-memory repository, config | Domain |

## Quick Start

```bash
cargo run
```

Server starts on `:8080` with zero external dependencies (in-memory storage).

## API

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/api/v1/users` | List all users |
| `POST` | `/api/v1/users` | Create a user |
| `GET` | `/api/v1/users/{id}` | Get user by ID |
| `PUT` | `/api/v1/users/{id}` | Update user |
| `DELETE` | `/api/v1/users/{id}` | Delete user |
| `GET` | `/api/v1/roles` | List all roles |
| `POST` | `/api/v1/roles` | Create a role |
| `GET` | `/api/v1/roles/{id}` | Get role by ID |
| `PUT` | `/api/v1/roles/{id}` | Update role |
| `DELETE` | `/api/v1/roles/{id}` | Delete role |

## Testing

```bash
cargo test
```

## Commands

```
make build         Build binary
make run           Run application
make test          Run tests
make lint          Run clippy
make clean         Clean artifacts
make docker-build  Build Docker image
make docker-up     Start with Docker Compose
```
