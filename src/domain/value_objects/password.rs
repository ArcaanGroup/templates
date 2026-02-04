use crate::domain::DomainError;
use bcrypt::{hash, verify, DEFAULT_COST};
use serde::{Deserialize, Serialize};
use std::fmt;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Password(String);

impl Password {
    pub fn new(plain_password: String) -> Result<Self, DomainError> {
        if plain_password.len() < 8 {
            return Err(DomainError::InvalidOperation {
                message: "Password must be at least 8 characters long".to_string(),
            });
        }

        let hashed = hash(plain_password, DEFAULT_COST)
            .map_err(|e| DomainError::Other(anyhow::anyhow!("Failed to hash password: {}", e)))?;

        Ok(Password(hashed))
    }

    pub fn verify(&self, plain_password: &str) -> Result<bool, DomainError> {
        verify(plain_password, &self.0)
            .map_err(|e| DomainError::Other(anyhow::anyhow!("Failed to verify password: {}", e)))
    }

    pub fn hash(&self) -> &str {
        &self.0
    }
}

impl fmt::Display for Password {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "[REDACTED]")
    }
}
