pub mod entities;
pub mod value_objects;
pub mod services;
pub mod events;

// Common domain types and traits
use serde::{Deserialize, Serialize};
use std::fmt::Debug;
use uuid::Uuid;

/// Base trait for all domain entities
pub trait Entity: Debug {
    type Id: Debug + Clone;

    fn id(&self) -> &Self::Id;
    fn equals(&self, other: &dyn Entity<Id = Self::Id>) -> bool;
}

/// Base trait for domain events
pub trait DomainEvent: Debug + Send + Sync {
    fn occurred_on(&self) -> chrono::DateTime<chrono::Utc>;
}

/// Result type for domain operations
pub type DomainResult<T> = Result<T, DomainError>;

#[derive(Debug, thiserror::Error)]
pub enum DomainError {
    #[error("Entity not found: {entity} with id {id}")]
    NotFound { entity: String, id: Uuid },

    #[error("Business rule violation: {message}")]
    BusinessRuleViolation { message: String },

    #[error("Invalid operation: {message}")]
    InvalidOperation { message: String },

    #[error(transparent)]
    Other(#[from] anyhow::Error),
}
