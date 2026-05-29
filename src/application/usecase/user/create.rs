use std::sync::Arc;

use async_trait::async_trait;

use crate::application::error::AppError;
use crate::application::usecase::user::{RoleRepository, UserRepository};
use crate::domain;

pub struct CreateUserInput {
    pub name: String,
    pub email: String,
    pub phone: String,
    pub password: String,
    pub role_ids: Vec<String>,
}

pub struct CreateUserOutput {
    pub user: domain::User,
}

#[async_trait]
pub trait CreateUserUseCase: Send + Sync {
    async fn execute(&self, input: CreateUserInput) -> Result<CreateUserOutput, AppError>;
}

pub struct CreateUserUseCaseImpl {
    user_repo: Arc<dyn UserRepository>,
    role_repo: Arc<dyn RoleRepository>,
}

impl CreateUserUseCaseImpl {
    pub fn new(user_repo: Arc<dyn UserRepository>, role_repo: Arc<dyn RoleRepository>) -> Self {
        CreateUserUseCaseImpl {
            user_repo,
            role_repo,
        }
    }
}

#[async_trait]
impl CreateUserUseCase for CreateUserUseCaseImpl {
    async fn execute(&self, input: CreateUserInput) -> Result<CreateUserOutput, AppError> {
        let mut user = domain::User::new(input.name, input.email, input.phone, input.role_ids)?;
        user.set_password(&input.password)?;

        let existing = self.user_repo.find_by_email(&user.email).await;
        if existing.is_ok() {
            return Err(AppError::from(domain::Error::AlreadyExists));
        }

        super::helpers::validate_role_ids(&*self.role_repo, &user.role_ids).await?;

        self.user_repo.create(&user).await?;
        Ok(CreateUserOutput { user })
    }
}
