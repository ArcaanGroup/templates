use crate::domain::{entities::User, DomainEvent};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UserCreatedEvent {
    pub user_id: uuid::Uuid,
    pub email: String,
    pub timestamp: DateTime<Utc>,
}

impl UserCreatedEvent {
    pub fn new(user: &User) -> Self {
        UserCreatedEvent {
            user_id: user.id,
            email: user.email.as_str().to_string(),
            timestamp: Utc::now(),
        }
    }
}

impl DomainEvent for UserCreatedEvent {
    fn occurred_on(&self) -> DateTime<Utc> {
        self.timestamp
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UserUpdatedEvent {
    pub user_id: uuid::Uuid,
    pub timestamp: DateTime<Utc>,
}

impl UserUpdatedEvent {
    pub fn new(user_id: uuid::Uuid) -> Self {
        UserUpdatedEvent {
            user_id,
            timestamp: Utc::now(),
        }
    }
}

impl DomainEvent for UserUpdatedEvent {
    fn occurred_on(&self) -> DateTime<Utc> {
        self.timestamp
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UserDeletedEvent {
    pub user_id: uuid::Uuid,
    pub timestamp: DateTime<Utc>,
}

impl UserDeletedEvent {
    pub fn new(user_id: uuid::Uuid) -> Self {
        UserDeletedEvent {
            user_id,
            timestamp: Utc::now(),
        }
    }
}

impl DomainEvent for UserDeletedEvent {
    fn occurred_on(&self) -> DateTime<Utc> {
        self.timestamp
    }
}
