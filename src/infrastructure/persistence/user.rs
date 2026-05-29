use std::collections::HashMap;
use std::sync::RwLock;

use async_trait::async_trait;

use crate::application::usecase::user::UserRepository;
use crate::domain;

pub struct InMemoryUserRepository {
    users: RwLock<HashMap<String, domain::User>>,
}

impl InMemoryUserRepository {
    pub fn new() -> Self {
        InMemoryUserRepository {
            users: RwLock::new(HashMap::new()),
        }
    }
}

impl Default for InMemoryUserRepository {
    fn default() -> Self {
        Self::new()
    }
}

#[async_trait]
impl UserRepository for InMemoryUserRepository {
    async fn find_by_id(&self, id: &str) -> Result<domain::User, domain::Error> {
        let users = self.users.read().map_err(|_| {
            domain::Error::InvalidInput("lock poisoned".to_string())
        })?;
        match users.get(id) {
            Some(user) if user.deleted_at.is_none() => Ok(user.clone()),
            _ => Err(domain::Error::NotFound),
        }
    }

    async fn find_all(
        &self,
        offset: usize,
        limit: usize,
    ) -> Result<(Vec<domain::User>, i64), domain::Error> {
        let users = self.users.read().map_err(|_| {
            domain::Error::InvalidInput("lock poisoned".to_string())
        })?;
        let mut all: Vec<&domain::User> = users
            .values()
            .filter(|u| u.deleted_at.is_none())
            .collect();
        all.sort_by_key(|a| a.created_at);

        let total = all.len() as i64;
        let slice: Vec<domain::User> = all
            .into_iter()
            .skip(offset)
            .take(limit)
            .cloned()
            .collect();

        Ok((slice, total))
    }

    async fn find_by_email(&self, email: &str) -> Result<domain::User, domain::Error> {
        let users = self.users.read().map_err(|_| {
            domain::Error::InvalidInput("lock poisoned".to_string())
        })?;
        for user in users.values() {
            if user.deleted_at.is_none() && user.email == email {
                return Ok(user.clone());
            }
        }
        Err(domain::Error::NotFound)
    }

    async fn create(&self, user: &domain::User) -> Result<(), domain::Error> {
        let mut users = self.users.write().map_err(|_| {
            domain::Error::InvalidInput("lock poisoned".to_string())
        })?;
        users.insert(user.id.clone(), user.clone());
        Ok(())
    }

    async fn update(&self, user: &domain::User) -> Result<(), domain::Error> {
        let mut users = self.users.write().map_err(|_| {
            domain::Error::InvalidInput("lock poisoned".to_string())
        })?;
        if !users.contains_key(&user.id) {
            return Err(domain::Error::NotFound);
        }
        users.insert(user.id.clone(), user.clone());
        Ok(())
    }

    async fn delete(&self, id: &str) -> Result<(), domain::Error> {
        let mut users = self.users.write().map_err(|_| {
            domain::Error::InvalidInput("lock poisoned".to_string())
        })?;
        match users.get_mut(id) {
            Some(user) if user.deleted_at.is_none() => {
                user.mark_deleted();
                Ok(())
            }
            _ => Err(domain::Error::NotFound),
        }
    }
}
