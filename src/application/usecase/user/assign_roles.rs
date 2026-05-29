use std::sync::Arc;

use async_trait::async_trait;

use crate::application::error::AppError;
use crate::application::usecase::user::{RoleRepository, UserRepository};

pub struct AssignRolesInput {
    pub role_ids: Vec<String>,
}

#[async_trait]
pub trait AssignRolesUseCase: Send + Sync {
    async fn execute(&self, id: &str, input: AssignRolesInput) -> Result<(), AppError>;
}

pub struct AssignRolesUseCaseImpl {
    user_repo: Arc<dyn UserRepository>,
    role_repo: Arc<dyn RoleRepository>,
}

impl AssignRolesUseCaseImpl {
    pub fn new(user_repo: Arc<dyn UserRepository>, role_repo: Arc<dyn RoleRepository>) -> Self {
        AssignRolesUseCaseImpl {
            user_repo,
            role_repo,
        }
    }
}

#[async_trait]
impl AssignRolesUseCase for AssignRolesUseCaseImpl {
    async fn execute(&self, id: &str, input: AssignRolesInput) -> Result<(), AppError> {
        let mut user = self.user_repo.find_by_id(id).await?;
        super::helpers::validate_role_ids(&*self.role_repo, &input.role_ids).await?;
        user.assign_roles(input.role_ids);
        self.user_repo.update(&user).await?;
        Ok(())
    }
}
