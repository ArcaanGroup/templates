use std::sync::Arc;

use async_trait::async_trait;

use crate::application::error::AppError;
use crate::application::usecase::user::{RoleRepository, UserRepository};
use crate::domain;

pub struct GetUserRolesInput {
    pub id: String,
}

pub struct GetUserRolesOutput {
    pub roles: Vec<domain::Role>,
}

#[async_trait]
pub trait GetUserRolesUseCase: Send + Sync {
    async fn execute(&self, input: GetUserRolesInput) -> Result<GetUserRolesOutput, AppError>;
}

pub struct GetUserRolesUseCaseImpl {
    user_repo: Arc<dyn UserRepository>,
    role_repo: Arc<dyn RoleRepository>,
}

impl GetUserRolesUseCaseImpl {
    pub fn new(user_repo: Arc<dyn UserRepository>, role_repo: Arc<dyn RoleRepository>) -> Self {
        GetUserRolesUseCaseImpl {
            user_repo,
            role_repo,
        }
    }
}

#[async_trait]
impl GetUserRolesUseCase for GetUserRolesUseCaseImpl {
    async fn execute(&self, input: GetUserRolesInput) -> Result<GetUserRolesOutput, AppError> {
        let user = self.user_repo.find_by_id(&input.id).await?;
        let mut roles = Vec::with_capacity(user.role_ids.len());
        for rid in &user.role_ids {
            if let Ok(role) = self.role_repo.find_by_id(rid).await {
                roles.push(role);
            }
        }
        Ok(GetUserRolesOutput { roles })
    }
}
