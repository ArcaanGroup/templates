use crate::domain::DomainError;
use serde::{Deserialize, Serialize};
use std::fmt;
use validator::Validate;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Email(String);

impl Email {
    pub fn new(value: String) -> Result<Self, DomainError> {
        // Basic validation - could be enhanced with regex
        if !value.contains('@') || !value.contains('.') {
            return Err(DomainError::InvalidOperation {
                message: "Invalid email format".to_string(),
            });
        }

        let email = Email(value.to_lowercase());

        // Validate using validator crate
        email
            .validate()
            .map_err(|e| DomainError::InvalidOperation {
                message: format!("Email validation failed: {:?}", e),
            })?;

        Ok(email)
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}

impl fmt::Display for Email {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.0)
    }
}

impl Validate for Email {
    fn validate(&self) -> Result<(), validator::ValidationErrors> {
        // Custom validation logic can be added here
        Ok(())
    }
}

impl AsRef<str> for Email {
    fn as_ref(&self) -> &str {
        &self.0
    }
}
