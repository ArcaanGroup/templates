use std::sync::Arc;

use async_trait::async_trait;

use crate::application::error::AppError;
use crate::application::usecase::user::{RoleRepository, UserRepository};
use crate::domain;

pub struct UpdateUserInput {
    pub name: String,
    pub email: String,
    pub phone: String,
    pub avatar: String,
    pub role_ids: Vec<String>,
}

pub struct UpdateUserOutput {
    pub user: domain::User,
}

#[async_trait]
pub trait UpdateUserUseCase: Send + Sync {
    async fn execute(&self, id: &str, input: UpdateUserInput) -> Result<UpdateUserOutput, AppError>;
}

pub struct UpdateUserUseCaseImpl {
    user_repo: Arc<dyn UserRepository>,
    role_repo: Arc<dyn RoleRepository>,
}

impl UpdateUserUseCaseImpl {
    pub fn new(user_repo: Arc<dyn UserRepository>, role_repo: Arc<dyn RoleRepository>) -> Self {
        UpdateUserUseCaseImpl {
            user_repo,
            role_repo,
        }
    }
}

#[async_trait]
impl UpdateUserUseCase for UpdateUserUseCaseImpl {
    async fn execute(&self, id: &str, input: UpdateUserInput) -> Result<UpdateUserOutput, AppError> {
        let mut user = self.user_repo.find_by_id(id).await?;

        if input.email != user.email {
            let existing = self.user_repo.find_by_email(&input.email).await;
            if existing.is_ok() {
                return Err(AppError::from(domain::Error::AlreadyExists));
            }
        }

        super::helpers::validate_role_ids(&*self.role_repo, &input.role_ids).await?;

        user.update_info(input.name, input.email, input.phone, input.avatar, input.role_ids)?;
        self.user_repo.update(&user).await?;
        Ok(UpdateUserOutput { user })
    }
}
