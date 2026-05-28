# go-clean-template — agent guide

## Architecture

Clean Architecture with strict inward dependency rule:

```
domain  ←  application  ←  interface  ←  infrastructure
```

- `domain/` — entities, repository interfaces, domain errors. Zero imports outside stdlib. Entities own all validation (`Validate()`, `SetPassword()`, etc.).
- `application/` — use cases (business logic). Depends only on domain. Orchestrates only — zero validation logic, zero `DomainError` construction.
- `interface/` — HTTP handlers, middleware, DTOs, chi router. Depends on application. DTOs (`internal/interface/dto/`) hold serialization tags; handlers decode into DTOs, map to use case inputs, unwrap outputs, convert domain entities to response DTOs.
- `infrastructure/` — concrete repository implementations, logger. Depends on domain.
- `cmd/main.go` — DI wiring point. Only place where all layers are imported together.
- `tests/` — external test packages (`user_test`, `role_test`, `handler_test`) mirroring the source tree; mock types are exported (`MockUserRepo`, `MockCreateUserUseCase`) for cross-package access.

## Use case segregation (ISP)

Each use case is a standalone module with its own file, following the Interface
Segregation Principle. Use cases are grouped by entity in subdirectories:

```
internal/application/usecase/
├── user/
│   ├── create.go          # CreateUserInput, CreateUserOutput, CreateUserUseCase
│   ├── get.go             # GetUserInput, GetUserOutput, GetUserUseCase
│   ├── list.go            # ListUsersInput, ListUsersOutput, ListUsersUseCase
│   ├── update.go          # UpdateUserInput, UpdateUserOutput, UpdateUserUseCase
│   ├── delete.go          # DeleteUserInput, DeleteUserUseCase
│   ├── assign_roles.go    # AssignRolesInput, AssignRolesUseCase
│   ├── get_roles.go       # GetUserRolesInput, GetUserRolesOutput, GetUserRolesUseCase
│   └── helpers.go         # shared orchestration helpers (e.g. validateRoleIDs)
├── role/
│   ├── create.go
│   ├── get.go
│   ├── list.go
│   ├── update.go
│   ├── delete.go
│   └── helpers.go
```

Every use case follows the same signature pattern:
`Execute(ctx context.Context, input *XxxInput) (*XxxOutput, error)`.

Request DTOs (`XxxInput`) are co-located with their use case. Output types always
wrap domain entities in a named struct (`CreateUserOutput{User *domain.User}`).
Handler layer owns all domain→DTO mapping via `toUserResponse()`/`toRoleResponse()`
helpers in `internal/interface/handler/helpers.go`. Presentation DTOs
(`UserResponse`, `RoleResponse`) live in `internal/interface/dto/`.

```go
// Handler flow:
var reqDTO dto.CreateUserRequest
json.NewDecoder(r.Body).Decode(&reqDTO)
result, _ := createUC.Execute(ctx, &usecase.CreateUserInput{
    Name:     reqDTO.Name,
    Email:    reqDTO.Email,
    Password: reqDTO.Password,
})
writeJSON(w, http.StatusCreated, toUserResponse(result.User))
```

## Adding a new feature (e.g. a new entity)

