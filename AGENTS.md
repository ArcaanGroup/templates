# AGENTS.md

## Commands

```bash
pdm install                  # install dependencies
pdm run uvicorn app.main:app --reload   # dev server (port 8004, see main.py)
pdm run pytest               # run tests
pdm run alembic upgrade head # apply migrations
pdm run alembic revision --autogenerate -m "msg"  # create migration
```

Makefile shortcuts: `make init-db`, `make dev`, `make test`, `make seed`, `make upgrade`

## Stack

- **Package manager**: PDM (prefix all commands with `pdm run`)
- **Python**: 3.12 (exact, see pyproject.toml)
- **Framework**: FastAPI with clean architecture
- **Database**: PostgreSQL + SQLAlchemy (async) + Alembic
- **Config**: pydantic-settings reads `.env` (see `.env.example` for template)

## Architecture

```
app/
  domain/entities/      # business models
  interface/dto/        # request/response DTOs
  interface/mappers/    # DTO <-> entity conversion
  application/use_cases/# business logic
  interface/repository/ # repository interfaces
  infra/repositories/   # SQLAlchemy implementations
  interface/controller/ # FastAPI routes
  interface/dependencies/# dependency injection wiring
  infra/core/config.py  # pydantic-settings config class
```

## Gotchas

- **alembic.ini sqlalchemy.url** must match `.env` database config (no auto-sync)
- **Permissions** stored in `statics/permissions.json` (not database-backed)
- **asyncio_mode = "auto"** in pytest config (no manual event loop handling)
- **No lint/typecheck** configured (Makefile `lint` target is just py_compile)
- **Seed script** creates admin/admin@example.com/Secret123 with "Admin" role + super:user permission

## DB Setup Sequence

Requires PostgreSQL running: `make init-db` (or manually: create-db → upgrade → seed)
