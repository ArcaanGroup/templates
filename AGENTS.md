# AGENTS.md

## Commands

```bash
pdm install                              # install dependencies
pdm run uvicorn app.main:app --reload    # dev server (port 8004, see main.py)
pdm run pytest                           # run all tests
pdm run pytest -v                        # verbose
pdm run pytest tests/unit/               # unit tests only
pdm run pytest tests/integration/        # integration tests only
pdm run pytest -k "test_login"           # filter by test name
pdm run alembic upgrade head             # apply migrations
pdm run alembic revision --autogenerate -m "msg"  # create migration
```

Makefile shortcuts: `make init-db`, `make dev`, `make test`, `make seed`, `make upgrade`, `make seed-mem`, `make seed-db`

## Stack

- **Package manager**: PDM (prefix all commands with `pdm run`)
- **Python**: 3.12 (exact, see pyproject.toml)
- **Framework**: FastAPI with clean architecture
- **Persistence**: In-memory (default, no DB required) or PostgreSQL + SQLAlchemy + Alembic
- **Config**: pydantic-settings reads `.env` (see `.env.example` for template)

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
  interface/dependencies/  # DI wiring (resolves repos → use cases → controllers)
  infra/repositories/      # concrete implementations
    json/                  # JSON-file-backed (permissions, policies)
    in_memory/             # dict-backed (users, roles, refresh tokens)
  infra/core/              # config, logging, middleware, seed
```

## Dependencies at a Glance

| Layer | Depends On | Knows About |
|---|---|---|
| `domain/entities` | nothing | Business rules (validation, behavior) |
| `application/use_cases` | `domain/entities`, `interface/repository` | Orchestration, request/response DTOs |
| `interface/controller` | `application/use_cases`, `interface/dto` | HTTP (FastAPI decorators, Depends) |
| `interface/dependencies` | `infra/repositories`, `application/use_cases` | Wiring (which impl to inject) |
| `infra/repositories` | `interface/repository` | Storage (JSON, dict, SQLAlchemy, etc.) |

## Testing

### Structure

```
tests/
  conftest.py              # shared fixtures (test_client, admin_token)
  test_main.py             # ping endpoint
  unit/
    test_domain_entities.py       # entity creation, validation, behavior
    test_in_memory_repositories.py # repo CRUD, pagination, edge cases
  integration/
    test_auth.py           # login, /me, token validation
    test_users.py          # user CRUD, role assign/remove via API
    test_roles.py          # role CRUD, permission assign/remove via API
```

### Fixtures (`tests/conftest.py`)

| Fixture | Scope | What it provides |
|---|---|---|
| `test_client` | session | `TestClient(app)` — lifespan runs once, seeding in-memory repos |
| `admin_token` | session | Bearer token for admin user (from seeded data) |

### Key patterns

- **Unit tests** instantiate repos directly (`InMemoryUserRepository()`), no DI involved
- **Integration tests** go through the full FastAPI stack via `test_client`, using `admin_token` for auth
- **`@pytest.mark.asyncio`** required for any test method calling `async` repo methods
- **`asyncio_mode = "auto"`** in `pyproject.toml` — test files matching `test_*.py` get auto event loop
- Repos are **session-scoped singletons** (from `app/infra/repositories/in_memory/registry.py`). Tests that modify data affect all tests in the session — design integration tests to create/fetch their own data rather than depending on existing state

### Writing a new integration test

```python
def test_create_role(test_client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = test_client.post("/api/roles/", headers=headers, json={"name": "Viewer"})
    assert response.status_code == 200
    assert response.json()["payload"]["name"] == "Viewer"
```

### Gotchas

- **Loguru I/O warning on exit** — harmless, filtered in conftest.py
- **Seed data is shared** — the lifespan seeds 1 admin user + 1 admin role. Tests should create additional data rather than mutate the seed
- **`datetime.utcnow()` deprecation** — pre-existing in the codebase, `datetime.now(datetime.UTC)` is the Python 3.12+ replacement

## Gotchas

- **alembic.ini sqlalchemy.url** must match `.env` database config (no auto-sync)
- **Permissions** stored in `statics/permissions.json` (not database-backed)
- **asyncio_mode = "auto"** in pytest config (no manual event loop handling)
- **No lint/typecheck** configured (Makefile `lint` target is just py_compile)
- **Seed scripts** both create admin/admin@example.com/Secret123 with "Admin" role + super:user permission
- **In-memory repos** are process-scoped singletons — seeding and serving must happen in the same process (auto-seeded via FastAPI lifespan)

## DB Setup Sequence

Requires PostgreSQL running: `make init-db` (or manually: create-db → upgrade → seed)

## Seeding

- `make seed` — prompts to choose database or in-memory
- `make seed-db` — seeds into PostgreSQL (requires DB setup)
- `make seed-mem` — seeds into in-memory repos (no DB needed)
- In-memory seeding happens **automatically on `make dev`** via FastAPI lifespan event