Touch every layer in order:
1. **domain** — entity struct (with `Validate()` method), repository interface, domain errors
2. **application/usecase/<entity>/** — one file per use case operation (create, get, list, update, delete, …). Each file contains `XxxInput`, `XxxOutput`, use case interface, implementation, and constructor. Use cases orchestrate only — no validation logic.
3. **interface/dto** — request DTOs (`CreateXxxRequest`) with `json` tags, response DTOs (`XxxResponse`)
4. **interface/handler** — HTTP handlers; inject individual use case interfaces (not a fat "service" interface); write DTO mapping helpers
5. **interface/router** — register new routes on chi
6. **infrastructure/persistence** — concrete repository (in-memory, thread-safe with `sync.RWMutex`)
7. **infrastructure/seed** — add seed data in `internal/infrastructure/seed/seed.go`
8. **cmd/main.go** — wire each use case individually, then the handler; `seed.Run` is called automatically on startup
9. **tests/** — add external test packages at `tests/application/usecase/<entity>/` and `tests/interface/handler/`

## Testing patterns

All tests live in `tests/` as external test packages (`package user_test`, `package handler_test`).
Mock types are exported (capitalized) to be accessible across packages.

- **Use case tests** (`tests/application/usecase/<entity>/`) — mock `domain.XxxRepository` with exported `MockXxxRepo` types and `testify/mock`. Shared mocks live in `mocks_test.go` within each test directory.
- **Handler tests** (`tests/interface/handler/`) — mock individual use case interfaces (e.g. `MockCreateUserUseCase`) with `testify/mock`, use `httptest`. Each handler test only wires the specific use case it exercises via `handler.NewUserHandler(mockUC, nil, nil, ...)`.
- Repository tests are omitted from the template (require DB); in-memory repo is trivially correct.

Run: `go test -v -coverprofile=coverage.out -covermode=atomic ./...` (no `-race` flag — CGO may be disabled on Windows).

## Swagger

- Annotations live on handler methods (`internal/interface/handler/`) and DTOs (`internal/interface/dto/`).
- `make swag` regenerates `docs/` from annotations using `swaggo/swag`.
- `make build` and `make run` expect `docs/` to exist (checked in; regenerate with `make swag`).
- `docs/docs.go` may need manual patching if generated CLI version diverges from the library.
- Raw OpenAPI spec served at `GET /openapi.json` (for codegen tools like orval).
- Swagger UI served at `GET /swagger/`. Resolves relative to `/swagger/doc.json`.
- When adding a new handler, add swagger operation annotations to its method.
- `@Param body` annotations must reference DTO types (`dto.CreateUserRequest`), not use case input types.

## Key conventions

- **ID generation** — `crypto/rand` hex in `generateID()` at `internal/domain/id.go`. No external UUID library.
- **Error flow** — domain errors (`ErrNotFound`, `ErrAlreadyExists`, `ErrInvalidInput`) propagate through all layers. Handlers map them to HTTP status codes via `errors.Is`/`errors.As`. Use cases never construct `DomainError` — only domain entities and repositories do.
- **Entity validation** — `Validate()` method on domain entities returns `*DomainError` wrapping `ErrInvalidInput`. Password validation and hashing lives in `User.SetPassword()`, not in the use case.
- **Use case purity** — use cases orchestrate: call domain constructors → call repo methods → propagate errors. No `if x == "" { return error }` patterns. Empty-string ID checks are naturally handled by `FindByID("")` → `ErrNotFound`.
- **DTO mapping** — handlers decode HTTP into `dto.XxxRequest`, map field-by-field to `usecase.XxxInput`, call use case, unwrap `result.Xxx` domain entity, convert to response DTO via `toXxxResponse()`. JSON tags live only on `dto/` types — use case input structs are tag-free.
- **Output types** — every use case defines a named `XxxOutput` struct, even for single-entity returns (e.g. `GetUserOutput{User *domain.User}`). Consistency over brevity.
- **Logging** — `slog` JSON handler. Middleware logs every request with method, path, status, duration, request_id.
- **Router** — `chi/v5`. URL params via `chi.URLParam(r, "id")`.
- **Middleware order** — RequestID → Recoverer → Logger → CORS (defined in `internal/interface/router/router.go:16-19`).
- **Dependencies** — `chi/v5`, `testify`, and `swaggo/http-swagger` (for Swagger UI). Domain layer is pure stdlib.
- **Handler constructor** — each handler receives individual use case interfaces; `nil` may be passed for unused use cases in tests that only exercise one handler method.

## Commands

| Command | What it does |
|---|---|---|
| `make run` | `go run ./cmd/main.go` — starts server on `:8080` |
| `make test` | runs all tests with coverage |
| `make lint` | `golangci-lint run ./...` |
| `make build` | `go build -ldflags="-s -w" -o ./bin/go-clean-template ./cmd/main.go` |
| `make init` | `go run ./cmd/init/main.go` — interactive bootstrap CLI |
| `make seed` | `go run ./cmd/seed/main.go` — seed initial data (idempotent) |
| `go vet ./...` | pre-commit check |

## Bootstrap CLI (`cmd/init/`)

Interactive CLI with two commands:

- **`init`** — Renames the Go module across all files (`go.mod`, `.go`, `.md`, `.yaml`, etc.). Prompts for new module name then walks the tree with `filepath.Walk`, skipping `.git`/`bin`/`tmp`/`.tools`.
- **`generate`** — Scaffolds a full CRUD entity across all layers (16 files created, 5 existing files modified):
  - `internal/domain/<entity>.go` — entity struct, `NewEntity`, `Validate()`, repository interface
  - `internal/application/usecase/<entity>/` — 5 use case files (create, get, list, update, delete)
  - `internal/interface/dto/<entity>.go` — request/response DTOs with json tags
  - `internal/interface/handler/<entity>.go` — HTTP CRUD handlers
  - `internal/infrastructure/persistence/<entity>.go` — in-memory repo with `sync.RWMutex`
  - `tests/application/usecase/<entity>/` — 6 test files (create, get, list, update, delete, mocks)
  - `tests/interface/handler/<entity>_test.go` — handler tests with mock use cases
  - **Modifies**: `cmd/main.go`, `cmd/seed/main.go`, `router.go`, `seed.go`, `helpers.go`

The generator uses Go `text/template` with a `bt` helper function (`{{bt}}`) for backtick injection in generated test code.

## Seed conventions

- **Single entry point** — `seed.Run(ctx, log, roleRepo, userRepo)` in `internal/infrastructure/seed/seed.go`
- **Idempotent** — checks for existing data via repository `FindAll` before creating; safe to run multiple times
- **Ordered** — seeds parent entities first (e.g. roles before users that reference them)
- **Standalone command** — `make seed` runs a dedicated `cmd/seed/main.go` entry point, identical logic
- **Auto-seeded on startup** — `cmd/main.go` calls `seed.Run` after repository construction, before the HTTP server starts
- **Infrastructure layer** — depends only on `domain` repository interfaces, not on use cases or handlers

## Replacing the in-memory repository

1. Implement the `domain.XxxRepository` interface in `internal/infrastructure/persistence/`
2. Swap the constructor call in `cmd/main.go`
3. Use cases and handlers need zero changes — they depend on the interface only.
