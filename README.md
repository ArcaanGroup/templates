# FastAPI Server

A FastAPI server following Clean Architecture with in-memory persistence.

## Features

- FastAPI framework with async support
- Clean architecture with separation of concerns
- Repository pattern with interfaces
- DTOs (Data Transfer Objects) separated from domain models
- Standardized response format
- Dependency injection
- Proper exception handling
- JWT-based authentication with refresh tokens
- RBAC (Role-Based Access Control) with permissions and policies

## Architecture

```
app/
  domain/entities/         # business models (no framework deps)
  domain/error/            # domain exceptions
  application/use_cases/   # business logic, orchestrates repositories
  interface/dto/           # request/response DTOs
  interface/mappers/       # DTO <-> entity conversion
  interface/repository/    # repository interfaces (abstract)
  interface/controller/    # FastAPI routes
  interface/dependencies/  # DI wiring (resolves repos -> use cases -> controllers)
  infra/repositories/      # concrete implementations
    json/                  # JSON-file-backed (permissions, policies)
    in_memory/             # dict-backed (users, roles, refresh tokens)
  infra/core/              # config, logging, middleware, seed
  infra/services/          # password hashing, JWT tokens
```

## Quick Start

```bash
pdm install
make dev
```

The server runs on `http://localhost:8000` (or port 8004, see `app/main.py`).
