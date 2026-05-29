use std::sync::Arc;

use axum::routing::{delete, get, post, put};
use axum::{Json, Router};

use crate::interface::handler::role::RoleHandler;
use crate::interface::handler::user::UserHandler;
use crate::interface::middleware;

pub fn new(user_handler: UserHandler, role_handler: RoleHandler) -> Router {
    let user_handler = Arc::new(user_handler);
    let role_handler = Arc::new(role_handler);

    let user_routes = Router::new()
        .route("/", get(UserHandler::list_all))
        .route("/", post(UserHandler::create))
        .route("/{id}", get(UserHandler::get_by_id))
        .route("/{id}", put(UserHandler::update))
        .route("/{id}", delete(UserHandler::delete))
        .route("/{id}/roles", get(UserHandler::get_roles))
        .route("/{id}/roles", post(UserHandler::assign_roles))
        .with_state(user_handler);

    let role_routes = Router::new()
        .route("/", get(RoleHandler::list_all))
        .route("/", post(RoleHandler::create))
        .route("/{id}", get(RoleHandler::get_by_id))
        .route("/{id}", put(RoleHandler::update))
        .route("/{id}", delete(RoleHandler::delete))
        .with_state(role_handler);

    Router::new()
        .route("/health", get(|| async {
            Json(serde_json::json!({"status": "ok"}))
        }))
        .nest("/api/v1/users", user_routes)
        .nest("/api/v1/roles", role_routes)
        .layer(axum::middleware::from_fn(middleware::request_id))
        .layer(axum::middleware::from_fn(middleware::recover_middleware))
        .layer(axum::middleware::from_fn(middleware::logger_middleware))
        .layer(middleware::cors_layer())
}
