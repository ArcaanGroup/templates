# go-clean-template

A production-grade **Clean Architecture** template for Go applications, emphasizing separation of concerns, testability, and maintainability.

## Architecture

```
cmd/                    → Application entry point (DI wiring, server lifecycle)
config/                 → Environment-based configuration
internal/
├── domain/             → Enterprise business rules (entities, repository interfaces, errors)
├── application/        → Use cases / application business rules
├── interface/          → Adapters (HTTP handlers, middleware, router)
└── infrastructure/     → External implementations (persistence, logger)
```

**Dependency rule:** Dependencies point inward. `domain` knows nothing of the outside world. `infrastructure` implements `domain` interfaces.

## Layers

| Layer | Purpose | Dependencies |
|---|---|---|
| **Domain** | Entities, repository interfaces, domain errors | None |
| **Application** | Use case implementations, DTOs | Domain |
| **Interface** | HTTP handlers, middleware, router | Application |
| **Infrastructure** | Logger, in-memory repository | Domain |

## Quick Start

```bash
make run
```

Server starts on `:8080` with zero external dependencies (in-memory storage).

Swagger UI at `http://localhost:8080/swagger/`.

## API

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/openapi.json` | OpenAPI spec (JSON) |
| `GET` | `/swagger/*` | Swagger UI |
| `GET` | `/api/v1/users` | List all users |
| `POST` | `/api/v1/users` | Create a user |
| `GET` | `/api/v1/users/{id}` | Get user by ID |
| `PUT` | `/api/v1/users/{id}` | Update user |
| `DELETE` | `/api/v1/users/{id}` | Delete user |

### Example

```bash
curl -X POST localhost:8080/api/v1/users \
  -H 'Content-Type: application/json' \
  -d '{"name":"Alice","email":"alice@example.com"}'
```

## Testing

```bash
make test        # 18 tests, all passing
make coverage    # HTML coverage report
```

## Commands

```
make build         Build binary (runs swag first)
make run           Run application (runs swag first)
make test          Run tests
make lint          Run golangci-lint
make swag          Regenerate Swagger docs
make coverage      Test coverage report
make clean         Clean artifacts
make docker-build  Build Docker image
make docker-up     Start with Docker Compose
```

## Replacing the Repository

To use a real database:

1. Implement `domain.UserRepository` in `internal/infrastructure/persistence/`
2. Wire the new implementation in `cmd/main.go`
3. Add connection config to `config/config.go`

The use case layer and handlers remain unchanged — they depend only on the interface.
