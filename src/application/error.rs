use crate::domain;
use axum::http::StatusCode;
use axum::response::{IntoResponse, Response};
use axum::Json;

#[derive(Debug)]
pub enum AppError {
    NotFound,
    AlreadyExists,
    InvalidInput(String),
    Internal(anyhow::Error),
}

impl std::fmt::Display for AppError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            AppError::NotFound => write!(f, "not found"),
            AppError::AlreadyExists => write!(f, "already exists"),
            AppError::InvalidInput(msg) => write!(f, "{}", msg),
            AppError::Internal(e) => write!(f, "{}", e),
        }
    }
}

impl std::error::Error for AppError {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        match self {
            AppError::Internal(e) => Some(e.as_ref()),
            _ => None,
        }
    }
}

impl From<domain::Error> for AppError {
    fn from(e: domain::Error) -> Self {
        match e {
            domain::Error::NotFound => AppError::NotFound,
            domain::Error::AlreadyExists => AppError::AlreadyExists,
            domain::Error::InvalidInput(msg) => AppError::InvalidInput(msg),
        }
    }
}

impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        let (status, msg) = match &self {
            AppError::NotFound => (StatusCode::NOT_FOUND, "not found".to_string()),
            AppError::AlreadyExists => (StatusCode::CONFLICT, "already exists".to_string()),
            AppError::InvalidInput(m) => (StatusCode::BAD_REQUEST, m.clone()),
            AppError::Internal(_) => {
                (StatusCode::INTERNAL_SERVER_ERROR, "internal server error".to_string())
            }
        };
        let body = serde_json::json!({"error": msg});
        (status, Json(body)).into_response()
    }
}
