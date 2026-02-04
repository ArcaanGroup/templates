use crate::domain::entities::User;
use crate::domain::services::UserRepository;
use crate::domain::value_objects::Email;
use crate::domain::DomainResult;
use async_trait::async_trait;
use std::collections::HashMap;
use std::sync::{Arc, RwLock};
use tracing;
use uuid::Uuid;

#[derive(Clone)]
pub struct InMemoryUserRepository {
    users: Arc<RwLock<HashMap<Uuid, User>>>,
    email_index: Arc<RwLock<HashMap<String, Uuid>>>,
}

impl InMemoryUserRepository {
    pub fn new() -> Self {
        Self {
            users: Arc::new(RwLock::new(HashMap::new())),
            email_index: Arc::new(RwLock::new(HashMap::new())),
        }
    }
}

#[async_trait]
impl UserRepository for InMemoryUserRepository {
    async fn find_by_id(&self, id: Uuid) -> DomainResult<User> {
        tracing::debug!("Finding user by ID: {}", id);
        let users = self.users.read().unwrap();
        if let Some(user) = users.get(&id) {
            if user.is_active {
                tracing::debug!("Found active user with ID: {}", id);
                Ok(user.clone())
            } else {
                tracing::debug!("User with ID {} is inactive", id);
                Err(crate::domain::DomainError::NotFound {
                    entity: "User".to_string(),
                    id,
                })
            }
        } else {
            tracing::debug!("User with ID {} not found", id);
            Err(crate::domain::DomainError::NotFound {
                entity: "User".to_string(),
                id,
            })
        }
    }

    async fn find_by_email(&self, email: &str) -> DomainResult<User> {
        tracing::debug!("Finding user by email: {}", email);
        let email_index = self.email_index.read().unwrap();
        if let Some(user_id) = email_index.get(email) {
            let users = self.users.read().unwrap();
            if let Some(user) = users.get(user_id) {
                if user.is_active {
                    tracing::debug!("Found active user with email: {}", email);
                    Ok(user.clone())
                } else {
                    tracing::debug!("User with email {} is inactive", email);
                    Err(crate::domain::DomainError::NotFound {
                        entity: "User".to_string(),
                        id: *user_id,
                    })
                }
            } else {
                tracing::debug!("User with email {} not found in users map", email);
                Err(crate::domain::DomainError::NotFound {
                    entity: "User".to_string(),
                    id: *user_id,
                })
            }
        } else {
            tracing::debug!("No user found with email: {}", email);
            Err(crate::domain::DomainError::NotFound {
                entity: "User".to_string(),
                id: Uuid::nil(), // We don't have the ID here
            })
        }
    }

    async fn save(&self, user: User) -> DomainResult<()> {
        tracing::debug!(
            "Saving user with ID: {} and email: {}",
            user.id,
            user.email.as_str()
        );
        let mut users = self.users.write().unwrap();
        let mut email_index = self.email_index.write().unwrap();

        // Remove old email index if user already exists
        if let Some(existing_user) = users.get(&user.id) {
            email_index.remove(existing_user.email.as_str());
            tracing::debug!(
                "Removed old email index for user: {}",
                existing_user.email.as_str()
            );
        }

        // Add/update user
        users.insert(user.id, user.clone());

        // Update email index
        email_index.insert(user.email.as_str().to_string(), user.id);
        tracing::debug!("Successfully saved user with ID: {}", user.id);

        Ok(())
    }

    async fn delete(&self, id: Uuid) -> DomainResult<()> {
        tracing::info!("Deleting user with ID: {}", id);
        let mut users = self.users.write().unwrap();
        if let Some(mut user) = users.get_mut(&id) {
            // Create a new user with is_active = false
            let mut updated_user = user.clone();
            updated_user.is_active = false;
            users.insert(id, updated_user);
            tracing::info!("Successfully marked user as deleted: {}", id);
            Ok(())
        } else {
            tracing::warn!("Attempt to delete non-existent user with ID: {}", id);
            Err(crate::domain::DomainError::NotFound {
                entity: "User".to_string(),
                id,
            })
        }
    }
}
