use crate::domain::error::Error;
use crate::domain::id::generate_id;
use chrono::{DateTime, Utc};

#[derive(Debug, Clone)]
pub struct Role {
    pub id: String,
    pub name: String,
    pub description: String,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

impl Role {
    pub fn new(name: String, description: String) -> Result<Self, Error> {
        let r = Role {
            id: generate_id(),
            name,
            description,
            created_at: Utc::now(),
            updated_at: Utc::now(),
        };
        r.validate()?;
        Ok(r)
    }

    pub fn update_info(&mut self, name: String, description: String) -> Result<(), Error> {
        self.name = name;
        self.description = description;
        self.updated_at = Utc::now();
        self.validate()
    }

    pub fn validate(&self) -> Result<(), Error> {
        if self.name.trim().is_empty() {
            return Err(Error::InvalidInput("name is required".to_string()));
        }
        Ok(())
    }
}
