pub mod dtos;
pub mod ports;
pub mod usecases;

use serde::{Deserialize, Serialize};
use std::fmt::Debug;

// Common application layer types
pub type ApplicationResult<T> = Result<T, ApplicationError>;

#[derive(Debug, thiserror::Error)]
pub enum ApplicationError {
    #[error("Domain error: {0}")]
    Domain(#[from] crate::domain::DomainError),

    #[error("Validation error: {message}")]
    Validation { message: String },

    #[error("Authentication error: {message}")]
    Authentication { message: String },

    #[error("Authorization error: {message}")]
    Authorization { message: String },

    #[error(transparent)]
    Other(#[from] anyhow::Error),
}
