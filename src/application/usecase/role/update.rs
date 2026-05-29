use std::sync::Arc;

use async_trait::async_trait;

use crate::application::error::AppError;
use crate::application::usecase::user::RoleRepository;
use crate::domain;

pub struct UpdateRoleInput {
    pub name: String,
    pub description: String,
}

pub struct UpdateRoleOutput {
    pub role: domain::Role,
}

#[async_trait]
pub trait UpdateRoleUseCase: Send + Sync {
    async fn execute(&self, id: &str, input: UpdateRoleInput) -> Result<UpdateRoleOutput, AppError>;
}

pub struct UpdateRoleUseCaseImpl {
    role_repo: Arc<dyn RoleRepository>,
}

impl UpdateRoleUseCaseImpl {
    pub fn new(role_repo: Arc<dyn RoleRepository>) -> Self {
        UpdateRoleUseCaseImpl { role_repo }
    }
}

#[async_trait]
impl UpdateRoleUseCase for UpdateRoleUseCaseImpl {
    async fn execute(&self, id: &str, input: UpdateRoleInput) -> Result<UpdateRoleOutput, AppError> {
        let mut role = self.role_repo.find_by_id(id).await?;

        if input.name != role.name {
            let existing = self.role_repo.find_by_name(&input.name).await;
            if existing.is_ok() {
                return Err(AppError::from(domain::Error::AlreadyExists));
            }
        }

        role.update_info(input.name, input.description)?;
        self.role_repo.update(&role).await?;
        Ok(UpdateRoleOutput { role })
    }
}
