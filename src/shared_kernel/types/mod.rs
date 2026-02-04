use serde::{Deserialize, Serialize};
use std::fmt::Debug;

/// Generic result type for the application
pub type Result<T> = std::result::Result<T, Error>;

/// Common error type for the application
#[derive(Debug, thiserror::Error)]
pub enum Error {
    /// Validation error
    #[error("Validation error: {message}")]
    Validation { message: String },

    /// Business rule violation
    #[error("Business rule violation: {message}")]
    BusinessRule { message: String },

    /// Resource not found
    #[error("Resource not found: {resource} with id {id}")]
    NotFound { resource: String, id: String },

    /// Unauthorized access
    #[error("Unauthorized access")]
    Unauthorized,

    /// Forbidden access
    #[error("Access forbidden")]
    Forbidden,

    /// Internal server error
    #[error("Internal server error: {source}")]
    Internal {
        source: Box<dyn std::error::Error + Send + Sync>,
    },
}

impl Error {
    pub fn internal<E>(source: E) -> Self
    where
        E: std::error::Error + Send + Sync + 'static,
    {
        Self::Internal {
            source: Box::new(source),
        }
    }
}
