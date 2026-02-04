use crate::domain::{
    value_objects::{Email, Password},
    Entity,
};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::fmt::Debug;
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct User {
    pub id: Uuid,
    pub email: Email,
    pub password: Password,
    pub username: String,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    pub is_active: bool,
}

impl User {
    pub fn new(
        email: Email,
        password: Password,
        username: String,
    ) -> Result<Self, crate::domain::DomainError> {
        Ok(User {
            id: Uuid::new_v4(),
            email,
            password,
            username,
            created_at: Utc::now(),
            updated_at: Utc::now(),
            is_active: true,
        })
    }

    pub fn deactivate(&mut self) {
        self.is_active = false;
        self.updated_at = Utc::now();
    }

    pub fn activate(&mut self) {
        self.is_active = true;
        self.updated_at = Utc::now();
    }

    pub fn change_email(&mut self, new_email: Email) {
        self.email = new_email;
        self.updated_at = Utc::now();
    }
}

impl Entity for User {
    type Id = Uuid;

    fn id(&self) -> &Self::Id {
        &self.id
    }

    fn equals(&self, other: &dyn Entity<Id = Self::Id>) -> bool {
        self.id() == other.id()
    }
}
