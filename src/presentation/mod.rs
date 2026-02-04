use crate::application::usecases::CreateUserUsecase;
use crate::infrastructure::middleware::logging_middleware;
use crate::infrastructure::repositories::InMemoryUserRepository;
use axum::{
    extract::State,
    http::StatusCode,
    middleware,
    response::Json,
    routing::{get, post},
    Router,
};
use serde_json::json;
use std::sync::Arc;
use uuid::Uuid;

pub fn create_app(user_usecase: Arc<CreateUserUsecase<InMemoryUserRepository>>) -> Router {
    Router::new()
        .route("/health", get(health_handler))
        .route("/users", post(create_user_handler))
        .route("/users/:id", get(get_user_handler))
        .with_state(user_usecase)
        .layer(middleware::from_fn(logging_middleware))
}

async fn health_handler() -> Json<serde_json::Value> {
    Json(json!({
        "status": "healthy",
        "timestamp": chrono::Utc::now().to_rfc3339()
    }))
}

async fn create_user_handler(
    State(usecase): State<Arc<CreateUserUsecase<InMemoryUserRepository>>>,
    Json(payload): Json<crate::application::dtos::CreateUserRequest>,
) -> Result<Json<crate::application::dtos::GetUserResponse>, StatusCode> {
    match usecase.execute(payload).await {
        Ok(user) => Ok(Json(user)),
        Err(_) => Err(StatusCode::INTERNAL_SERVER_ERROR),
    }
}

async fn get_user_handler(
    State(_usecase): State<Arc<CreateUserUsecase<InMemoryUserRepository>>>,
    axum::extract::Path(_id): axum::extract::Path<Uuid>,
) -> Result<Json<crate::application::dtos::GetUserResponse>, StatusCode> {
    // Implementation would go here
    Err(StatusCode::NOT_IMPLEMENTED)
}
