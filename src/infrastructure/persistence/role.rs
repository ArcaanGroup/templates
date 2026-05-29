use std::collections::HashMap;
use std::sync::RwLock;

use async_trait::async_trait;

use crate::application::usecase::user::RoleRepository;
use crate::domain;

pub struct InMemoryRoleRepository {
    roles: RwLock<HashMap<String, domain::Role>>,
}

impl InMemoryRoleRepository {
    pub fn new() -> Self {
        InMemoryRoleRepository {
            roles: RwLock::new(HashMap::new()),
        }
    }
}

impl Default for InMemoryRoleRepository {
    fn default() -> Self {
        Self::new()
    }
}

#[async_trait]
impl RoleRepository for InMemoryRoleRepository {
    async fn find_by_id(&self, id: &str) -> Result<domain::Role, domain::Error> {
        let roles = self.roles.read().map_err(|_| {
            domain::Error::InvalidInput("lock poisoned".to_string())
        })?;
        match roles.get(id) {
            Some(role) => Ok(role.clone()),
            None => Err(domain::Error::NotFound),
        }
    }

    async fn find_all(
        &self,
        offset: usize,
        limit: usize,
    ) -> Result<(Vec<domain::Role>, i64), domain::Error> {
        let roles = self.roles.read().map_err(|_| {
            domain::Error::InvalidInput("lock poisoned".to_string())
        })?;
        let mut all: Vec<&domain::Role> = roles.values().collect();
        all.sort_by_key(|a| a.created_at);

        let total = all.len() as i64;
        let slice: Vec<domain::Role> = all
            .into_iter()
            .skip(offset)
            .take(limit)
            .cloned()
            .collect();

        Ok((slice, total))
    }

    async fn find_by_name(&self, name: &str) -> Result<domain::Role, domain::Error> {
        let roles = self.roles.read().map_err(|_| {
            domain::Error::InvalidInput("lock poisoned".to_string())
        })?;
        for role in roles.values() {
            if role.name == name {
                return Ok(role.clone());
            }
        }
        Err(domain::Error::NotFound)
    }

    async fn create(&self, role: &domain::Role) -> Result<(), domain::Error> {
        let mut roles = self.roles.write().map_err(|_| {
            domain::Error::InvalidInput("lock poisoned".to_string())
        })?;
        roles.insert(role.id.clone(), role.clone());
        Ok(())
    }

    async fn update(&self, role: &domain::Role) -> Result<(), domain::Error> {
        let mut roles = self.roles.write().map_err(|_| {
            domain::Error::InvalidInput("lock poisoned".to_string())
        })?;
        if !roles.contains_key(&role.id) {
            return Err(domain::Error::NotFound);
        }
        roles.insert(role.id.clone(), role.clone());
        Ok(())
    }

    async fn delete(&self, id: &str) -> Result<(), domain::Error> {
        let mut roles = self.roles.write().map_err(|_| {
            domain::Error::InvalidInput("lock poisoned".to_string())
        })?;
        if roles.remove(id).is_none() {
            return Err(domain::Error::NotFound);
        }
        Ok(())
    }
}
