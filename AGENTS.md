# rust-clean-template — Rust version

## Architecture

Clean Architecture with strict inward dependency rule:

```
domain  ←  application  ←  interface  ←  infrastructure
```

- `domain/` — entities, domain errors. Zero external dependencies.
- `application/` — use cases (business logic), repository traits. Depends on domain.
- `interface/` — HTTP handlers, middleware, DTOs, axum router. Depends on application.
- `infrastructure/` — concrete repository implementations, logger, config. Depends on domain.
- `src/main.rs` — DI wiring point. Only place where all layers are imported together.

## Module structure

```
src/
├── main.rs
├── domain/
│   ├── mod.rs
│   ├── error.rs       # Error enum (NotFound, AlreadyExists, InvalidInput)
│   ├── id.rs          # generate_id()
│   ├── user.rs        # User entity, UserRepository trait (via domain)
│   └── role.rs        # Role entity, RoleRepository trait (via domain)
├── application/
│   ├── mod.rs
│   ├── error.rs       # AppError (application-level error type)
│   └── usecase/
│       ├── mod.rs
│       ├── user/      # Create, Get, List, Update, Delete, AssignRoles, GetUserRoles
│       └── role/      # Create, Get, List, Update, Delete
├── interface/
│   ├── mod.rs
│   ├── dto/           # Request/Response DTOs with serialization
│   ├── handler/       # HTTP handlers, helpers, error-to-response mapping
│   ├── middleware/    # Axum middleware (request_id, logger, recoverer, CORS)
│   └── router.rs     # Router construction
└── infrastructure/
    ├── mod.rs
    ├── config.rs      # Environment-based configuration
    ├── logger.rs      # Tracing-based structured logger
    ├── persistence/   # In-memory repos (UserRepository, RoleRepository)
    └── seed.rs        # Seed initial data
```

## Use case segregation (ISP)

Each use case is a standalone module with its own file:
- `src/application/usecase/user/create.rs` — `CreateUserInput`, `CreateUserOutput`, `CreateUserUseCase` trait + impl
- Same pattern for get, list, update, delete, assign_roles, get_roles

Every use case follows `async fn execute(&self, input: XxxInput) -> Result<XxxOutput, AppError>`.

Repository traits are also in the application layer and use `#[async_trait]`:
```rust
#[async_trait]
pub trait UserRepository: Send + Sync {
    async fn find_by_id(&self, id: &str) -> Result<User, domain::Error>;
    async fn find_all(&self, offset: usize, limit: usize) -> Result<(Vec<User>, i64), domain::Error>;
    // ...
}
```

## Key patterns

- **Handler flow**: Request → DTO decode → Use case input → Use case execute → Output → Response DTO
- **Error mapping**: `AppError` implements `IntoResponse` for axum, mapping domain errors to HTTP status codes
- **State management**: Each handler group gets its own `Arc<Handler>` as axum state via `.with_state()`
- **ID generation**: `rand` crate, UUID-like format (`xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

## Commands

| Command | What it does |
|---|---|
| `cargo run` | Starts server on `:8080` |
| `cargo test` | Runs all tests |
| `cargo clippy` | Lints the project |
| `cargo build --release` | Production build |
