use std::sync::Arc;

use async_trait::async_trait;

use crate::application::error::AppError;
use crate::application::usecase::user::RoleRepository;
use crate::domain;

pub struct CreateRoleInput {
    pub name: String,
    pub description: String,
}

pub struct CreateRoleOutput {
    pub role: domain::Role,
}

#[async_trait]
pub trait CreateRoleUseCase: Send + Sync {
    async fn execute(&self, input: CreateRoleInput) -> Result<CreateRoleOutput, AppError>;
}

pub struct CreateRoleUseCaseImpl {
    role_repo: Arc<dyn RoleRepository>,
}

impl CreateRoleUseCaseImpl {
    pub fn new(role_repo: Arc<dyn RoleRepository>) -> Self {
        CreateRoleUseCaseImpl { role_repo }
    }
}

#[async_trait]
impl CreateRoleUseCase for CreateRoleUseCaseImpl {
    async fn execute(&self, input: CreateRoleInput) -> Result<CreateRoleOutput, AppError> {
        let role = domain::Role::new(input.name, input.description)?;

        let existing = self.role_repo.find_by_name(&role.name).await;
        if existing.is_ok() {
            return Err(AppError::from(domain::Error::AlreadyExists));
        }

        self.role_repo.create(&role).await?;
        Ok(CreateRoleOutput { role })
    }
}
