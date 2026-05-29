use std::sync::Arc;

use async_trait::async_trait;

use crate::application::error::AppError;
use crate::application::usecase::user::RoleRepository;
use crate::domain;

pub struct GetRoleInput {
    pub id: String,
}

pub struct GetRoleOutput {
    pub role: domain::Role,
}

#[async_trait]
pub trait GetRoleUseCase: Send + Sync {
    async fn execute(&self, input: GetRoleInput) -> Result<GetRoleOutput, AppError>;
}

pub struct GetRoleUseCaseImpl {
    role_repo: Arc<dyn RoleRepository>,
}

impl GetRoleUseCaseImpl {
    pub fn new(role_repo: Arc<dyn RoleRepository>) -> Self {
        GetRoleUseCaseImpl { role_repo }
    }
}

#[async_trait]
impl GetRoleUseCase for GetRoleUseCaseImpl {
    async fn execute(&self, input: GetRoleInput) -> Result<GetRoleOutput, AppError> {
        let role = self.role_repo.find_by_id(&input.id).await?;
        Ok(GetRoleOutput { role })
    }
}
