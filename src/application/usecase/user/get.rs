use std::sync::Arc;

use async_trait::async_trait;

use crate::application::error::AppError;
use crate::application::usecase::user::UserRepository;
use crate::domain;

pub struct GetUserInput {
    pub id: String,
}

pub struct GetUserOutput {
    pub user: domain::User,
}

#[async_trait]
pub trait GetUserUseCase: Send + Sync {
    async fn execute(&self, input: GetUserInput) -> Result<GetUserOutput, AppError>;
}

pub struct GetUserUseCaseImpl {
    user_repo: Arc<dyn UserRepository>,
}

impl GetUserUseCaseImpl {
    pub fn new(user_repo: Arc<dyn UserRepository>) -> Self {
        GetUserUseCaseImpl { user_repo }
    }
}

#[async_trait]
impl GetUserUseCase for GetUserUseCaseImpl {
    async fn execute(&self, input: GetUserInput) -> Result<GetUserOutput, AppError> {
        let user = self.user_repo.find_by_id(&input.id).await?;
        Ok(GetUserOutput { user })
    }
}
