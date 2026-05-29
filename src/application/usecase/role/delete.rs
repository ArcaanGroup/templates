use std::sync::Arc;

use async_trait::async_trait;

use crate::application::error::AppError;
use crate::application::usecase::user::RoleRepository;

pub struct DeleteRoleInput {
    pub id: String,
}

#[async_trait]
pub trait DeleteRoleUseCase: Send + Sync {
    async fn execute(&self, input: DeleteRoleInput) -> Result<(), AppError>;
}

pub struct DeleteRoleUseCaseImpl {
    role_repo: Arc<dyn RoleRepository>,
}

impl DeleteRoleUseCaseImpl {
    pub fn new(role_repo: Arc<dyn RoleRepository>) -> Self {
        DeleteRoleUseCaseImpl { role_repo }
    }
}

#[async_trait]
impl DeleteRoleUseCase for DeleteRoleUseCaseImpl {
    async fn execute(&self, input: DeleteRoleInput) -> Result<(), AppError> {
        self.role_repo.find_by_id(&input.id).await?;
        self.role_repo.delete(&input.id).await?;
        Ok(())
    }
}
